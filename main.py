from framework.wsgi import Application
from controllers.page_controllers import IndexPage, AboutPage, ContactsPage, CategoriesPage, AddCategory, \
    CoursesPage, AddCourse, CloneCourse
from controllers.front_controllers import AddToken

routes = {
    '/': IndexPage(),
    '/about/': AboutPage(),
    '/contacts/': ContactsPage(),
    '/categories/': CategoriesPage(),
    '/addcategory/': AddCategory(),
    '/courses/': CoursesPage(),
    '/addcourse/': AddCourse(),
    '/clonecourse/': CloneCourse()
}

front_controllers = [
    AddToken()
]

application = Application(routes, front_controllers)
