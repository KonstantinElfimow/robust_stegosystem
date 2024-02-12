import numpy as np
import scipy.stats as st


def pca(features: np.ndarray, n_components: int):
    """
    Метод главных компонент, PCA (principal component analysis).
    Линейный алгоритм неконтролируемого машинного обучения
    """
    # Вычисляем среднее по векторам
    mean = np.mean(features, axis=0)
    # Центрирование
    centered_data = features - mean
    # Вычисление ковариационной матрицы
    covariance_matrix = np.cov(centered_data, rowvar=False)
    # Вычисление собственных значений и собственных векторов ковариационной матрицы
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    del covariance_matrix
    # Сортировка собственных векторов в порядке убывания собственных значений
    indices = np.argsort(eigenvalues)[::-1]
    sorted_eigenvalues, sorted_eigenvectors = eigenvalues[indices], eigenvectors[:, indices]

    # Выбор первых k собственных векторов
    selected_eigenvectors = sorted_eigenvectors[:, :n_components]

    # Преобразование данных в новое пространство признаков
    reduced_features = np.dot(centered_data, selected_eigenvectors)
    # Обратное преобразование данных в исходное пространство признаков
    new_features = (np.asarray(np.dot(reduced_features, selected_eigenvectors.T) + mean, dtype=np.complex64)
                    .real
                    .astype(np.uint8))
    return new_features
