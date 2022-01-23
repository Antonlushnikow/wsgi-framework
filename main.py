from framework.wsgi import Application
from controllers import IndexPage, AboutPage

routes = {
    '/': IndexPage(),
    '/about/': AboutPage()
}

application = Application(routes)
