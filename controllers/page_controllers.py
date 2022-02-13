from framework.template_controllers import BaseController
from framework.templator import render
from framework.wsgi import Application
from logger import Logger
from models.models import Student, Category, Course, CourseChangeObserverFactory, CourseStudent, \
    MapperRegistry, UnitOfWork
from patterns.decorator import class_debug


logger_browsing = Logger('browsing')  # переход по страницам
logger_actions = Logger('actions')  # действия с данными

app = Application()


@class_debug
class PageController(BaseController):
    def __call__(self, *args, **kwargs):
        """Добавляем логирование"""
        logger_browsing.log(f'Opened {self.url}')
        return super().__call__(*args, **kwargs)

    def redirect(self, request):
        request['method'] = 'GET'
        return self.__call__(request)


@class_debug
@app.route('/')
class IndexPage(PageController):
    """
    Контроллер главной страницы
    """
    def __init__(self):
        super().__init__()
        self.url = 'index.html'


@class_debug
@app.route('/about/')
class AboutPage(PageController):
    """
    Контроллер вывода информации о сайте
    """
    def __init__(self):
        super().__init__()
        self.url = 'about.html'


@class_debug
@app.route('/contacts/')
class ContactsPage(PageController):
    """
    Контроллер вывода контактов
    """
    def __call__(self, request):
        if request['method'] == 'POST':
            self.url = 'feedback.html'
            print(f'got message from {request["data"]["email"]}: {request["data"]["msg"]}')
            logger_actions.log('Feedback was sent')
        else:
            self.url = 'contacts.html'
        logger_browsing.log(f'Opened {self.url}')
        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/categories/')
class CategoriesPage(PageController):
    """
    Контроллер вывода списка категорий
    """
    def __init__(self):
        super().__init__()
        self.url = 'categories.html'

    def __call__(self, request):
        mapper = MapperRegistry.get_mapper_by_name('Category')
        data = mapper.get_all()
        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/addcategory/')
class AddCategory(PageController):
    """
    Контроллер добавления категории
    """
    def __init__(self):
        super().__init__()
        self.url = 'new-category.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            category = Category(
                None,
                request["data"]["title"],
                request["data"]["description"]
            )
            mapper = MapperRegistry.get_mapper_by_name('Category')
            mapper.create(category)
            logger_actions.log('New category was added')
            return CategoriesPage().redirect(request)

        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/courses/')
class CoursesPage(PageController):
    """
    Контроллер вывода списка курсов
    """
    def __init__(self):
        super().__init__()
        self.url = 'courses.html'

    def __call__(self, request):
        course_mapper = MapperRegistry.get_mapper_by_name('Course')
        data = course_mapper.get_all()

        cat_mapper = MapperRegistry.get_mapper_by_name('Category')
        for course in data:
            course.cat_title = cat_mapper.get_by_id(course.id_category).title

        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/addcourse/')
