import numpy as np


def complexity_metric(image_bit_plane: np.array) -> float | None:
    try:
        if image_bit_plane.shape[0] != image_bit_plane.shape[1]:
            raise ValueError('Матрица не квадратная!')
    except ValueError as e:
        print(e)
        return None
    column_bounds = np.sum(np.abs(np.diff(image_bit_plane, axis=0)))
    row_bounds = np.sum(np.abs(np.diff(image_bit_plane, axis=1)))
    complexity = (row_bounds + column_bounds) / (2 * image_bit_plane.shape[0] * (image_bit_plane.shape[0] - 1))
    return complexity
