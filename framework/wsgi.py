import re

from controllers.front_controllers import AddSlash
from framework.template_controllers import NotFoundPage
from framework.utils import parse_params, parse_post_data
from patterns.singleton import Singleton


class Application(metaclass=Singleton):
    def __init__(self, routes={}, front_controllers=[]):
        self.routes = {}
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

        id = re.search(r'\b\d+', path)
        new_path = re.search(r'\D+\b', path)
        path = re.search(r'\D+\b', path)[0] if new_path else '/'
        add_slash = AddSlash()
        path = add_slash(path)

        # print(self.routes)

        if path in self.routes:
            controller = self.routes[path]
            if id:
                request.update({'id': id[0]})
            for front in self.front_controllers:
                front(request)
        else:
            controller = NotFoundPage()
        code, body = controller(request)

        start_response(code, [('Content-Type', 'text/html')])
        return [body]

    def route(self, url):
        def decorator(cls):
            arg = re.search(r'\b\d+', url)
            if arg:
                self.routes[url] = cls(arg[0])
            else:
                self.routes[url] = cls()

            return cls
        return decorator

path = '/enroll/dsfsdf/'
arg = re.search(r'\b\d+', path)
new_path = re.search(r'\D+\b', path)

print(arg, new_path)
