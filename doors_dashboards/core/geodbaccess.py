import geopandas as gpd
from typing import Any
from typing import Dict
from typing import List

from xcube_geodb.core.geodb import GeoDBClient

from doors_dashboards.core.constants import REFERENCE_CRS

_GEODB_CLIENT = None
_PART_SIZE = 100000


def _get_client() -> GeoDBClient:
    global _GEODB_CLIENT
    if _GEODB_CLIENT is None:
        _GEODB_CLIENT = GeoDBClient(
            auth_aud="https://xcube-users.brockmann-consult.de/api/v2",
            auth_domain="https://winchester.production.brockmann-consult.de/winchester",
            gs_server_url="https://winchester.production.brockmann-consult.de/winchester"
        )
    return _GEODB_CLIENT


def get_collection_names_from_geodb():
    geodb = _get_client()
    df = geodb.get_my_collections()
    doors_collections = df[df["database"].str.contains("doors")]
    return list(doors_collections.collection)


def get_dataframe_from_geodb(
    collection: str,
    database: str,
    variables: List[str],
    name_of_time_column: str = "timestamp",
    convert_from_parameters: Dict[str, Any] = None,
    label: str = None,
    levels: List[str] = None,
    mask: gpd.GeoDataFrame = None,
) -> gpd.GeoDataFrame:
    geodb = _get_client()
    num_rows = geodb.count_collection_rows(collection, database=database)
    if num_rows > 1000000:
        gdf = geodb.get_collection_pg(
            collection, where="id % 100 = 0", database=database
        )
    else:
        gdf = geodb.get_collection(collection, database=database)

    gdf = gdf.sort_values("id")
    if gdf.crs != REFERENCE_CRS:
        gdf = gdf.to_crs(REFERENCE_CRS)
    if mask is not None:
        gdf = gdf.clip(mask)

    if convert_from_parameters:
        keys = convert_from_parameters.get("keys")
        value = convert_from_parameters.get("value")
        parameter = convert_from_parameters.get("parameter")
        full = keys + [value]
        for variable in variables:
            sgdf = gdf[gdf[parameter] == variable][full]
            for row, line in sgdf.iterrows():
                loc_row = gdf[keys[0]] == line[keys[0]]
                for key in keys[1:]:
                    loc_row &= gdf[key] == line[key]
                gdf.loc[loc_row, variable] = line[value]

    sub_gdf_list = ["geometry", name_of_time_column] + variables
    if levels:
        sub_gdf_list.extend(levels)
    if label:
        sub_gdf_list.append(label)
    sub_gdf_list = list(set(sub_gdf_list))
    sub_gdf = gdf[sub_gdf_list]

    sub_gdf = sub_gdf.drop_duplicates()

    return sub_gdf
