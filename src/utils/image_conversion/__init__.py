import numpy as np
from PIL import Image
from src.utils.math_module import pca

""" Библиотека по различным преобразованиям изображения """


def compress_with_pca(image: Image.Image, n_components: int) -> Image.Image:
    # Преобразуем в оттенки серого
    img = np.asarray(image.convert('L'), dtype=np.uint8).copy()

    height, width = img.shape[0: 2]

    # Разбиение на блоки размером 8x8
    blocks = []
    for i in range(0, height - 7, 8):
        for j in range(0, width - 7, 8):
            block = img[i: i + 8, j: j + 8]
            blocks.append(block)
    vectors = np.asarray(blocks, dtype=np.uint8).reshape(-1, 64)
    del blocks

    new_vectors = pca(vectors, n_components)
    new_vectors = new_vectors.reshape(-1, 8, 8)

    # Восстановленное изображение
    reconstruction = np.zeros(img.shape, dtype=np.uint8)
    count = 0
    for i in range(0, height - 7, 8):
        for j in range(0, width - 7, 8):
            reconstruction[i: i + 8, j: j + 8] = new_vectors[count, :, :]
            count += 1
    reconstructed_image = Image.fromarray(reconstruction)
    return reconstructed_image


def bit_planes_scaled_gray_image(image: Image) -> np.array:
    """
    Функция преобразовывает изображение в оттенки серого и масштабирует его,
    при этом сглаживая края изображения и предотвращая появление артефактов при изменении
    размера. Затем получаются битовые плоскости изображения. Так как оттенки серого хранят значения
    от 0 до (2 ^ 8 - 1), то и битовых плоскостей будет 8. Результат функции будет использован для определения
    "сложности" изображения
    """
    matrix = np.asarray(image.convert('L').resize((8, 8), Image.Resampling.LANCZOS), dtype=np.uint8)
    binary_matrix = (np.unpackbits(matrix.astype(np.uint8), axis=1)  # Преобразовываем числа в биты
                     .reshape(tuple([*matrix.shape, 8]))  # Преобразовываем матрицу в трёхмерную плоскость
                     .transpose((2, 0, 1)))  # Меняем оси местами и получаем нарезанные битовые области изображения
    return binary_matrix
