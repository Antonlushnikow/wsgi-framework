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
