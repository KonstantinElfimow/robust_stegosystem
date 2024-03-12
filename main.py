import logging
from collections import deque
import json
from typing import Callable

import numpy as np
import io
import requests
from PIL import Image
from dotenv import load_dotenv
import os
from src.robust_hashing import average_hash, dhash, phash
from src.db.mongo_db import MongoDB
from src.db.singleton import MongoDBSingleton
from src.fill_db import fill_db
from src.research_robust import research_robust
import pandas as pd
from string import ascii_letters, digits
pd.set_option('display.max_colwidth', None)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_images():
    pass


def format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return '{:d} дней, {:02d}:{:02d}:{:.3f}'.format(int(days), int(hours), int(minutes), seconds)


def is_correct_alphabet(message: str, bytes_size: int) -> bool:
    mapping: dict = {
        1: (0, 127),
        2: (128, 2047),
        3: (2048, 65535),
        4: (65536, 1114111)
    }
    alphabet: set = {chr(i) for i in range(mapping[bytes_size][0], mapping[bytes_size][1] + 1)}
    return len(set(message) - alphabet) == 0


def sender(bytes_size: int, key: int, hash_size: int, hash_method: Callable):
    repository_path = './resources/repository/images.json'
    df = pd.read_json(repository_path)

    np.random.seed(key)
    message = ''.join(list(np.random.choice(list(ascii_letters + digits), size=16, replace=True)))
    np.random.seed()

    if not is_correct_alphabet(message, bytes_size):
        raise ValueError('Сообщение составлено неверно в соответствии с принятой кодировкой!')

    filepath = './resources/communication/sent_message.txt'
    with open(filepath, mode='w', encoding='utf-8') as file:
        file.write(message)

    logger.info(f'Передатчик. Передаваемое сообщение: {message}')

    np.random.seed(key)
    rand_l = deque(np.random.randint(0, 2 ** (bytes_size * 8), size=len(message)))
    np.random.seed()

    logger.info(f'Передатчик. Сгенерированные числа: {rand_l}')

    context = []
    uint_types = {1: np.uint8, 2: np.uint16, 4: np.uint32}
    hash_type = {16: np.uint16, 64: np.uint64}
    for i, m_i in enumerate(message):
        rand = rand_l.popleft()
        series = df[f'{hash_method.__name__}'].astype(hash_type.get(hash_size)) ^ rand
        number = ord(m_i)
        index_row = np.random.choice(series[series.astype(uint_types.get(bytes_size)) == number].index.to_list(), size=1)
        context.append({'image_url': df.loc[index_row, 'image_url'].to_string(index=False), 'label': i})
    logger.info(f'Передатчик. context:\n{context}')
    logger.info('Передатчик. Передаём контекст приёмнику!')
    return context


def receiver(context: list[dict], bytes_size: int, key: int, hash_size: int, hash_method: Callable):
    logger.info('Приёмник. Получаем контекст!')
    # Организуем порядок в соответствии с меткой
    context.sort(key=lambda x: x['label'])
    # Храним полученные хэши
    hashes = []
    hash_type = {16: np.uint16, 64: np.uint64}
    for doc in context:
        url = doc['image_url']
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f'{url}: успех!')
            with Image.open(io.BytesIO(response.content)) as image:
                hash_code = hash_type[hash_size](hash_method(image, hash_size).value)
                hashes.append(hash_code)
        else:
            logger.error(f'Приёмник. {url}: неудача! HTTP status code: {response.status_code}')
    # Декодируем сообщение
    buffer = io.StringIO()

    np.random.seed(key)
    rand_l = deque(np.random.randint(0, 2 ** (bytes_size * 8), size=len(context)))
    np.random.seed()

    uint_types = {1: np.uint8, 2: np.uint16, 4: np.uint32}
    for hash_code in hashes:
        rand = rand_l.popleft()
        number = uint_types.get(bytes_size)(np.bitwise_xor(hash_code, rand))
        m_i = chr(int(number))
        buffer.write(m_i)

    filepath = './resources/communication/received_message.txt'
    message = buffer.getvalue()
    with open(filepath, mode='w', encoding='utf-8') as file:
        file.write(message)
    logger.info(f'Приёмник. Полученное сообщение: {message}')


def start_communication(bytes_size: int, key: int, hash_size: int, hash_method: Callable):
    context = sender(bytes_size, key, hash_size, hash_method)
    receiver(context, bytes_size, key, hash_size, hash_method)


def main():
    with open('config.json', encoding='utf-8', mode='r') as file:
        params: dict = json.load(file)

    if params.get('mongo_db', None):
        singleton = MongoDBSingleton()
        singleton.db = MongoDB(**params['mongo_db'])
    else:
        raise ValueError('Добавьте настройку connection для MongoDB в config.json!')

    if params.get('fill_db', None):
        if params['fill_db']['flag']:
            source = params['fill_db']['source_path']
            hash_size = params['fill_db']['hash_size']
            fill_db(source, hash_size)

    if params.get('test_time', None):
        if params['test_time']['flag']:
            pass

    if params.get('research_robust', None):
        if params['research_robust']['flag']:
            research_robust()

    if params.get('start_communication', None):
        if params['start_communication']['flag']:
            load_dotenv()
            key: int = int(os.environ.get('KEY'))

            size = params['start_communication']['encoding_size_bytes']
            hash_size = params['start_communication']['hash_size']
            hash_method = dhash
            start_communication(size, key, hash_size, hash_method)


if __name__ == '__main__':
    main()
