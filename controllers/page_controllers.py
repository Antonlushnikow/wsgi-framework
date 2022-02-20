from framework.template_controllers import PageController
from framework.templator import render
from framework.wsgi import Application as app
from logger import Logger
from models.models import Student, Category, Course, CourseChangeObserverFactory, \
    MapperRegistry, UnitOfWork
from patterns.decorator import class_debug, validate_post_data


logger_browsing = Logger('browsing')  # переход по страницам
logger_actions = Logger('actions')  # действия с данными

NO_CATEGORY_ID = 1


class ListController(PageController):
    def __call__(self, request, *args, **kwargs):
        data = self.get_queryset()
        body = render(template_name=self.template_name, data=data, request=request)
        return self.response, body.encode()

    def get_queryset(self):
        try:
            mapper = MapperRegistry.get_mapper_by_name(self.model)
            return mapper.get_all()
        except Exception as e:
            print(f'Модель не найдена - {e.args}')


@class_debug
@app.route('/')
class IndexPage(PageController):
    """
    Контроллер главной страницы
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'index.html'


@app.route('/temp/')
class TestPage(ListController):
    """
    Контроллер главной страницы
    """
    def __init__(self):
        super().__init__()
        self.model = 'Course'
        self.template_name = 'test.html'


@class_debug
@app.route('/about/')
class AboutPage(PageController):
    """
    Контроллер вывода информации о сайте
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'about.html'


