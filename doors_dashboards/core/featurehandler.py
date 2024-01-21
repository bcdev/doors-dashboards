import pandas as pd
from typing import Dict
from typing import List
from typing import Tuple

from doors_dashboards.core.geodbaccess import get_dataframe_from_geodb


class FeatureHandler():

    def __init__(self, config: Dict):
        self._df = self.read_features(config)
        self._label = config.get("label")
        self._variables = config.get("variables")

    @property
    def df(self):
        return self._df

    @property
    def variables(self):
        return self._variables

    def read_features(self, features: Dict) -> pd.DataFrame:
        if "file" in features:
            with open(features["file"], "r") as points_file:
                df = pd.read_csv(points_file)
            return df
        if "geodb" in features:
            return get_dataframe_from_geodb(
                features["geodb"].get("collection"),
                features["geodb"].get("database"),
                variables=features.get("variables")
            )
        return None

    def get_points_as_tuples(self) -> \
            Tuple[List[float], List[float], List[str]]:
        lons = list(self.df["lon"])
        lats = list(self.df["lat"])
        labels = [""] * len(lons)
        if self._label:
            labels = list(self.df[self._label])
        elif self.variables:
            labels = []
            for i, row in self.df.iterrows():
                dic = row.to_dict()
                res = ''
                for k, v in dic.items():
                    res += f'{k}: {v}<br>'
                labels.append(res[:-4])
        return lons, lats, labels

    @df.setter
    def df(self, value):
        self._df = value

    @variables.setter
    def variables(self, value):
        self._variables = value
