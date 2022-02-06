from controllers.front_controllers import AddSlash
from framework.template_controllers import NotFoundPage
from framework.utils import parse_params, parse_post_data


class Application:
    def __init__(self, routes, front_controllers):
        self.routes = routes
        self.front_controllers = front_controllers

    def __call__(self, environ, start_response):
        request = {}
        data = {}

        method = environ['REQUEST_METHOD']
        if method == 'GET':
            data = parse_params(environ['QUERY_STRING'])
        elif method == 'POST':
            data = parse_post_data(environ)

        request['method'] = method
        request['data'] = data

        # Add slash to url
        path = environ['PATH_INFO']
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
