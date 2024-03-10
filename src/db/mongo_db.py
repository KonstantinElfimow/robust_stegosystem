import hashlib
from typing import Any, Mapping
from pymongo import MongoClient
from pymongo.cursor import Cursor
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
        if self.client[self.collection].find_one({'_id': data['_id']}) is None:
            UserValidator(**data)
            # Если id такого документа не существует, добавить его в базу данных
            self.client[self.collection].insert_one(data)
        else:
            raise Exception(f"Объект уже существует с _id: {data.get('_id')}")

    def read_all(self) -> Cursor[Mapping[str, Any] | Any] | None:
        # Получить все данные из коллекции
        data = self.client[self.collection].find()
        return data

    def read(self, *, filt: dict) -> Cursor[Mapping[str, Any] | Any] | None:
        data = self.client[self.collection].find(filt)
        return data

    def update(self, *, filt: dict, upd: dict):
        if self.client[self.collection].find(filt) is not None:
            # Если объект существует, обновить его данные
            self.client[self.collection].update(filt, {'$set': upd})
        else:
            raise Exception(f'Объекты с заданным фильтром не найдены!')

    def delete(self, *, collection: str, filt: dict):
        if self.client[collection].find(filt) is not None:
            # Если объект существует, удалить его из базы данных
            self.client[collection].delete(filt)
        else:
            raise Exception(f'Объекты не найдены!')
