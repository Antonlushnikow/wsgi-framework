import json
from abc import ABC

from patterns.prototype import PrototypeMixin
from patterns.observer import ObservableSubject, Observer
from patterns.decorator import class_debug

JSON_PATH = 'data'


def load_data(filename) -> list:
    filename = f'{JSON_PATH}/{filename}'
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        with open(filename, 'x') as f:
            f.write('[]')
        return []


def save_data(filename, json_data):
    filename = f'{JSON_PATH}/{filename}'

    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=4)


class CRUD:
    @classmethod
    def get_all(cls):
        """
        Возвращает все данные из JSON
        """
        return load_data(FILES[cls.__name__])

    @classmethod
    def get_by_key(cls, key, value) -> list:
        """
        Возвращает данные из JSON по конкретному значению
        или пустой словарь
        """
        data = load_data(FILES[cls.__name__])
        rows = []
        for row in data:
            if row[key] == value:
                rows.append(row)
        return rows

    @classmethod
    def get_id(cls) -> int:
        return len(cls.get_all()) + 1

    @staticmethod
    def save_to_file(model, data: dict) -> None:
        """
        Добавляет данные в JSON
        """
        json_data = load_data(FILES[model])
        json_data.append(data)
        save_data(FILES[model], json_data)


class BaseModel(CRUD):
    _objects = []
    def __init__(self, id=None):
        self.id = id

    def save(self):
        """
        Сохраняет словарь аттрибутов объекта в файл
        """
        if not self.id:
            self.id = self.__class__.get_id()
        dict_to_save = {}

        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            dict_to_save[key] = value

        self.save_to_file(self.__class__.__name__, dict_to_save)

    @classmethod
    def create_object_by_id(cls, id):
        dict_ = cls.get_by_key('id', id)[0]
        obj = cls(**dict_)
        obj.id = id
        return obj

    @classmethod
    def delete_by_id(cls, id: int):
        json_data = cls.get_all()
        new_json_data = []
        for item in json_data:
            if item['id'] == id:
                continue
            new_json_data.append(item)
        save_data(FILES[cls.__name__], new_json_data)


    @classmethod
    def create_objects(cls):
        """
        Создает объекты класса по данным JSON
        """
        json_data = cls.get_all()
        for dict_ in json_data:
            cls._objects.append(cls(**dict_))

    @classmethod
    def get_all_objects(cls):
        cls._objects = []
        cls.create_objects()
        return cls._objects

    @classmethod
    def get_objects_by_key(cls, key, value) -> list:
        cls._objects = []
        json_data = cls.get_by_key(key, value)
        for dict_ in json_data:
            cls._objects.append(cls(**dict_))
        return cls._objects

    @classmethod
    def update_object(cls, id, **dict_):
        cls.delete_by_id(id)
        obj = cls(**dict_)
        obj.id = id
        obj.save()


class Person(BaseModel):
    def __init__(self, firstname, lastname, email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lastname = lastname
        self.firstname = firstname
        self.email = email

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Student(Person):
    pass


class Teacher(Person):
    pass


class PersonFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    @classmethod
    def create(cls, type_, *args):
        return cls.types[type_](*args)


class Client:
    @staticmethod
    def create_user(type_, *args):
        return PersonFactory.create(type_, *args)


class Category(BaseModel):
    def __init__(self, title, short_title, description, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.short_title = short_title
        self.description = description

    def __str__(self):
        return f'{self.title}'


class Course(BaseModel, PrototypeMixin, ObservableSubject):
    def __init__(self, title, category, description, *args, **kwargs):
        BaseModel.__init__(self, *args, **kwargs)
        ObservableSubject.__init__(self)
        # self._observer = ObservedSubject()
        self.title = title
        self.category = category
        self.description = description

    def __str__(self):
        return f'{self.title}'

    def update_object(self, id):
        Course.delete_by_id(id)
        self.id = id
        self.save()
        self._subject_name = self.id
        self.notify()


# class CourseBuilder:
#     def __init__(self):
#         self.course = Course()
#
#     def title(self, title):
#         self.course.title = title
#         return self
#
#     def category(self, category):
#         self.course.category = category
#         return self
#
#     def description(self, description):
#         self.course.description = description
#         return self
#
#     def build(self):
#         return self.course


class CourseStudent(BaseModel):
    def __init__(self, course_id, student_id, *args, ** kwargs):
        super().__init__(*args, **kwargs)
        self.course_id = course_id
        self.student_id = student_id


class CourseChangeObserver(Observer, ABC):
    def __init__(self):
        super().__init__()

    def students(self, course_id) -> list:
        course_students = CourseStudent.get_objects_by_key('course_id', course_id)
        students = [Student.create_object_by_id(item.student_id) for item in course_students]
        return students


class SmsCourseChangeObserver(CourseChangeObserver):
    def on_update(self, course_id):
        course = Course.get_by_key('id', course_id)[0]['title']
        for student in self.students(course_id):
            print(f'SMS сообщение для {student.lastname}. Курс "{course}" был изменен')


class EmailCourseChangeObserver(CourseChangeObserver):
    def on_update(self, course_id):
        course = Course.get_by_key('id', course_id)[0]['title']
        for student in self.students(course_id):
            print(f'Письмо на {student.email}. Курс "{course}" был изменен')


class CourseChangeObserverFactory:
    types = {
        'sms': SmsCourseChangeObserver,
        'email': EmailCourseChangeObserver
    }

    @staticmethod
    def create_observer(type_):
        try:
            return __class__.types[type_]()
        except:
            raise ValueError


FILES = {
    'Student': 'students.json',
    'Teacher': 'teachers.json',
    'Category': 'categories.json',
    'Course': 'courses.json',
    'CourseStudent': 'course_student.json',
}
