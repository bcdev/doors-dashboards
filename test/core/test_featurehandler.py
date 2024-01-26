from unittest import TestCase

from doors_dashboards.core.featurehandler import FeatureHandler


class FeatureHandlerClass(TestCase):

    def test_read_features_multiple_collections(self):
        test_config = [
            dict(id="EMBLAS_CHL_2016_2019",
                 type="geodb",
                 params=dict(
                    title="EMBLAS_CHL_2016_2019",
                    collection="EMBLAS_CHL_2016_2019",
                    database="water-quality",
                    label="station",
                    levels=["cruise", "station", "sampling_depth"],
                    geometry_per="station",
                    variables=[
                        "chl-a [mg/m3]"
                    ]
                )
            ),
            dict(id="EMBLAS_Physics_2016_2019",
                 type="geodb",
                 params=dict(
                     title="EMBLAS_Physics_2016_2019",
                     collection="EMBLAS_Physics_2016_2019",
                     database="water-quality",
                     label="station",
                     levels=["cruise", "station", "sampling_depth"],
                     geometry_per="station",
                     variables=[
                         "salinity [psu]",
                         "temperature [°c]"
                     ]
                 )
            ),
            dict(id="EMBLAS_Nutrients_2016_2019",
                 type="geodb",
                 params=dict(
                     title="EMBLAS_Nutrients_2016_2019",
                     collection="EMBLAS_Nutrients_2016_2019",
                     database="water-quality",
                     label="station",
                     levels=["cruise", "station", "sampling_depth"],
                     geometry_per="station",
                     convert_from_parameters=dict(
                         keys=["station", "sampling depth [m]"],
                         parameter="parameter",
                         value="value"
                     ),
                     variables=[
                         "Ammonia nitrogen",
                         "Nitrate nitrogen",
                         "Nitrite nitrogen",
                         "Phosphate",
                         "Silicon",
                         "Total nitrogen",
                         "Total phosphorus"
                     ]
                 )
            )
        ]
        feature_handler = FeatureHandler(test_config)
        self.assertEquals(
            ["cruise", "station", "sampling_depth"],
            feature_handler.get_levels("EMBLAS_CHL_2016_2019")
        )
        df = feature_handler.get_df("EMBLAS_Nutrients_2016_2019")
        self.assertIsNotNone(df)
        df.to_csv("test.csv")
