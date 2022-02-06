from datetime import datetime

from patterns.singleton import SingletonByName


LOG_PATH = 'logs/'


class Logger(metaclass=SingletonByName):
    def __init__(self, name):
        self.name = f'{name}'

    def log(self, data):
        with open(f'{LOG_PATH}{self.name}', 'a+') as f:
            f.write(f'{datetime.now()} - {data}\n')
