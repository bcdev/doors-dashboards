import pandas as pd
import geopandas as gpd
from shapely import wkt
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from doors_dashboards.core.constants import REFERENCE_CRS
from doors_dashboards.core.geodbaccess import get_dataframe_from_geodb


class FeatureHandler:

    def __init__(self, configs: List, eez: str=None):
        self._configs = {c["id"]: c for c in configs}
        self._dfs = {}
        self._eez_frame = self._load_eez(eez)
        self._selected_collection = self.get_collections()[0] \
            if len(self.get_collections()) > 0 else None

    def select_collection(self, collection_name: str):
        if collection_name not in self.get_collections():
            raise ValueError(f"Unknown collection {collection_name}")
        self._selected_collection = collection_name

    def get_selected_collection(self) -> Optional[str]:
        return self._selected_collection

    def get_default_collection(self) -> str:
        return self.get_collections()[0]

    def get_default_variable(self, collection: str) -> str:
        return self.get_variables(collection)[0]

    @staticmethod
    def _load_eez(eez: str = None):
        if eez:
            extended_eez_path = f"../../data/eez/{eez}/{eez}.shp"
            eez = gpd.read_file(extended_eez_path, driver='ESRI Shapefile')
            eez = eez.to_crs(REFERENCE_CRS)
            return eez

    def get_collections(self) -> List[str]:
        return list(self._configs.keys())

    def get_df(self, collection: str = None) -> gpd.GeoDataFrame:
        collection = self._selected_collection if not collection else collection
        if collection not in self._dfs:
            if collection not in self._configs:
                raise ValueError(
                    f"No collection with name '{collection}' configured."
                )
            self._dfs[collection] = self._read_features(
                self._configs[collection]
            )
        return self._dfs[collection]

    def get_variables(self, collection: str = None):
        collection = self._selected_collection if not collection else collection
        variables = self._configs.get(collection, {}).get("params", {}).\
            get("variables")
        time_column_name = self.get_time_column_name(collection)
        if variables is None:
            variables = list(self.get_df(collection).columns)
            to_be_removed = ["geometry", time_column_name]
            label = self._get_label_column_name(collection)
            if label:
                to_be_removed.append(label)
            to_be_removed.extend(self.get_levels(collection))
            for r in to_be_removed:
                if r in variables:
                    variables.remove(r)
        variables.sort()
        return variables

    def get_time_column_name(self, collection: str = None):
        collection = self._selected_collection if not collection else collection
        return self._configs.get(collection, {}).get("params", {}).\
            get("time_column", "timestamp")

    def get_time_range(self, collection: str = None) -> \
            Tuple[pd.Timestamp, pd.Timestamp]:
        df = self.get_df(collection)
        time_column_name = self.get_time_column_name(collection)
        dt_time = pd.to_datetime(df[time_column_name])
        return pd.Timestamp(min(dt_time)), pd.Timestamp(max(dt_time))

    def _get_label_column_name(self, collection: str):
        return self._configs.get(collection, {}).get("params", {}).get("label")

    def get_color_code_config(self, collection: str) -> Dict[str, Any]:
        return (self._configs.get(collection, {}).get("params", {}).
                get("colorcodevariable", {}))

    def get_levels(self, collection: str = None) -> List[str]:
        collection = self._selected_collection if not collection else collection
        return self._configs.get(collection, {}).get("params", {}).\
            get("levels", [])

    def get_color(self, collection: str = None) -> str:
        collection = self._selected_collection if not collection else collection
        return self._configs.get(collection, {}).get("params", {}).\
            get("color", "blue")

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

    def get_nested_level_values(self, collection: str = None) \
            -> Optional[Union[List[str], Dict[str, Any]]]:
        collection = self._selected_collection if not collection else collection
        levels = self.get_levels(collection)
        if not levels:
            return None
        gdf = self.get_df(collection)
        return self._get_nested_level_values(gdf, levels)

    def _read_features(self, features: Dict) -> gpd.GeoDataFrame:
        if features.get("type") == "local":
            filepath = features.get("params").get("file")
            crs = features.get("params").get("crs", REFERENCE_CRS)
            with open(filepath, "r") as points_file:
                df = pd.read_csv(points_file)
                df["geometry"] = df["geometry"].apply(wkt.loads)
                gdf = gpd.GeoDataFrame(df, crs=crs)
                if crs != REFERENCE_CRS:
                    gdf = gdf.to_crs(REFERENCE_CRS)
                if self._eez_frame is not None:
                    gdf = gdf.clip(self._eez_frame)
                return gdf
        if features.get("type") == "geodb":
            params = features.get("params")
            return get_dataframe_from_geodb(
                params.get("collection"),
                params.get("database"),
                variables=params.get("variables"),
                name_of_time_column=params.get("time_column", "timestamp"),
                convert_from_parameters=params.get(
                    "convert_from_parameters", None
                ),
                label=params.get("label"),
                levels=params.get("levels"),
                mask=self._eez_frame
            )

    def get_points_as_tuples(self, collection: str = None) -> \
            Tuple[List[float], List[float], List[str], List[float]]:
        collection = self._selected_collection if not collection else collection
        gdf = self.get_df(collection)

        lons = list(gdf.geometry.apply(lambda p: p.x))
        lats = list(gdf.geometry.apply(lambda p: p.y))

        label = self._get_label_column_name(collection)
        if label:
            labels = list(gdf[label])
        else:
            labels = []
            for i, row in gdf.iterrows():
                dic = row.to_dict()
                res = ''
                for k, v in dic.items():
                    res += f'{k}: {v}<br>'
                labels.append(res[:-4])
        ccvar = self.get_color_code_config(collection).get("name")
        values = list(df[ccvar]) if ccvar else None
        return lons, lats, labels, values
