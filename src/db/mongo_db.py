from typing import Any, Mapping
from pymongo import MongoClient
from pymongo.cursor import Cursor


class MongoDB(object):
    def __init__(self, *, host: str, port: int, db_name: str):
        # Создать экземпляр класса MongoClient для подключения к базе данных
        self._client = MongoClient(f'mongodb://{host}:{port}')[db_name]

    @property
    def client(self):
        return self._client

    def create(self, *, collection: str, data: dict) -> bool:
        try:
            # Проверить, существует ли объект с таким же именем
            if self.client[collection].find_one({'_id': data.get('_id')}) is None:
                # Если id такого документа не существует, добавить его в базу данных
                self.client[collection].insert_one(data)
            else:
                raise Exception(f"Объект с _id: {data.get('_id')}")
        except Exception as ex:
            print('[create] Ошибка!')
            print(ex)
            return False
        else:
            print(f"[create] Новый объект _id: {data.get('_id')}")
            return True

    def read_all(self, *, collection: str) -> Cursor[Mapping[str, Any] | Any] | None:
        try:
            # Получить все данные из коллекции
            data = self.client[collection].find()
        except Exception as ex:
            print('[read_all] Ошибка!')
            print(ex)
        else:
            print('[read_all] Получили все объекты!')
            return data

    def read(self, *, collection: str, filt: dict) -> Cursor[Mapping[str, Any] | Any] | None:
        try:
            data = self.client[collection].find(filt)
        except Exception as ex:
            print('[read] Ошибка!')
            print(ex)
        else:
            print(f'[read] Получили объекты по фильтру!')
            return data

    def update(self, *, collection: str, filt: dict, upd: dict) -> bool:
        try:
            if self.client[collection].find(filt) is not None:
                # Если объект существует, обновить его данные
                self.client[collection].update(filt, {'$set': upd})
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

