from controllers.front_controllers import AddSlash
from framework.template_controllers import NotFoundPage


class Application:
    def __init__(self, routes, front_controllers):
        self.routes = routes
        self.front_controllers = front_controllers

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        request = {}
        # Add slash to url
        add_slash = AddSlash()
        path = add_slash(path)
        if path in self.routes:
            controller = self.routes[path]
            for front in self.front_controllers:
                front(request)
        else:
            controller = NotFoundPage()
        code, body = controller(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body]
