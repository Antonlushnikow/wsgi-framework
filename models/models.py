import abc
import sqlite3
import threading

from models.data_mapper import ClassMapper, MapperNotFoundException
from patterns.prototype import PrototypeMixin
from patterns.observer import ObservableSubject, Observer


conn = sqlite3.connect('db.sqlite', check_same_thread=False)


class UnitOfWork:
    """
    Реализация паттерна "Единица работы"
    """
    current = threading.local()

    def __init__(self):
        self.new_objects = []
        self.dirty_objects = []
        self.removed_objects = []

    def register_new(self, obj):
        """Добавить объект в новые"""
        self.new_objects.append(obj)

    def register_dirty(self, obj):
        """Добавить объект в измененные"""
        self.dirty_objects.append(obj)

    def register_removed(self, obj):
        """Добавить объект в удаляемые"""
        self.removed_objects.append(obj)

    def commit(self):
        """Произвести действия по вставке, обновлению и удалению"""
        self.insert_new()
        self.update_dirty()
        self.delete_removed()

    def insert_new(self):
        """Проходит по списку новых объектов, вызывает метод create маппера"""
        for obj_ in self.new_objects:
            MapperRegistry.get_mapper(obj_).create(obj_)

    def update_dirty(self):
        """Проходит по списку измененных объектов, вызывает метод update маппера"""
        for obj_ in self.dirty_objects:
            MapperRegistry.get_mapper(obj_).update(obj_)

    def delete_removed(self):
        """Проходит по списку удаляемых объектов, вызывает метод delete маппера"""
        for obj_ in self.removed_objects:
            MapperRegistry.get_mapper(obj_).delete(obj_)

    @staticmethod
    def new_current():
        """Создает в потоке экземпляр объекта UnitOfWork"""
        __class__.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        """Создает в потоке экземпляр объекта UnitOfWork"""
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        """Вовзращает текущий объект UnitOfWork"""
        return cls.current.unit_of_work


class DomainObject:
    """
    Абстрактный класс объектов предметной области
    """
    def mark_new(self):
        """Помечает объекты на запись в БД"""
        UnitOfWork.get_current().register_new(self)

    def mark_dirty(self):
        """Помечает объекты на обновление в БД"""
        UnitOfWork.get_current().register_dirty(self)

    def mark_removed(self):
        """Помечает объекты на удаление из БД"""
        UnitOfWork.get_current().register_removed(self)


class Person(metaclass=abc.ABCMeta):
    """
    Абстрактный класс для пользователей сайта
    """
    def __init__(self, id_person, firstname, lastname, email):
        self.id_person = id_person
        self.firstname = firstname
        self.lastname = lastname
        self.email = email


class Student(Person, DomainObject):
    """
    Класс для объектов типа "Студенты"
    """
    pass


class StudentMapper(ClassMapper):
    """
    Маппер объектов класса Student
    """
    def __init__(self, connection):
        super().__init__(connection)
        self.mapped_class = Student
        self.table_name = 'students'
        self.id_name = 'id_person'

    def create(self, person):
        """Вставить запись в таблицу"""
        query = 'INSERT into students (firstname, lastname, email) VALUES (?, ?, ?)'
        self.cursor.execute(query, (person.firstname, person.lastname, person.email))
        self.commit()

    def update(self, student):
        """Обновить запись в БД"""
        query = 'UPDATE students SET firstname=?, lastname=?, email=? WHERE id_person=?'
        self.cursor.execute(query, (student.firstname, student.lastname, student.email, student.id_student))
        self.commit()


class Category:
    """
    Класс для объектов типа "Категории"
    """
    def __init__(self, id_category, title, description):
        self.id_category = id_category
        self.title = title
        self.description = description

    def __str__(self):
        return f'{self.title}'


class CategoryMapper(ClassMapper):
    """
    Маппер объектов класса Category
    """
    def __init__(self, connection):
        super().__init__(connection)
        self.mapped_class = Category
        self.table_name = 'categories'
        self.id_name = 'id_category'

    def create(self, category):
        """Вставить запись в таблицу"""
        query = f'INSERT into categories (title, description) VALUES (?, ?)'
        self.cursor.execute(query, (category.title, category.description))
        self.commit()

    def update(self, category):
        """Обновить запись в БД"""
        query = 'UPDATE categories SET title=?, description=? WHERE id_category=?'
        self.cursor.execute(query, (category.title, category.description, category.id_category))
        self.commit()


class Course(DomainObject, PrototypeMixin):
    """
    Класс для объектов типа "Курсы"
    """
    def __init__(self, id_course, title, id_category, description):
        DomainObject.__init__(self)
        self.id_course = id_course
        self.title = title
        self.id_category = id_category
        self.description = description

    def __str__(self):
        return f'{self.title}'

    def enroll(self, id_student):
        """Записать студента на курс"""
        mapper = MapperRegistry.get_mapper_by_name('CourseStudent')

        # Проверка имеющейся записи в БД
        if not mapper.get_by_filter({'id_course': self.id_course, 'id_student': id_student}):
            cour_stud = CourseStudent(None, self.id_course, id_student)
            mapper.create(cour_stud)
        else:
            print('Запись уже существует')


