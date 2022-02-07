import datetime


def func_debug(func, cls=None):
    def wrapper(*args, **kwargs):
        class_name = cls.__name__ if cls else 'None'
        print(f'{datetime.datetime.now()} - Запуск метода {func.__name__}'
              f' класса {class_name}')
        return func(*args, **kwargs)
    return wrapper


def class_debug(cls):
    cls.__call__ = func_debug(cls.__call__, cls)
    for item in dir(cls):
        if item.startswith('__'):
            continue
        attr = getattr(cls, item)
        if hasattr(attr, '__call__'):
            dec_method = func_debug(attr, cls)
            setattr(cls, item, dec_method)
    return cls
