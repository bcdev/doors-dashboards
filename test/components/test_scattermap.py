from doors_dashboards.components.scattermap import read_points

import unittest


class ConvertPointsTest(unittest.TestCase):

    def test_convert_points(self):
        input_points = [
            (-77.02, 12.03, 'Lima'),
            (31.14, 30.2, 'Cairo'),
            (100.29, 13.45, 'Bangkok')
        ]
        lons, lats, labels = read_points(input_points)
        self.assertEquals([-77.02, 31.14, 100.29], lons)
        self.assertEquals([12.03, 30.2, 13.45], lats)
        self.assertEquals(['Lima', 'Cairo', 'Bangkok'], labels)
