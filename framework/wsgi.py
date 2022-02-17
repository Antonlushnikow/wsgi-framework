import re

from controllers.front_controllers import AddSlash
from framework.template_controllers import NotFoundPage
from framework.utils import parse_params, parse_post_data
from patterns.singleton import Singleton


class Application:
    routes = {}

    def __init__(self, front_controllers=[]):
        self.front_controllers = front_controllers

    def __call__(self, environ, start_response):
        request = {}
        data = {}

        # self.start_response = start_response
        # self.environ = environ
        print(environ)
        method = environ['REQUEST_METHOD']
        if method == 'GET':
            data = parse_params(environ['QUERY_STRING'])
        elif method == 'POST':
            data = parse_post_data(environ)

        request['method'] = method
        request['data'] = data

        # Add slash to url
        path = environ['PATH_INFO']

        id_ = re.search(r'\b\d+', path)
        new_path = re.search(r'\D+\b', path)
        path = re.search(r'\D+\b', path)[0] if new_path else '/'
        add_slash = AddSlash()
        path = add_slash(path)

        # print(self.routes)

        if path in __class__.routes:
            controller = __class__.routes[path]
            if id_:
                request.update({'id': id_[0]})
            for front in self.front_controllers:
                front(request)
        else:
            controller = NotFoundPage()
        code, body = controller(request)

        start_response(code, [('Content-Type', 'text/html')])
        return [body]

    @classmethod
    def route(cls, url):
        def decorator(cls_):
            arg = re.search(r'\b\d+', url)
            if arg:
                cls.routes[url] = cls_(arg[0])
            else:
                cls.routes[url] = cls_()

            return cls_
        return decorator
