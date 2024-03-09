import numpy as np
import scipy.stats as st
from scipy import stats


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


def conf_interval_for_probabilistic_problem(n, alpha, p=0.5) -> (float, float):
    """ Функция позволяет определить доверительный интервал для задачи оценки вероятности событий """
    d = stats.norm.ppf(1 - alpha / 2) * ((p * (1 - p) / n) ** .5)
    return (p - d), (p + d)
