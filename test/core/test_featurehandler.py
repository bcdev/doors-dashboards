from unittest import TestCase

from doors_dashboards.core.featurehandler import FeatureHandler

_TEST_CONFIG = [
    dict(
        id="1",
        type="local",
        params=dict(
            file="test_data/1.csv",
            label="mylabel"
        )
    ),
    dict(
        id="2",
        type="local",
        params=dict(
            file="test_data/2.csv",
            variables=[
                "chlorophyll",
                "temperature"
            ]
        )
    ),
    dict(
        id="3",
        type="local",
        params=dict(
            file="test_data/3.csv",
            label="label",
            levels=["station"],
            variables=[
                "chlorophyll",
                "temperature"
            ]
        )
    ),
    dict(
        id="4",
        type="local",
        params=dict(
            file="test_data/4.csv",
            label="station",
            levels=["cruise", "station", "sampling_depth"],
            variables=[
                "chlorophyll",
                "temperature"
            ]
        )
    ),
]


class FeatureHandlerClass(TestCase):

    def setUp(self) -> None:
        self.feature_handler = FeatureHandler(_TEST_CONFIG)

    def test_get_collections(self):
        self.assertEqual(
            ["1", "2", "3", "4"], self.feature_handler.get_collections()
        )

    def test_get_variables(self):
        self.assertEqual([], self.feature_handler.get_variables("1"))
        self.assertEqual(["chlorophyll", "temperature"],
                          self.feature_handler.get_variables("2"))
        self.assertEqual(["chlorophyll", "temperature"],
                          self.feature_handler.get_variables("3"))
        self.assertEqual(["chlorophyll", "temperature"],
                          self.feature_handler.get_variables("4"))

    def test_get_levels(self):
        self.assertEqual([], self.feature_handler.get_levels("1"))
        self.assertEqual([], self.feature_handler.get_levels("2"))
        self.assertEqual(["station"], self.feature_handler.get_levels("3"))
        self.assertEqual(["cruise", "station", "sampling_depth"],
                          self.feature_handler.get_levels("4"))

    def test_get_nested_level_values(self):
        self.assertIsNone(self.feature_handler.get_nested_level_values("1"))
        self.assertIsNone(self.feature_handler.get_nested_level_values("2"))
        self.assertEqual(
            ["Terminal East", "Terminal Bulk Cargoes", "Terminal 2A",
             "Terminal West", "Terminal Rosenets", "Terminal Nessebar",
             "Terminal Sozopol"],
            self.feature_handler.get_nested_level_values("3")
        )
        nested_levels_4 = {
            "JBSS GE-UA 2019": {
                "JBSS GE-UA - 1A": [0.0, 11.0],
                "JBSS GE-UA - 2A": [0.0, 21.0]
            },
            "JOSS GE-UA 2016": {
                "JOSS GE-UA - 13": [54.0, 70.0],
                "JOSS GE-UA - 21": [0.0, 40.0]
            },
        }
        self.assertEqual(nested_levels_4,
                          self.feature_handler.get_nested_level_values("4"))

    def test_get_points_as_tuples_1(self):
        lons, lats, labels = self.feature_handler.get_points_as_tuples("1")
        self.assertEqual([20.5, 21.5, 22.5], lons)
        self.assertEqual([22.2, 42.2, 62.2], lats)
        self.assertEqual(["x", "y", "z"], labels)

    def test_get_points_as_tuples_2(self):
        lons, lats, labels = self.feature_handler.get_points_as_tuples("2")
        self.assertEqual([20.1, 10.2, -10.3], lons)
        self.assertEqual([65.4, 55.3, 45.2], lats)
        self.assertEqual([
            "lon: 20.1<br>lat: 65.4<br>chlorophyll: 0.001<br>"
            "temperature: 20.1<br>timestamp: 2007-10-12T23:01:02",
            "lon: 10.2<br>lat: 55.3<br>chlorophyll: 0.005<br>"
            "temperature: 10.1<br>timestamp: 2007-10-13T22:01:02",
            "lon: -10.3<br>lat: 45.2<br>chlorophyll: 0.01<br>"
            "temperature: 12.4<br>timestamp: 2007-10-14T21:01:02"],
            labels
        )

    def test_get_points_as_tuples_3(self):
        lons, lats, labels = self.feature_handler.get_points_as_tuples("3")
        self.assertEqual(
            [27.479, 27.47, 27.467, 27.457, 27.53, 27.728, 27.687], lons
        )
        self.assertEqual(
            [42.486, 42.486, 42.48, 42.485, 42.45, 42.657, 42.42], lats
        )
        self.assertEqual(["Terminal East", "Terminal Bulk Cargoes",
                           "Terminal 2A", "Terminal West", "Terminal Rosenets",
                           "Terminal Nessebar", "Terminal Sozopol"],
                          labels)

    def test_get_points_as_tuples_4(self):
        lons, lats, labels = self.feature_handler.get_points_as_tuples("4")
        self.assertEqual(
            [30.2518, 30.2518, 31.0021, 31.0021,
             36.0697, 36.0697, 31.5675, 31.5675], lons
        )
        self.assertEqual(
            [45.3386, 45.3386, 46.3333, 46.3333,
             43.526, 43.526, 44.1582, 44.1582], lats
        )
        self.assertEqual(
            ["JBSS GE-UA - 1A", "JBSS GE-UA - 1A", "JBSS GE-UA - 2A",
             "JBSS GE-UA - 2A", "JOSS GE-UA - 13", "JOSS GE-UA - 13",
             "JOSS GE-UA - 21", "JOSS GE-UA - 21"],
            labels
        )
