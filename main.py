from framework.wsgi import Application
from controllers.page_controllers import IndexPage, AboutPage, ContactsPage
from controllers.front_controllers import AddToken

routes = {
    '/': IndexPage(),
    '/about/': AboutPage(),
    '/contacts/': ContactsPage()
}

front_controllers = [
    AddToken()
]

application = Application(routes, front_controllers)
