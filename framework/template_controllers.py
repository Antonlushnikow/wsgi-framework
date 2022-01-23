from framework.templator import render


class BaseController:
    """Base Page Controller"""
    def __init__(self):
        self.url = ''
        self.object_list = []
        self.response = '200 OK'

    def __call__(self, request):
        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


class NotFoundPage(BaseController):
    """Page404 Controller"""
    def __init__(self):
        super().__init__()
        self.response = '404 Not Found'
        self.url = 'page404.html'
