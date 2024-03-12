import hashlib
from pymongo import MongoClient
from src.db.schema import UserValidator


class MongoDB(object):
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 27017,
                 db_name: str = 'example',
                 collection: str = 'images'):
        # Создать экземпляр класса MongoClient для подключения к базе данных
        self._client = MongoClient(f'mongodb://{host}:{port}')[db_name]
        self._collection = collection

    @property
    def client(self):
        return self._client

    @property
    def collection(self):
        return self._collection

    def create(self, *, data: dict, key: str):
        data['_id'] = hashlib.sha256(data[key].encode('utf-8')).hexdigest()
        # Проверить, существует ли объект с таким же ключом
        UserValidator(**data)
        try:
            self.client[self.collection].insert_one(data)
        except:
            raise Exception(f"Объект уже существует с _id: {data.get('_id')}")

    def read_all(self) -> list[dict] | None:
        # Получить все данные из коллекции
        data = self.client[self.collection].find()
        # Преобразовать результаты запроса в список словарей
        result = [doc for doc in data]
        return result

    def read(self, *, filt: dict) -> list[dict] | None:
        try:
            data = self.client[self.collection].find(filt)
            result = [doc for doc in data]
        except:
            raise Exception(f'Объекты с фильтром ({filt}) не найдены!')
        return result

    def update(self, *, filt: dict, upd: dict):
        try:
            self.client[self.collection].update(filt, {'$set': upd})
        except:
            raise Exception(f'Объекты с фильтром ({filt}) не найдены!')

    def delete(self, *, collection: str, filt: dict):
        try:
            # Если объект существует, удалить его из базы данных
            self.client[collection].delete(filt)
        except:
            raise Exception(f'Объекты не найдены!')
