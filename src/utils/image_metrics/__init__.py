import numpy as np


def complexity_metric(bit_planes: np.array) -> float:
    converted = np.array(bit_planes, dtype=np.int8)
    column_bounds = np.mean(np.sum(np.abs(np.diff(converted, axis=1)), axis=(1, 2)))
    row_bounds = np.mean(np.sum(np.abs(np.diff(converted, axis=2)), axis=(1, 2)))
    complexity = (row_bounds + column_bounds) / (2 * bit_planes.shape[1] * (bit_planes.shape[1] - 1))
    return round(complexity, 4)
