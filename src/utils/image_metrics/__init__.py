import numpy as np


def complexity_metric(image_bit_plane: np.array):
    # image_bit_plane = np.random.randint(0, 2, (4, 4))
    assert image_bit_plane.shape[0] == image_bit_plane.shape[1]
    column_bounds = np.sum(np.abs(np.diff(image_bit_plane, axis=0)))
    row_bounds = np.sum(np.abs(np.diff(image_bit_plane, axis=1)))
    complexity = (row_bounds + column_bounds) / (2 * image_bit_plane.shape[0] * (image_bit_plane.shape[0] - 1))
    print(image_bit_plane)
    print(row_bounds)
    print(column_bounds)
    print(complexity)
    return complexity
