from framework.wsgi import Application
from controllers.page_controllers import IndexPage, AboutPage, ContactsPage, CategoriesPage, AddCourseCategory, \
    CoursesPage, AddCourse
from controllers.front_controllers import AddToken

routes = {
    '/': IndexPage(),
    '/about/': AboutPage(),
    '/contacts/': ContactsPage(),
    '/categories/': CategoriesPage(),
    '/addcategory/': AddCourseCategory(),
    '/courses/': CoursesPage(),
    '/addcourse/': AddCourse()
}

front_controllers = [
    AddToken()
]

application = Application(routes, front_controllers)
