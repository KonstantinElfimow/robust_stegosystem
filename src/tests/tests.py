import json
from io import BytesIO
import unittest
import requests
from PIL import Image
from src import robust_hashing
from src.db.mongo_db import MongoDB
from src.utils.image_conversion import bit_planes_scaled_gray_image
from src.utils.image_metrics import complexity_metric


class TestUtils(unittest.TestCase):
    def setUp(self):
        with open('config.json', encoding='utf-8', mode='r') as file:
            params: dict = json.load(file)
        if params.get('mongo_db', None):
            self.db = MongoDB(**params['mongo_db'])

    def test_save_image(self):
        print('Тест: сохранение изображения в базу данных')
        url = 'https://img.freepik.com/free-photo/view-of-3d-adorable-cat-with-fluffy-clouds_23-2151113432.jpg'
        # Загрузка изображения по URL
        response = requests.get(url)
        hash_size = 16
        # Проверка успешности запроса
        if response.status_code == 200:
            # Чтение данных из ответа и создание объекта Image
            with Image.open(BytesIO(response.content)) as image:
                planes = bit_planes_scaled_gray_image(image)
                complexity = complexity_metric(planes)
                average_hash = robust_hashing.average_hash(image, hash_size).value
                phash = robust_hashing.phash(image, hash_size).value
                dhash = robust_hashing.dhash(image, hash_size).value
                print('Complexity: {}\nAverage hash: {}\nphash: {}\ndhash: {}'.format(complexity,
                                                                                      average_hash,
                                                                                      phash,
                                                                                      dhash))
                data = {'image_url': url,
                        'complexity': complexity,
                        'average_hash': average_hash,
                        'phash': phash,
                        'dhash': dhash}
                self.assertTrue(self.db.create(data=data, key='image_url'))
        else:
            print('Ошибка при загрузке изображения:', response.status_code)
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