@class_debug
@app.route('/contacts/')
class ContactsPage(PageController):
    """
    Контроллер вывода контактов
    """
    def __call__(self, request):
        if request['method'] == 'POST':
            self.template_name = 'feedback.html'
            print(f'got message from {request["data"]["email"]}: {request["data"]["msg"]}')
            logger_actions.log('Feedback was sent')
        else:
            self.template_name = 'contacts.html'

        body = render(self.template_name, object_list=self.object_list, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/categories/')
class CategoriesPage(ListController):
    """
    Контроллер вывода списка категорий
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'categories.html'
        self.model = 'Category'


@validate_post_data
@class_debug
@app.route('/addcategory/')
class AddCategory(PageController):
    """
    Контроллер добавления категории
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'new-category.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            if request['data']['is_validate']:
                category = Category(
                    None,
                    request['data']['title'],
                    request['data']['description']
                )
                mapper = MapperRegistry.get_mapper_by_name('Category')
                mapper.create(category)
                logger_actions.log('New category was added')
                return CategoriesPage().redirect(request)
            return ErrorHandler('is_empty', '/addcategory/').redirect(request)

        body = render(self.template_name, object_list=self.object_list, request=request)
        return self.response, body.encode()


@app.route('/categories/delete/')
class DeleteCategory(PageController):
    """
    Контроллер удаления категории
    """
    def __call__(self, request):
        try:
            UnitOfWork.new_current()
            cat_mapper = MapperRegistry.get_mapper_by_name('Category')
            cour_mapper = MapperRegistry.get_mapper_by_name('Course')

            # помечаем категорию на удаление
            category = cat_mapper.get_by_id(int(request['id']))
            category.mark_removed()

            # помечаем соответствующие курсы на смену категории на "Без категории"
            courses = cour_mapper.get_by_key('id_category', int(request['id']))
            for item in courses:
                item.id_category = NO_CATEGORY_ID
                item.mark_dirty()

            UnitOfWork.get_current().commit()
        except Exception as e:
            print(e.args)
        finally:
            UnitOfWork.set_current(None)

        return CategoriesPage().redirect(request)


@class_debug
@app.route('/courses/')
class CoursesPage(ListController):
    """
    Контроллер вывода списка курсов
    """
    def __init__(self):
        super().__init__()
        self.model = 'Course'
        self.template_name = 'courses.html'

    def get_queryset(self):
        try:
            mapper = MapperRegistry.get_mapper_by_name(self.model)
            data = mapper.get_all()
            cat_mapper = MapperRegistry.get_mapper_by_name('Category')
            for course in data:
                course.cat_title = cat_mapper.get_by_id(course.id_category).title
            return data
        except Exception as e:
            print(f'Модель не найдена - {e.args}')


@validate_post_data
@class_debug
@app.route('/addcourse/')
class AddCourse(PageController):
    """
    Контроллер добавления курса
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'new-course.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            if request['data']['is_validate']:
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
            return ErrorHandler('is_empty', '/addcourse/').redirect(request)

        mapper = MapperRegistry.get_mapper_by_name('Category')
        data = mapper.get_all()
        body = render(self.template_name, object_list=self.object_list, data=data, request=request)
        return self.response, body.encode()


@validate_post_data
@class_debug
@app.route('/courses/update/')
class UpdateCourse(PageController):
    """
    Контроллер изменения курса
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'update-course.html'

    def __call__(self, request):
        mapper = MapperRegistry.get_mapper_by_name('Course')
        if request['method'] == 'POST':
            id_course = int(request['data']['id_course'])
            if request['data']['is_validate']:
                course = Course(
                    id_course,
                    request['data']['title'],
                    request['data']['id_category'],
                    request['data']['description'],
                )

                mapper.attach(CourseChangeObserverFactory.create_observer('sms'))
                mapper.attach(CourseChangeObserverFactory.create_observer('email'))
                mapper.update(course)
                return CoursesPage().redirect(request)
            return ErrorHandler('is_empty', f'/courses/update/{id_course}').redirect(request)

        course = mapper.get_by_id(request['id'])
        cat_mapper = MapperRegistry.get_mapper_by_name('Category')
        data = cat_mapper.get_all()
        body = render(self.template_name, object_list=self.object_list, course=course, data=data, request=request)
        return self.response, body.encode()


@class_debug
@app.route('/clonecourse/')
class CloneCourse(PageController):
    """
    Контроллер клонирования курса
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'clone-course.html'

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
        body = render(self.template_name, object_list=self.object_list, data=data, request=request)
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


@class_debug
@app.route('/courses/enroll/')
class EnrollPage(PageController):
    """
    Контроллер записи на курс
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'enroll.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            mapper = MapperRegistry.get_mapper_by_name('Course')
            course = mapper.get_by_id(int(request['data']['id_course']))
            course.enroll(int(request['data']['id_student']))
            return CoursesPage().redirect(request)

        mapper = MapperRegistry.get_mapper_by_name('Course')
        course = mapper.get_by_id(int(request['id']))
        stud_mapper = MapperRegistry.get_mapper_by_name('Student')
        students = stud_mapper.get_all()
        body = render(self.template_name, object_list=self.object_list, course=course, students=students, request=request)
        return self.response, body.encode()


@app.route('/students/')
class StudentsPage(ListController):
    """
    Контроллер вывода списка студентов
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'students.html'
        self.model = 'Student'


@validate_post_data
@class_debug
@app.route('/addstudent/')
class AddStudent(PageController):
    """
    Контроллер добавления студента
    """
    def __init__(self):
        super().__init__()
        self.template_name = 'new-student.html'

    def __call__(self, request):
        if request['method'] == 'POST':
            if request['data']['is_validate']:
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
            return ErrorHandler('is_empty', '/addstudent/').redirect(request)

        body = render(self.template_name, object_list=self.object_list, request=request)
        return self.response, body.encode()


@app.route('/students/delete/')
class DeleteStudent(PageController):
    """
    Контроллер удаления студента
    """
    def __call__(self, request):
        try:
            UnitOfWork.new_current()
            stud_mapper = MapperRegistry.get_mapper_by_name('Student')
            cour_stud_mapper = MapperRegistry.get_mapper_by_name('CourseStudent')

            # помечаем студента на удаление
            student = stud_mapper.get_by_id(int(request['id']))
            student.mark_removed()

            # находим записи на удаление из таблицы Курсы-Студенты
            courses_students = cour_stud_mapper.get_by_key('id_student', int(request['id']))
            for item in courses_students:
                item.mark_removed()

            UnitOfWork.get_current().commit()
        except Exception as e:
            print(e.args)
        finally:
            UnitOfWork.set_current(None)

        return StudentsPage().redirect(request)


class ErrorHandler(PageController):
    """
    Контроллер страницы, отображающей ошибку ввода
    """
    def __init__(self, error_code, try_again_url):
        super().__init__()
        self.template_name = 'error.html'
        self.data = {
            'error_msg': ERRORS[error_code],
            'try_again_url': try_again_url
        }

    def __call__(self, request):
        body = render(self.template_name, object_list=self.object_list, data=self.data, request=request)
        return self.response, body.encode()


ERRORS = {
    'is_empty': 'Поля не могут быть пустыми',
}
