import hashlib
from typing import Any, Mapping
from pydantic import ValidationError
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

    def create(self, *, data: dict, key: str) -> bool:
        try:
            data['_id'] = hashlib.sha256(data[key].encode('utf-8')).hexdigest()
            # Проверить, существует ли объект с таким же ключом
            if self.client[self.collection].find_one({'_id': data['_id']}) is None:
                try:
                    UserValidator(**data)
                except ValidationError as ex:
                    print(ex)
                    return False
                # Если id такого документа не существует, добавить его в базу данных
                self.client[self.collection].insert_one(data)
            else:
                raise Exception(f"Объект уже существует с _id: {data.get('_id')}")
        except Exception as ex:
            print('[create] Ошибка!')
            print(ex)
            return False
        else:
            print(f"[create] Новый объект _id: {data.get('_id')}")
            return True

    def read_all(self) -> Cursor[Mapping[str, Any] | Any] | None:
        try:
            # Получить все данные из коллекции
            data = self.client[self.collection].find()
        except Exception as ex:
            print('[read_all] Ошибка!')
            print(ex)
        else:
            print('[read_all] Получили все объекты!')
            return data

    def read(self, *, filt: dict) -> Cursor[Mapping[str, Any] | Any] | None:
        try:
            data = self.client[self.collection].find(filt)
        except Exception as ex:
            print('[read] Ошибка!')
            print(ex)
        else:
            print(f'[read] Получили объекты по фильтру!')
            return data

    def update(self, *, filt: dict, upd: dict) -> bool:
        try:
            if self.client[self.collection].find(filt) is not None:
                # Если объект существует, обновить его данные
                self.client[self.collection].update(filt, {'$set': upd})
            else:
                raise Exception(f'Объекты с заданным фильтром не найдены!')
        except Exception as ex:
            print('[update] Ошибка!')
            print(ex)
            return False
        else:
            print(f'[update] Объекты с заданным фильтром обновлён!')
            return True

    def delete(self, *, collection: str, filt: dict):
        try:
            # Проверить, существует ли объект с заданным фильтром
            if self.client[collection].find(filt) is not None:
                # Если объект существует, удалить его из базы данных
                self.client[collection].delete(filt)
            else:
                raise Exception(f'Объекты не найдены!')
        except Exception as ex:
            print('[delete] Ошибка!')
            print(ex)
            return False
        else:
            print(f'[delete] Объекты удалены!')