class AddCourse(PageController):
    """
    Контроллер добавления курса
    """
    def __init__(self):
        super().__init__()
        self.url = 'new-course.html'

    def __call__(self, request):

        if request['method'] == 'POST':
            mapper = MapperRegistry.get_mapper_by_name('Course')
            course = Course(
                None,
                request["data"]["title"],
                request["data"]["id_category"],
                request["data"]["description"]
            )

            mapper.create(course)
            logger_actions.log(f'New course {request["data"]["title"]} was added')
            return CoursesPage().redirect(request)

        mapper = MapperRegistry.get_mapper_by_name('Category')
        data = mapper.get_all()
        body = render(self.url, object_list=self.object_list, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/courses/update/')
class UpdateCourse(PageController):
    """
    Контроллер изменения курса
    """
    def __init__(self):
        super().__init__()
        self.url = 'update-course.html'

    def __call__(self, request):
        mapper = MapperRegistry.get_mapper_by_name('Course')
        if request['method'] == 'POST':
            course = Course(
                int(request['data']['id_course']),
                request['data']['title'],
                request['data']['id_category'],
                request['data']['description'],
            )

            mapper.attach(CourseChangeObserverFactory.create_observer('sms'))
            mapper.attach(CourseChangeObserverFactory.create_observer('email'))
            mapper.update(course)
            return CoursesPage().redirect(request)

        course = mapper.get_by_id(request['id'])
        cat_mapper = MapperRegistry.get_mapper_by_name('Category')
        data = cat_mapper.get_all()
        body = render(self.url, object_list=self.object_list, course=course, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/clonecourse/')
class CloneCourse(PageController):
    """
    Контроллер клонирования курса
    """
    def __init__(self):
        super().__init__()
        self.url = 'clone-course.html'

    def __call__(self, request):
        mapper = MapperRegistry.get_mapper_by_name('Course')
        if request['method'] == 'POST':
            id_course = request["data"]["id_course"]
            original_course = mapper.get_by_id(id_course)
            cloned_course = Course.clone(original_course)
            cloned_course.title = f'CLONED_{cloned_course.title}'
            mapper.create(cloned_course)

            return CoursesPage().redirect(request)

        data = mapper.get_all()
        body = render(self.url, object_list=self.object_list, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/courses/enroll/')
class EnrollPage(PageController):
    """
    Контроллер записи на курс
    """
    def __init__(self):
        super().__init__()
        self.url = 'enroll.html'

    def __call__(self, request):
        mapper = MapperRegistry.get_mapper_by_name('CourseStudent')
        if request['method'] == 'POST':
            mapper = MapperRegistry.get_mapper_by_name('CourseStudent')
            course_student = CourseStudent(
                None,
                int(request['data']['id_course']),
                int(request['data']['id_student'])
            )
            mapper.create(course_student)

            return CoursesPage().redirect(request)

        mapper = MapperRegistry.get_mapper_by_name('Course')
        course = mapper.get_by_id(int(request['id']))
        stud_mapper = MapperRegistry.get_mapper_by_name('Student')
        students = stud_mapper.get_all()
        body = render(self.url, object_list=self.object_list, course=course, students=students, request=request)
        return self.response, body.encode()


@app.route('/students/')
class StudentsPage(PageController):
    """
    Контроллер вывода списка студентов
    """
    def __init__(self):
        super().__init__()
        self.url = 'students.html'

    def __call__(self, request):
        mapper = MapperRegistry.get_mapper_by_name('Student')
        data = mapper.get_all()
        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/addstudent/')
class AddStudent(PageController):
    """
    Контроллер добавления студента
    """
    def __call__(self, request):
        if request['method'] == 'POST':
            mapper = MapperRegistry.get_mapper_by_name('Student')
            student = Student(
                              None,
                              request['data']['firstname'],
                              request['data']['lastname'],
                              request['data']['email']
                              )
            mapper.create(student)

            logger_actions.log(f'New student {request["data"]["lastname"]} was added')
            return StudentsPage().redirect(request)

        self.url = 'new-student.html'
        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


@app.route('/courses/delete/')
class DeleteCourse(PageController):
    """
    Контроллер удаления курса
    """
    def __call__(self, request):
        try:
            UnitOfWork.new_current()
            cour_mapper = MapperRegistry.get_mapper_by_name('Course')
            cour_stud_mapper = MapperRegistry.get_mapper_by_name('CourseStudent')

            # помечаем курс на удаление
            course = cour_mapper.get_by_id(int(request['id']))
            course.mark_removed()

            # находим записи на удаление из таблицы Курсы-Студенты
            courses_students = cour_stud_mapper.get_by_key('id_course', int(request['id']))
            for item in courses_students:
                item.mark_removed()

            UnitOfWork.get_current().commit()
        except Exception as e:
            print(e.args)
        finally:
            UnitOfWork.set_current(None)

        return CoursesPage().redirect(request)
