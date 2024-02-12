from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import matplotlib.pyplot as plt
from src.robust_hashing import phash, dhash, average_hash

HASH_SIZE: int = 64
FILENAME: str = 'test.png'


def show_graphic(title: str,
                 x: list,
                 x_label: str,
                 distance_average_hash: list,
                 distance_phash: list,
                 distance_dhash: list):
    plt.plot(x, distance_average_hash, label='Average Hash', marker='o')
    plt.plot(x, distance_phash, label='pHash', marker='o')
    plt.plot(x, distance_dhash, label='dHash', marker='o')
    # добавление легенды и заголовка
    plt.legend()
    plt.title(title)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel('Расстояние Хемминга', fontsize=12)

    # включаем дополнительные отметки на осях
    plt.minorticks_on()

    plt.xlim([0., max(x) + 1])
    plt.ylim([0., HASH_SIZE])
    # включаем основную сетку
    plt.grid(which='major')
    # включаем дополнительную сетку
    plt.grid(which='minor', linestyle=':')
    plt.tight_layout()
    plt.show()


def build_graphics() -> None:
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

    show_graphic('Расстояние Хемминга при повороте изображения на заданный градус', degrees, 'Градус',
                 distance_average_hash, distance_phash, distance_dhash)

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

    show_graphic('Расстояние Хемминга при Гауссовском зашумлении изображения', radius, 'Радиус зашумления',
                 distance_average_hash, distance_phash, distance_dhash)
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

    show_graphic('Расстояние Хемминга при изменении яркости изображения', lst, '% от начальной яркости',
                 distance_average_hash, distance_phash, distance_dhash)


if __name__ == '__main__':
    build_graphics()
