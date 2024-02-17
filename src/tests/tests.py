import numpy as np
import unittest
import json

from src.utils.image_conversion import bit_planes
from src.utils.image_metrics import complexity_metric


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.matrix = np.random.randint(0, 256, (2, 2, 3))
        print('The image frame:\n', self.matrix)
        self.bit_matrix = np.random.randint(0, 2, (3, 3))
        print('The bit plane:\n', self.bit_matrix)

    def test_bit_planes(self):
        print('Bit planes (Red-channel):\n', bit_planes(self.matrix[:, :, 0]))
        print('Bit planes (Green-channel):\n', bit_planes(self.matrix[:, :, 1]))
        print('Bit planes (Blue-channel):\n', bit_planes(self.matrix[:, :, 2]))
        self.assertTrue(True)

    def test_complexity_metric(self):
        print('Bit plane complexity:\n', complexity_metric(self.bit_matrix))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
