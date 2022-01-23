from framework.template_controllers import BaseController


class IndexPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'index.html'


class AboutPage(BaseController):
    def __init__(self):
        super().__init__()
        self.url = 'about.html'
        self.object_list = [{'name': 'Leo'}, {'name': 'Kate'}]
