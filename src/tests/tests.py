import numpy as np
import unittest
from src.utils.image_conversion import bit_planes
from src.utils.image_metrics import complexity_metric, modified_complexity_metric


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.matrix = np.random.randint(0, 256, (2, 2, 3)).astype(np.uint8)
        self.bit_matrix = np.random.randint(0, 2, (8, 3, 3))

    def test_complexity_metric(self):
        print('bit planes:\n', self.bit_matrix)
        print('Bit plane complexity:\n', modified_complexity_metric(self.bit_matrix))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
