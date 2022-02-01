import abc
import json


def load_data(filename):
    with open(filename) as f:
        return json.load(f)


def save_data(filename, json_data):
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=4)


class CRUD:
    @staticmethod
    def create(person_type: str, data: dict):
        json_data = load_data(FILES[person_type])
        json_data.append(data)
        save_data(FILES[person_type], json_data)

    @staticmethod
    def get_all(person_type: str):
        return load_data(FILES[person_type])



class Person(abc.ABC, CRUD):
    def __init__(self, firstname, lastname, info=None):
        self.firstname = firstname
        self.lastname = lastname
        self.info = info


class Student(Person):
    pass


class Teacher(Person):
    pass


class CourseCategory:
    pass


class Course:
    pass


FILES = {
    'students': 'students.json',
    'teachers': 'teachers.json',
}

Student.create('students', {'name': 'Anton', 'surname': 'Lushnikov'})
students = Student.get_all('students')
print(students)
