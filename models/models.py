import abc
import sqlite3
import threading

from models.data_mapper import RecordNotFoundException, DbCommitException, ClassMapper, MapperNotFoundException

from patterns.prototype import PrototypeMixin
from patterns.observer import ObservableSubject, Observer


conn = sqlite3.connect('db.sqlite')


class UnitOfWork:
    current = threading.local()

    def __init__(self):
        self.new_objects = []
        self.dirty_objects = []
        self.removed_objects = []

    def register_new(self, obj):
        self.new_objects.append(obj)

    def register_dirty(self, obj):
        self.dirty_objects.append(obj)

    def register_removed(self, obj):
        self.removed_objects.append(obj)

    def commit(self):
        self.insert_new()
        self.update_dirty()
        self.delete_removed()

    def insert_new(self):
        for obj_ in self.new_objects:
            MapperRegistry.get_mapper(obj_).create(obj_)

    def update_dirty(self):
        for obj_ in self.dirty_objects:
            MapperRegistry.get_mapper(obj_).update(obj_)

    def delete_removed(self):
        for obj_ in self.removed_objects:
            MapperRegistry.get_mapper(obj_).delete(obj_)

    @staticmethod
    def new_current():
        __class__.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        return cls.current.unit_of_work


class DomainObject:
    def mark_new(self):
        UnitOfWork.get_current().register_new(self)

    def mark_dirty(self):
        UnitOfWork.get_current().register_dirty(self)

    def mark_removed(self):
        UnitOfWork.get_current().register_removed(self)


class Person(metaclass=abc.ABCMeta):
    def __init__(self, id_person, firstname, lastname, email):
        self.id_person = id_person
        self.firstname = firstname
        self.lastname = lastname
        self.email = email


class Student(Person, DomainObject):
    pass


class StudentMapper(ClassMapper):
    def create(self, person):
        query = 'INSERT into students (firstname, lastname, email) VALUES (?, ?, ?)'
        self.cursor.execute(query, (person.firstname, person.lastname, person.email))
        self.commit()

    def get_by_id(self, id_person: int,):
        query = 'SELECT id_person, firstname, lastname, email FROM students WHERE id_person=?'
        self.cursor.execute(query, (id_person,))
        result = self.cursor.fetchone()

        if result:
            return Student(*result)
        else:
            raise RecordNotFoundException('Запись не найдена в базе данных')

    def get_all(self) -> list:
        query = 'SELECT id_person, firstname, lastname, email FROM students'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(Student(*item))
            return rows
        return []

    def update(self, student):
        query = 'UPDATE students SET firstname=?, lastname=?, email=? WHERE id_person=?'
        self.cursor.execute(query, (student.firstname, student.lastname, student.email, student.id_student))
        self.commit()

    def delete(self, student):
        query = f'DELETE from students WHERE id_person=?'
        self.cursor.execute(query, (student.id_student, ))
        self.commit()


class Category:
    def __init__(self, id_category, title, description):
        self.id_category = id_category
        self.title = title
        self.description = description

    def __str__(self):
        return f'{self.title}'


class CategoryMapper(ClassMapper):
    def create(self, category):
        query = f'INSERT into categories (title, description) VALUES (?, ?)'
        self.cursor.execute(query, (category.title, category.description))
        self.commit()

    def get_by_id(self, id_category: int):
        query = f'SELECT id_category, title, description FROM categories WHERE id_category=?'
        self.cursor.execute(query, (id_category,))
        result = self.cursor.fetchone()

        if result:
            return Category(*result)
        else:
            raise RecordNotFoundException('Запись не найдена в базе данных')

    def get_all(self) -> list:
        query = f'SELECT id_category, title, description FROM categories'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(Category(*item))
            return rows
        return []

    def update(self, category):
        query = f'UPDATE categories SET title=?, description=? WHERE id_category=?'
        self.cursor.execute(query, (category.title, category.description, category.id_category))
        self.commit()

    def delete(self, id_category):
        query = f'DELETE from categories WHERE id_category=?'
        self.cursor.execute(query, id_category)
        self.commit()


class Course(DomainObject, PrototypeMixin):
    def __init__(self, id_course, title, id_category, description):
        DomainObject.__init__(self)
        self.id_course = id_course
        self.title = title
        self.id_category = id_category
        self.description = description

    def __str__(self):
        return f'{self.title}'


