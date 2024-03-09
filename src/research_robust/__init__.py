from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from src.robust_hashing import phash, dhash, average_hash
from src.research_robust.save_graphic import build_graphic

HASH_SIZE: int = 64
FILENAME: str = 'test.png'


def research_robust() -> None:
    with Image.open(FILENAME) as image:
        h_average_hash = average_hash(image, hash_size=HASH_SIZE)
        h_phash = phash(image, hash_size=HASH_SIZE)
        h_dhash = dhash(image, hash_size=HASH_SIZE)

    degrees = list(range(0, 50, 5))
    distance_average_hash = []
    distance_phash = []
    distance_dhash = []
    for d in degrees:
        with Image.open(FILENAME) as image:
            distance_average_hash.append(h_average_hash - average_hash(image.rotate(d), hash_size=HASH_SIZE))
            distance_phash.append(h_phash - phash(image.rotate(d), hash_size=HASH_SIZE))
            distance_dhash.append(h_dhash - dhash(image.rotate(d), hash_size=HASH_SIZE))

    build_graphic('Расстояние Хемминга при повороте изображения на заданный градус', degrees, 'Градус',
                  distance_average_hash, distance_phash, distance_dhash, HASH_SIZE)

    # Преобразование изображения в массив NumPy
    with Image.open(FILENAME) as image:
        image_array = np.array(image)

    # Создание гауссовского шума
    noise = np.random.normal(0, 10, image_array.shape)
    noisy_image_array = np.clip(image_array + noise, 0, 255).astype(np.uint8)

    # Преобразование массива NumPy обратно в изображение
    noisy_image = Image.fromarray(noisy_image_array)

    radius = list(range(0, 50, 5))
    distance_average_hash = []
    distance_phash = []
    distance_dhash = []
    for r in radius:
        distance_average_hash.append(h_average_hash - average_hash(noisy_image
                                                                   .filter(ImageFilter
                                                                           .GaussianBlur(radius=r)),
                                                                   hash_size=HASH_SIZE))
        distance_phash.append(h_phash - phash(noisy_image
                                              .filter(ImageFilter
                                                      .GaussianBlur(radius=r)),
                                              hash_size=HASH_SIZE))
        distance_dhash.append(h_dhash - dhash(noisy_image
                                              .filter(ImageFilter
                                                      .GaussianBlur(radius=r)),
                                              hash_size=HASH_SIZE))

    build_graphic('Расстояние Хемминга при Гауссовском зашумлении изображения', radius, 'Радиус зашумления',
                  distance_average_hash, distance_phash, distance_dhash, HASH_SIZE)
    # Изменение яркости изображения (затемнение)
    lst = list(range(0, 100, 10))
    distance_average_hash = []
    distance_phash = []
    distance_dhash = []
    for x in lst:
        with Image.open(FILENAME) as image:
            enhancer = ImageEnhance.Brightness(image).enhance(x)
        distance_average_hash.append(h_average_hash - average_hash(enhancer, hash_size=HASH_SIZE))
        distance_phash.append(h_phash - phash(enhancer, hash_size=HASH_SIZE))
        distance_dhash.append(h_dhash - dhash(enhancer, hash_size=HASH_SIZE))

    with Image.open('compressed_image.png') as compressed:
        print('Расстояние Хемминга Average hash при сравнении исходного изображения и скомпрессованного: ',
              h_average_hash - average_hash(compressed, hash_size=HASH_SIZE), '.\n Размер хэш-кода: ', HASH_SIZE)
        print('Расстояние Хемминга pHash при сравнении исходного изображения и скомпрессованного: ',
              h_phash - phash(compressed, hash_size=HASH_SIZE), '.\n Размер хэш-кода: ', HASH_SIZE)
        print('Расстояние Хемминга dHash при сравнении исходного изображения и скомпрессованного: ',
              h_dhash - dhash(compressed, hash_size=HASH_SIZE), '.\n Размер хэш-кода: ', HASH_SIZE)

    build_graphic('Расстояние Хемминга при изменении яркости изображения', lst, '% от начальной яркости',
                  distance_average_hash, distance_phash, distance_dhash, HASH_SIZE)
