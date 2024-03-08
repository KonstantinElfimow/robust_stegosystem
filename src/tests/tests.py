import math
from io import BytesIO
import numpy as np
import unittest
import requests
from PIL import Image
from src import robust_hashing
from src.db.image_system_api import ImageSystem
from src.utils.image_conversion import bit_planes
from src.utils.image_metrics import complexity_metric, modified_complexity_metric


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.db = ImageSystem()
        self.matrix = np.random.randint(0, 256, (2, 2, 3)).astype(np.uint8)
        self.bit_matrix = np.random.randint(0, 2, (8, 3, 3))

    def test_complexity_metric(self):
        print('bit planes:\n', self.bit_matrix)
        print('Bit plane complexity:\n', modified_complexity_metric(self.bit_matrix))

    def test_save_image(self):
        print('Тест: сохранение изображения в базу данных')
        url = 'https://img.freepik.com/free-photo/view-of-3d-adorable-cat-with-fluffy-clouds_23-2151113432.jpg'
        # Загрузка изображения по URL
        response = requests.get(url)
        hash_size = 16
        ANTIALIAS = Image.Resampling.LANCZOS
        # Проверка успешности запроса
        if response.status_code == 200:
            # Чтение данных из ответа и создание объекта Image
            with Image.open(BytesIO(response.content)) as image:
                temp = image.convert('L').resize((int(math.sqrt(hash_size)), int(math.sqrt(hash_size))), ANTIALIAS)
                pixels = np.asarray(temp, dtype=np.uint8)
                planes = bit_planes(pixels)
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
                self.assertTrue(self.db.add_image_to_db(data=data))
        else:
            print('Ошибка при загрузке изображения:', response.status_code)
            self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
