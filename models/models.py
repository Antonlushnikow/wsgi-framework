import abc
import json


def load_data(filename):
    with open(filename) as f:
        return json.load(f)


def save_data(filename, json_data):
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=4)


class CRUD:
    @classmethod
    def get_all(cls):
        return load_data(FILES[cls.__name__])

    @staticmethod
    def save_to_file(model, data):
        json_data = load_data(FILES[model])
        json_data.append(data)
        save_data(FILES[model], json_data)


class BaseModel(CRUD):
    def save(self):
        self.save_to_file(self.__class__.__name__, self.__dict__)


class Person(BaseModel):
    def __init__(self, firstname, lastname, info=None):
        self.firstname = firstname
        self.lastname = lastname
        self.info = info

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Student(Person):
    def __init__(self, firstname, lastname, info=None):
        super().__init__(firstname, lastname, info)
        self._type = 'students'


class Teacher(Person):
    def __init__(self, firstname, lastname, info=None):
        super().__init__(firstname, lastname, info)
        self._type = 'teachers'


class CourseCategory(BaseModel):
    def __init__(self, title):
        self.title = title


class Course:
    pass


FILES = {
    'Student': 'students.json',
    'Teacher': 'teachers.json',
    'CourseCategory': 'categories.json',
    'Course': 'courses.json',
}