class CourseMapper(ClassMapper, ObservableSubject):
    def __init__(self, *args, **kwargs):
        ClassMapper.__init__(self, *args, **kwargs)
        ObservableSubject.__init__(self)

    def create(self, course):
        query = 'INSERT into courses (title, id_category, description) VALUES (?, ?, ?)'
        self.cursor.execute(query, (course.title, course.id_category, course.description))
        self.commit()

    def get_by_id(self, id_course: int):
        query = 'SELECT id_course, title, id_category, description FROM courses WHERE id_course=?'
        self.cursor.execute(query, (id_course,))
        result = self.cursor.fetchone()

        if result:
            return Course(*result)
        else:
            raise RecordNotFoundException('Запись не найдена в базе данных')

    def get_all(self) -> list:
        query = 'SELECT id_course, title, id_category, description FROM courses'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(Course(*item))
        return rows

    def update(self, course):
        query = 'UPDATE courses SET title=?, id_category=?, description=? WHERE id_course=?'
        self.cursor.execute(query, (course.title, course.id_category, course.description, course.id_course))
        self._subject_name = course.id_course
        self.notify()
        self.commit()

    def delete(self, course):
        query = 'DELETE from courses WHERE id_course=?'
        self.cursor.execute(query, (course.id_course, ))
        self.commit()


class CourseStudent(DomainObject):
    def __init__(self, id_course_student, id_course, id_student):
        self.id_course_student = id_course_student
        self.id_course = id_course
        self.id_student = id_student


class CourseStudentMapper(ClassMapper):
    def create(self, cour_stud) -> None:
        query = 'INSERT into courses_students (id_course, id_student) VALUES (?, ?)'
        self.cursor.execute(query, (cour_stud.id_course, cour_stud.id_student))
        self.commit()

    def get_by_id(self, id_course_student: int):
        query = 'SELECT id_course_student, id_course, id_student FROM courses_students WHERE id_course_student=?'
        self.cursor.execute(query, (id_course_student,))
        result = self.cursor.fetchone()

        if result:
            return CourseStudent(*result)
        else:
            raise RecordNotFoundException('Запись не найдена в базе данных')

    def get_by_key(self, key, value) -> list:
        query = f'SELECT id_course_student, id_course, id_student FROM courses_students WHERE {key}={value}'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(CourseStudent(*item))
            return rows
        return []

    def get_all(self) -> list:
        query = 'SELECT id_course_student, id_course, id_student FROM courses_students'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(CourseStudent(*item))
            return rows
        return []

    def update(self, cour_stud):
        query = 'UPDATE courses_students SET id_course=?, id_student=? WHERE id_course_student=?'
        self.cursor.execute(query, (cour_stud.id_course, cour_stud.id_student, cour_stud.id_course_student))
        self.commit()

    def delete(self, cour_stud):
        query = f'DELETE from courses_students WHERE id_course_student=?'
        self.cursor.execute(query, (cour_stud.id_course_student, ))
        self.commit()


class MapperRegistry:
    mappers = {
        'Student': StudentMapper,
        'Course': CourseMapper,
        'Category': CategoryMapper,
        'CourseStudent': CourseStudentMapper
    }

    @classmethod
    def get_mapper(cls, obj_):
        cls_name = type(obj_).__name__
        if cls_name in cls.mappers:
            return cls.mappers[cls_name](conn)
        else:
            raise MapperNotFoundException('Mapper не найден')

    @classmethod
    def get_mapper_by_name(cls, cls_name):
        if cls_name in cls.mappers:
            return cls.mappers[cls_name](conn)
        else:
            raise MapperNotFoundException('Mapper не найден')


class CourseChangeObserver(Observer, abc.ABC):
    def students(self, id_course) -> list:
        cour_stud_mapper = CourseStudentMapper(conn)
        stud_mapper = StudentMapper(conn)
        courses_students = cour_stud_mapper.get_by_key('id_course', id_course)
        students = [stud_mapper.get_by_id(item.id_student) for item in courses_students]
        return students


class SmsCourseChangeObserver(CourseChangeObserver):
    def on_update(self, id_course):
        course_mapper = CourseMapper(conn)
        course = course_mapper.get_by_id(id_course)
        for student in self.students(id_course):
            print(f'SMS сообщение для {student.lastname}. Курс "{course}" был изменен')


class EmailCourseChangeObserver(CourseChangeObserver):
    def on_update(self, id_course):
        course_mapper = CourseMapper(conn)
        course = course_mapper.get_by_id(id_course)
        for student in self.students(id_course):
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
