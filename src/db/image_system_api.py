from datetime import datetime
import numpy as np
from bson import json_util
from pydantic import ValidationError
from src.db.mongo_db import MongoDB
from src.db.schema import UserValidator


class StegoSystem:
    def __init__(self, *,
                 host: str = 'localhost',
                 port: int = 27017,
                 db_name: str = 'example'):
        # Создать экземпляр класса MongoDB
        self._db = MongoDB(host=host, port=port, db_name=db_name)

    # Определить метод register_user для регистрации нового пользователя
    def add_image_to_db(self, *, data: dict) -> bool:

        # Создать словарь, содержащий данные
        data = {
            'image': data['image'],
            'registered_at': datetime.now()
        }

        # Проверить данные пользователя с помощью схемы UserValidator
        try:
            UserValidator(**data)
        except ValidationError as ex:
            print('[add_image_to_db] Ошибка валидации!')
            print(ex)
            return False

        data['_id'] = hash(data.get('image'))
        # Вызвать метод create_object класса MongoDB для вставки данных в базу данных
        return self.db.create(data=data, collection='images')

    @property
    def db(self):
        return self._db
