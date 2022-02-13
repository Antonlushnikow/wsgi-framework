import abc


class RecordNotFoundException(Exception):
    def __init__(self, args):
        super().__init__(f'Запись не найдена: {args}')


class DbCommitException(Exception):
    def __init__(self, args):
        super().__init__(f'Неудачная попытка записи: {args}')


class MapperNotFoundException(Exception):
    def __init__(self, args):
        super().__init__(f'Mapper не найден: {args}')


class ClassMapper(metaclass=abc.ABCMeta):
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_by_id(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_all(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        pass

    def commit(self):
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)
