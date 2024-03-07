import numpy as np


def complexity_metric(bit_planes: np.array) -> float:
    column_bounds = np.sum(np.abs(np.diff(bit_planes, axis=1)))
    row_bounds = np.sum(np.abs(np.diff(bit_planes, axis=2)))
    complexity = (row_bounds + column_bounds) / ((2 * bit_planes.shape[1] * (bit_planes.shape[1] - 1)) * bit_planes.shape[0])
    return round(complexity, 4)


def modified_complexity_metric(bit_planes: np.array) -> float:
    # По столбцам
    complexity_column = 0
    zeros_in_columns = np.count_nonzero(bit_planes == 0, axis=1)
    ones_in_columns = np.count_nonzero(bit_planes == 1, axis=1)

    # По строкам
    complexity_row = 0
    zeros_in_rows = np.count_nonzero(bit_planes == 0, axis=2)
    ones_in_rows = np.count_nonzero(bit_planes == 1, axis=2)

    complexity = (complexity_column + complexity_row) / 2
    return round(complexity)
