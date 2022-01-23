class AddSlash:
    """Add slash to the end of URL if necessary"""
    def __call__(self, path):
        if path[-1] != '/':
            path = f'{path}/'
        return path