class CourseMapper(ClassMapper, ObservableSubject):
    """
    Маппер объектов класса Course
    """
    def __init__(self, *args, **kwargs):
        ClassMapper.__init__(self, *args, **kwargs)
        ObservableSubject.__init__(self)
        self.mapped_class = Course
        self.table_name = 'courses'
        self.id_name = 'id_course'

    def create(self, course):
        """Вставить запись в таблицу"""
        query = 'INSERT into courses (title, id_category, description) VALUES (?, ?, ?)'
        self.cursor.execute(query, (course.title, course.id_category, course.description))
        self.commit()

    def update(self, course):
        """Обновить запись в БД. Отправить уведомление об обновлении"""
        query = 'UPDATE courses SET title=?, id_category=?, description=? WHERE id_course=?'
        self.cursor.execute(query, (course.title, course.id_category, course.description, course.id_course))
        self._subject_name = course.id_course
        self.notify()
        self.commit()


class CourseStudent(DomainObject):
    """
    Класс для объектов типа "Записи на курс"
    """
    def __init__(self, id_course_student, id_course, id_student):
        self.id_course_student = id_course_student
        self.id_course = id_course
        self.id_student = id_student


class CourseStudentMapper(ClassMapper):
    """
    Маппер класса CourseStudent
    """
    def __init__(self, connection):
        super().__init__(connection)
        self.mapped_class = CourseStudent
        self.table_name = 'courses_students'
        self.id_name = 'id_course_student'

    def create(self, cour_stud) -> None:
        query = 'INSERT into courses_students (id_course, id_student) VALUES (?, ?)'
        self.cursor.execute(query, (cour_stud.id_course, cour_stud.id_student))
        self.commit()

    def update(self, cour_stud) -> None:
        """Обновить запись в БД"""
        query = 'UPDATE courses_students SET id_course=?, id_student=? WHERE id_course_student=?'
        self.cursor.execute(query, (cour_stud.id_course, cour_stud.id_student, cour_stud.id_course_student))
        self.commit()


class MapperRegistry:
    """
    Класс для создания мапперов
    """
    mappers = {
        'Student': StudentMapper,
        'Course': CourseMapper,
        'Category': CategoryMapper,
        'CourseStudent': CourseStudentMapper
    }

    @classmethod
    def get_mapper(cls, obj_):
        """Фабричный метод, создающий маппер по объекту класса"""
        cls_name = type(obj_).__name__
        if cls_name in cls.mappers:
            return cls.mappers[cls_name](conn)
        else:
            raise MapperNotFoundException('Mapper не найден')

    @classmethod
    def get_mapper_by_name(cls, cls_name):
        """Фабричный метод, создающий маппер по имени класса"""
        if cls_name in cls.mappers:
            return cls.mappers[cls_name](conn)
        else:
            raise MapperNotFoundException('Mapper не найден')


class CourseChangeObserver(Observer, abc.ABC):
    """
    Абстрактный класс наблюдателя изменения курса
    """
    def students(self, id_course) -> list:
        """
        Вывод списка студентов, записанных на курс
        """
        cour_stud_mapper = CourseStudentMapper(conn)
        stud_mapper = StudentMapper(conn)
        courses_students = cour_stud_mapper.get_by_key('id_course', id_course)
        students = [stud_mapper.get_by_id(item.id_student) for item in courses_students]
        return students


class SmsCourseChangeObserver(CourseChangeObserver):
    """
    Наблюдатель для уведомления по SMS
    """
    def on_update(self, id_course):
        """Действие при обновлении курса"""
        course_mapper = CourseMapper(conn)
        course = course_mapper.get_by_id(id_course)
        for student in self.students(id_course):
            print(f'SMS сообщение для {student.lastname}. Курс "{course}" был изменен')


class EmailCourseChangeObserver(CourseChangeObserver):
    """
    Наблюдатель для уведомления по электронной почте
    """
    def on_update(self, id_course):
        """Действие при обновлении курса"""
        course_mapper = CourseMapper(conn)
        course = course_mapper.get_by_id(id_course)
        for student in self.students(id_course):
            print(f'Письмо на {student.email}. Курс "{course}" был изменен')


class CourseChangeObserverFactory:
    """
    Класс для создания наблюдателей
    """

    types = {
        'sms': SmsCourseChangeObserver,
        'email': EmailCourseChangeObserver
    }

    @staticmethod
    def create_observer(type_):
        """Фабричный метод, создающий нужного наблюдателя"""
        try:
            return __class__.types[type_]()
        except ValueError as e:
            print(e.args)
