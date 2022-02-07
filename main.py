from framework.wsgi import Application
from controllers.page_controllers import *
from controllers.front_controllers import AddToken


front_controllers = [
    AddToken()
]

application = Application(front_controllers)
