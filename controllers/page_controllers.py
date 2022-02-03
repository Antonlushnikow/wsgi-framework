from framework.template_controllers import BaseController
from framework.templator import render
from framework.utils import Logger
from models.models import Course, CourseCategory


logger_browsing = Logger('browsing')
logger_actions = Logger('actions')


class IndexPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'index.html'


class AboutPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'about.html'


class ContactsPage(BaseController):
    def __init__(self):
        super().__init__()

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


class CategoriesPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'categories.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            category = CourseCategory(
                request["data"]["title"],
                request["data"]["short_title"],
                request["data"]["desc"]
            )
            category.save()
            logger_actions.log('New category was added')
        logger_browsing.log(f'Opened {self.url}')
        data = CourseCategory.get_all()
        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


class AddCourseCategory(BaseController):
    def __init__(self):
        super().__init__()

    def __call__(self, request):
        self.url = 'new-category.html'
        logger_browsing.log(f'Opened {self.url}')
        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


class CoursesPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'courses.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            course = Course(
                request["data"]["title"],
                request["data"]["category"],
                request["data"]["desc"]
            )
            course.save()
            logger_actions.log('New course was added')
        data = Course.get_all()
        logger_browsing.log(f'Opened {self.url}')
        body = render(self.url, data=data, request=request)
        return self.response, body.encode()


class AddCourse(BaseController):
    def __init__(self):
        super().__init__()

    def __call__(self, request):
        self.url = 'new-course.html'
        logger_browsing.log(f'Opened {self.url}')
        data = CourseCategory.get_all()
        body = render(self.url, object_list=self.object_list, data=data, request=request)
        return self.response, body.encode()
