import pandas as pd
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from doors_dashboards.core.geodbaccess import get_dataframe_from_geodb


class FeatureHandler:

    def __init__(self, configs: List):
        self._configs = {c["id"]: c for c in configs}
        self._dfs = {}

    def get_collections(self) -> List[str]:
        return list(self._configs.keys())

    def get_df(self, collection: str):
        if collection not in self._dfs:
            if collection not in self._configs:
                raise ValueError(
                    f"No collection with name '{collection}' configured."
                )
            self._dfs[collection] = self._read_features(
                self._configs[collection]
            )
        return self._dfs[collection]

    def get_variables(self, collection: str):
        variables = self._configs.get(collection, {}).get("variables")
        if variables is None:
            variables = list(self.get_df(collection).columns)
            to_be_removed = ["lat", "lon", "timestamp"]
            label = self._get_label_column_name(collection)
            if label:
                to_be_removed.append(label)
            to_be_removed.extend(self.get_levels(collection))
            for r in to_be_removed:
                if r in variables:
                    variables.remove(r)
        return variables

    def _get_label_column_name(self, collection: str):
        return self._configs.get(collection, {}).get("params", {}).get("label")

    def get_levels(self, collection: str) -> List[str]:
        return self._configs.get(collection, {}).get("params", {}).\
            get("levels", [])

    def _get_unique_values(self, collection: str, column: str) -> List[str]:
        return list(self.get_df(collection)[column].unique())

    def _get_nested_level_values(
            self, gdf: pd.DataFrame, levels: List[str]
    ) -> Union[List[str], Dict[str, Any]]:
        level = levels[0]
        level_keys = list(gdf[level].unique())
        if len(levels) == 1:
            return level_keys
        level_dict = dict()
        for level_key in level_keys:
            sub_gdf = gdf[gdf[level] == level_key]
            level_dict[level_key] = self._get_nested_level_values(
                sub_gdf, levels[1:]
            )
        return level_dict

    def get_nested_level_values(self, collection: str) \
            -> Optional[Union[List[str], Dict[str, Any]]]:
        levels = self.get_levels(collection)
        if not levels:
            return None
        gdf = self.get_df(collection)
        return self._get_nested_level_values(gdf, levels)

    @staticmethod
    def _read_features(features: Dict) -> pd.DataFrame:
        if features.get("type") == "local":
            filepath = features.get("params").get("file")
            with open(filepath, "r") as points_file:
                return pd.read_csv(points_file)
        if features.get("type") == "geodb":
            params = features.get("params")
            return get_dataframe_from_geodb(
                params.get("collection"),
                params.get("database"),
                variables=params.get("variables"),
                convert_from_parameters=params.get(
                    "convert_from_parameters", None
                ),
                label=params.get("label"),
                levels=params.get("levels")
            )

    def get_points_as_tuples(self, collection: str) -> \
            Tuple[List[float], List[float], List[str]]:
        df = self.get_df(collection)
        lons = list(df["lon"])
        lats = list(df["lat"])
        label = self._get_label_column_name(collection)
        if label:
            labels = list(df[label])
        else:
            labels = []
            for i, row in df.iterrows():
                dic = row.to_dict()
                res = ''
                for k, v in dic.items():
                    res += f'{k}: {v}<br>'
                labels.append(res[:-4])
        return lons, lats, labels
