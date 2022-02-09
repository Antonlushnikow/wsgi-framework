import json
from patterns.prototype import PrototypeMixin


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
    last_id = len(load_data(filename))
    print(f'{last_id} - last_id')

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
    def get_by_key(cls, key, value):
        """
        Возвращает данные из JSON по конкретному значению
        или пустой словарь
        """
        data = load_data(FILES[cls.__name__])
        for row in data:
            if row[key] == value:
                return row
        return {}

    @classmethod
    def get_id(cls) -> int:
        return len(cls.get_all()) + 1


    @staticmethod
    def save_to_file(model, data):
        """
        Добавляет данные в JSON
        """
        json_data = load_data(FILES[model])
        json_data.append(data)
        save_data(FILES[model], json_data)


class BaseModel(CRUD):
    def save(self):
        """
        Сохраняет словарь аттрибутов объекта в файл
        """
        new_item_dict = {'id': self.__class__.get_id()}
        new_item_dict.update(self.__dict__)
        self.save_to_file(self.__class__.__name__, new_item_dict)


class Person(BaseModel):
    def __init__(self, firstname, lastname, email):
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
    def __init__(self, title, short_title, description):
        self.title = title
        self.short_title = short_title
        self.description = description

    def __str__(self):
        return f'{self.title}'


class Course(BaseModel, PrototypeMixin):
    def __str__(self):
        return f'{self.title}'


class CourseBuilder:
    def __init__(self):
        self.course = Course()

    def title(self, title):
        self.course.title = title
        return self

    def category(self, category):
        self.course.category = category
        return self

    def description(self, description):
        self.course.description = description
        return self

    def build(self):
        return self.course


class CourseStudent(BaseModel):
    def __init__(self, course_id, student_id):
        self.course_id = course_id
        self.student_id = student_id


FILES = {
    'Student': 'students.json',
    'Teacher': 'teachers.json',
    'Category': 'categories.json',
    'Course': 'courses.json',
    'CourseStudent': 'course_student.json',
}
