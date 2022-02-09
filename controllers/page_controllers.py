from framework.template_controllers import BaseController
from framework.templator import render
from framework.wsgi import Application
from logger import Logger
from models.models import Course, Category, CourseBuilder, Student, Client, CourseStudent
from patterns.decorator import class_debug


logger_browsing = Logger('browsing')  # переход по страницам
logger_actions = Logger('actions')  # действия с данными


app = Application()
client = Client()


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
    def __init__(self):
        super().__init__()
        self.url = 'index.html'


@class_debug
@app.route('/about/')
class AboutPage(PageController):
    def __init__(self):
        super().__init__()
        self.url = 'about.html'


@class_debug
@app.route('/contacts/')
class ContactsPage(PageController):
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
    def __init__(self):
        super().__init__()
        self.url = 'categories.html'

    def __call__(self, request):
        data = Category.get_all()
        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/addcategory/')
class AddCategory(PageController):
    def __init__(self):
        super().__init__()
        self.url = 'new-category.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            category = Category(
                request["data"]["title"],
                request["data"]["short_title"],
                request["data"]["desc"]
            )
            category.save()
            logger_actions.log('New category was added')
            return CategoriesPage().redirect(request)

        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/courses/')
class CoursesPage(PageController):
    def __init__(self):
        super().__init__()
        self.url = 'courses.html'

    def __call__(self, request):
        data = Course.get_all()
        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/addcourse/')
class AddCourse(PageController):
    def __call__(self, request):
        if request['method'] == 'POST':
            course = CourseBuilder(). \
                title(request["data"]["title"]). \
                category(request["data"]["category"]). \
                description(request["data"]["desc"]). \
                build()

            course.save()
            logger_actions.log(f'New course {request["data"]["title"]} was added')
            return CoursesPage().redirect(request)

        self.url = 'new-course.html'
        data = Category.get_all()
        body = render(self.url, object_list=self.object_list, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/clonecourse/')
class CloneCourse(PageController):
    def __init__(self):
        super().__init__()
        self.url = 'clone-course.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            original_title = request["data"]["course"]
            original_dict = Course.get_by_key('title', original_title)

            original_course = CourseBuilder().\
                title(f"CLONED_{original_dict['title']}").\
                category(original_dict['category']).\
                description(original_dict['description']).\
                build()

            prototype_course = original_course.clone()
            prototype_course.save()
            logger_actions.log(f'Course {original_title} was cloned')

            return CoursesPage().redirect(request)

        data = Course.get_all()
        body = render(self.url, object_list=self.object_list, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/students/')
class StudentsPage(PageController):
    def __init__(self):
        super().__init__()
        self.url = 'students.html'

    def __call__(self, request):
        data = Student.get_all()
        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/addstudent/')
class AddStudent(PageController):
    def __call__(self, request):
        if request['method'] == 'POST':

            student = client.create_user('student',
                               request['data']['firstname'],
                               request['data']['lastname'],
                               request['data']['email']
                                         )
            student.save()
            logger_actions.log(f'New student {request["data"]["lastname"]} was added')
            return StudentsPage().redirect(request)

        self.url = 'new-student.html'
        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/courses/enroll/')
class EnrollPage(PageController):
    def __init__(self):
        super().__init__()
        self.url = 'enroll.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            course_student = CourseStudent(
                request['data']['title'],
                request['data']['student']
            )
            course_student.save()

            return CoursesPage().redirect(request)

        id = int(request['id'])
        course = Course.get_by_key('id', id)
        students = Student.get_all()
        body = render(self.url, object_list=self.object_list, course=course, students=students, request=request)
        return self.response, body.encode()
