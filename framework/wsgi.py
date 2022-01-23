from framework.front_controllers import AddSlash
from framework.template_controllers import NotFoundPage


class Application:
    def __init__(self, routes):
        self.routes = routes

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        # Add slash to url
        add_slash = AddSlash()
        path = add_slash(path)
        if path in self.routes:
            controller = self.routes[path]
        else:
            controller = NotFoundPage()
        code, body = controller()
        start_response(code, [('Content-Type', 'text/html')])
        return [body]
