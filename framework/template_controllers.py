from framework.templator import render


class BaseController:
    """Base Page Controller"""
    def __init__(self):
        self.template_name = None
        self.object_list = []
        self.response = '200 OK'

    def __call__(self, request):
        body = render(self.template_name, object_list=self.object_list, request=request)
        return self.response, body.encode()


class NotFoundPage(BaseController):
    """Page404 Controller"""
    def __init__(self):
        super().__init__()
        self.response = '404 Not Found'
        self.template_name = 'page404.html'


class PageController(BaseController):
    def __init__(self):
        super().__init__()
        self.template_name = None
        self.model = None

    def redirect(self, request):
        request['method'] = 'GET'
        return self.__call__(request)
