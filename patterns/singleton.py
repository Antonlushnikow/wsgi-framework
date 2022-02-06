class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class SingletonByName(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instances = {}

    def __call__(cls, *args, **kwargs):
        name = args[0]
        if name not in cls.__instances:
            cls.__instances[name] = super().__call__(*args, **kwargs)
        return cls.__instances[name]
