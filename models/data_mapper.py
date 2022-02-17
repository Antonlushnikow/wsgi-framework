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
        self.mapped_class = None
        self.table_name = None
        self.id_name = None

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        pass

    def get_by_id(self, id_category: int):
        """Получить объект класса по идентификатору"""
        query = f'SELECT * FROM {self.table_name} WHERE {self.id_name}=?'
        self.cursor.execute(query, (id_category,))
        result = self.cursor.fetchone()

        if result:
            return self.mapped_class(*result)
        else:
            raise RecordNotFoundException('Запись не найдена в базе данных')

    def get_by_key(self, key, value) -> list:
        """Получить список объектов по значению ключа"""
        query = f'SELECT * FROM {self.table_name} WHERE {key}={value}'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(self.mapped_class(*item))
            return rows
        return []

    def get_by_filter(self, filter_: dict) -> list:
        """Получение списка объектов из БД, соответствующих фильтру {key: value, ...} """
        query_string = ' AND '.join([f'{key}={value}' for key, value in filter_.items()])
        query = f'SELECT * FROM {self.table_name} WHERE {query_string}'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(self.mapped_class(*item))
            return rows
        return []

    def get_all(self):
        """Получение списка объектов, соответствующих всем записям таблицы"""
        query = f'SELECT * FROM {self.table_name}'
        result = self.cursor.execute(query)

        rows = []
        if result:
            for item in result:
                rows.append(self.mapped_class(*item))
            return rows
        return []

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        pass

    def delete(self, obj_):
        """Удалить запись из БД"""
        query = f'DELETE from {self.table_name} WHERE {self.id_name}=?'
        id_ = getattr(obj_, self.id_name)
        self.cursor.execute(query, (id_, ))
        self.commit()

    def commit(self):
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)
