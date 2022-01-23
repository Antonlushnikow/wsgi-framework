import random
import string


class AddSlash:
    """Add slash to the end of URL if necessary"""
    def __call__(self, path):
        if path[-1] != '/':
            path = f'{path}/'
        return path


class AddToken:
    """Add Token to Request"""
    def __call__(self, request):
        token = ''.join(random.choice(string.ascii_letters) for _ in range(32))
        request['token'] = token
