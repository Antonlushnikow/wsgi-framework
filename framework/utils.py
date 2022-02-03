import datetime
import json

from urllib.parse import unquote, unquote_plus


def parse_params(string: str):
    """Parse param=value&... string"""
    res = {}
    if string:
        pairs = string.split('&')
        for item in pairs:
            key, value = item.split('=')
            res[key] = value
    return res


def parse_post_data(environ):
    """Parse POST data"""
    data = environ['wsgi.input']
    length = environ['CONTENT_LENGTH']
    if data:
        length = int(length) if length else 0
        data = data.read(length).decode('utf-8')
        data = unquote(data)
        data = unquote_plus(data)
        return parse_params(data)
    return {}


class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


LOG_PATH = 'logs/'


class Logger(metaclass=Singleton):
    def __init__(self, filename):
        self.name = f'{LOG_PATH}{filename}'

    def log(self, data):
        with open(self.name, 'a+') as f:
            f.write(f'{datetime.datetime.now()} - {data}\n')
