from framework.template_controllers import BaseController
from framework.templator import render


class IndexPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'index.html'


class AboutPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'about.html'


class ContactsPage(BaseController):
    def __init__(self):
        super().__init__()

    def __call__(self, request):
        if request['method'] == 'POST':
            self.url = 'feedback.html'
            print(f'got message from {request["data"]["email"]}: {request["data"]["msg"]}')
        else:
            self.url = 'contacts.html'

        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()


class AddCourseCategory(BaseController):
    def __init__(self):
        super().__init__()

    def __call__(self, request):
        if request['method'] == 'POST':
            self.url = 'categories.html'
            print(f'got message from {request["data"]["email"]}: {request["data"]["msg"]}')
        else:
            self.url = 'new-category.html'

        body = render(self.url, object_list=self.object_list, request=request)
        return self.response, body.encode()
