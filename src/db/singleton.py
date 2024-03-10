from src.db.mongo_db import MongoDB


class MongoDBSingleton(object):
    _instance = None

    def __new__(cls):
        """ Создает singleton объект, если он не создан,
          или иначе возвращает предыдущий singleton объект """
        if cls._instance is None:
            cls._instance = super(MongoDBSingleton, cls).__new__(cls)
        return cls._instance
