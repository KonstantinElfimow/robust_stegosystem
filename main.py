import json
import numpy as np
import io
import time
from dotenv import load_dotenv
import os
from PIL import Image

from src.db.mongo_db import MongoDB
from src.db.singleton import MongoDBSingleton
from src.fill_db import fill_db
from src.research_robust import research_robust
from src.robust_hashing import ImageHash, phash


def get_images():
    pass


def format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return '{:d} дней, {:02d}:{:02d}:{:.3f}'.format(int(days), int(hours), int(minutes), seconds)


def sender(hash_size: int, key: int):
    return True


def receiver(hash_size: int, key: int):
    message_path: str = 'resources/message_recovered.txt'

    # Храним полученные хэши
    hashes: list[int] = []

    # Декодируем сообщение
    buffer = io.StringIO()

    np.random.seed(key)
    for h in hashes:
        rand = np.random.randint(0, 2 ** hash_size)
        m = np.uint8(np.bitwise_xor(h, rand))

        m_i = str(int(m).to_bytes(1, byteorder='little', signed=False), encoding='utf-8')
        buffer.write(m_i)
    np.random.seed()

    with open(message_path, mode='w', encoding='utf-8') as file:
        file.write(buffer.getvalue())

    return True


def start_model(hash_size: int, key: int):
    df = sender(hash_size, key)
    flag = receiver(hash_size, key)


def save_collection_to_json(filepath: str):
    db = MongoDBSingleton().db
    with open(filepath, encoding='utf-8', mode='w') as file:
        json.dump(db.read_all(), file, indent=4, allow_nan=False, ensure_ascii=False)


if __name__ == '__main__':
    with open('config.json', encoding='utf-8', mode='r') as file:
        params: dict = json.load(file)

    if params.get('mongo_db', None):
        singleton = MongoDBSingleton()
        singleton.db = MongoDB(**params['mongo_db'])
    else:
        raise ValueError('Добавьте настройку connection для MongoDB в config.json!')

    if params.get('fill_db', None):
        if params['fill_db']['flag']:
            if params.get('hash_size', None):
                flag = fill_db(params['fill_db']['source_path'], params['hash_size'])
                if flag:
                    filepath = './resources/repository/image_collection.json'
                    save_collection_to_json(filepath)
            else:
                raise ValueError('Добавьте hash_size в config.json')

    if params.get('test_time', None):
        if params['test_time']:
            pass

    if params.get('research_robust', None):
        if params['research_robust']:
            research_robust()

    if params.get('start_model', None):
        if params['start_model']:
            load_dotenv()
            key: int = int(os.environ.get('KEY'))
            hash_size = params['hash_size']
            start_model(hash_size, key)
