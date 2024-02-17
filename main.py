import numpy as np
import base64
import io
import json
import time
from dotenv import load_dotenv
import os
from PIL import Image
from src.robust_hashing import ImageHash, phash

load_dotenv()

HASH_SIZE: int = 16
WINDOW_SIZE: int = 128
KEY: int = int(os.environ.get('KEY'))


def get_images():
    pass


def gamma_function(stop: int):
    return np.random.randint(0, stop)


def format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return '{:d} дней, {:02d}:{:02d}:{:.3f}'.format(int(days), int(hours), int(minutes), seconds)


def sender():
    info = io.StringIO()

    images_dir: str = 'repository/resources/sent_images'
    message_path: str = 'repository/resources/message.txt'
    info_path: str = 'encode_info.txt'

    # Начало заполнения map
    start_time = time.perf_counter()

    # Создаем словарь для сохранения перцептивных хешей и их кадров {pHash: [cutout_1, ...]}
    hashes: dict[int: list] = dict()
    # Создаём counter для отслеживания коллизий в map
    counter = 0
    # Проходимся по всем файлам в папке
    for filename in os.listdir(images_dir):
        # Открываем изображение и вычисляем перцептивный хэш
        with Image.open(os.path.join(images_dir, filename)) as image:
            arr = np.asarray(image, dtype=np.uint8)

        block_size = WINDOW_SIZE

        height, width = arr.shape[0:2]
        for i in range(0, height - block_size + 1, block_size):
            for j in range(0, width - block_size + 1, block_size):
                block = arr[i:i + block_size, j:j + block_size]

                h: ImageHash = phash(Image.fromarray(block), hash_size=HASH_SIZE)

                left = j
                upper = i
                right = left + block_size
                lower = upper + block_size
                coordinates: tuple = left, upper, right, lower

                hashes.setdefault(h.value, []).append([filename, coordinates])
                counter += 1
    # Окончание заполнения map
    end_time = time.perf_counter()
    # Примерное время заполнения map всевозможными ключами
    approximate_time = format_time(((end_time - start_time) * (2 ** HASH_SIZE)) / len(hashes))

    info.write('Примерное время заполнения всего map:\n{}\n'.format(approximate_time))
    info.write('Map заполнен на {} из {}\n'.format(len(hashes), 2 ** HASH_SIZE))
    info.write('Коллизий в map: {}\n'.format(counter - len(hashes)))
    del counter

    try:
        with open(message_path, mode='r', encoding='utf-8') as file:
            message = file.read()

        np.random.seed(KEY)

        chosen_frames = []

        for ch in message:
            gamma = gamma_function(2 ** HASH_SIZE)
            ch_ord = np.uint8(int(''.join(format(x, '08b') for x in ch.encode('utf-8')), 2))
            result = np.bitwise_xor(ch_ord, gamma)

            if hashes.get(result, None) is None:
                raise ValueError('Map не был полностью заполнен!')

            chosen_frames.append(hashes[result][0])
    except ValueError as e:
        info.write(f'Ошибка: {str(e)}')
        raise e
    else:
        info.write('Сообщение было успешно закодировано!\n')
    finally:
        with open(info_path, mode='w', encoding='utf-8') as file:
            file.write(info.getvalue())
        np.random.seed()

    # Создаем словарь для хранения и последующей передачи изображений в бинарном режиме
    filename_binary = {}
    counter = 0
    for filename_coors in chosen_frames:
        filename: str = filename_coors[0]
        coordinates: tuple = filename_coors[1]

        suffix = filename.split('.')[-1]

        with Image.open(os.path.join(images_dir, filename)) as image:
            frame = image.crop(coordinates)

        byte_stream = io.BytesIO()
        f = 'JPEG' if suffix.lower() == 'jpg' else suffix
        frame.save(byte_stream, format=f)
        byte_stream.seek(0)

        encoded_string = base64.b64encode(byte_stream.read()).decode('utf-8')
        filename_binary[f'{counter}.{suffix}'] = encoded_string
        counter += 1
    # Через REST API отправляем изображения в виде бинарника
    # requests.post(f'{request.host_url}/api/data/images', json=filename_binary, headers=headers)

    return True


def receiver():
    images_dir: str = 'repository/resources/received_images'
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    message_path: str = 'repository/resources/message_recovered.txt'

    # Храним полученные хэши
    hashes: list[int] = []

    data_json = ''  # requests.get(f'{request.host_url}/api/data/images', headers=headers).json()
    # Преобразуем json в dict
    data = json.loads(data_json)
    # декодирование строки из формата base64
    for filename, binary in data.items():
        # сохранение изображения в файл
        with open(os.path.join(images_dir, filename), mode='wb') as image_file:
            decoded_string = base64.b64decode(binary)
            image_file.write(decoded_string)

        with Image.open(os.path.join(images_dir, filename)) as image:
            h: ImageHash = phash(image, hash_size=HASH_SIZE)
            hashes.append(h.value)

    # Декодируем сообщение
    buffer = io.StringIO()

    np.random.seed(KEY)
    for h in hashes:
        gamma = gamma_function(2 ** HASH_SIZE)
        m = np.uint8(np.bitwise_xor(h, gamma))

        m_i = str(int(m).to_bytes(1, byteorder='little', signed=False), encoding='utf-8')
        buffer.write(m_i)
    np.random.seed()

    with open(message_path, mode='w', encoding='utf-8') as file:
        file.write(buffer.getvalue())

    return True


if __name__ == '__main__':
    pass
