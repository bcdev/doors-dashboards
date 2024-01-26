import geopandas as gpd
from typing import Any
from typing import Dict
from typing import List

from xcube_geodb.core.geodb import GeoDBClient



_GEODB_CLIENT = None


def _get_client() -> GeoDBClient:
    global _GEODB_CLIENT
    if _GEODB_CLIENT is None:
        _GEODB_CLIENT = GeoDBClient(
            auth_aud='https://xcube-users.brockmann-consult.de/api/v2'
        )
    return _GEODB_CLIENT


def get_collection_names_from_geodb():
    geodb = _get_client()
    df = geodb.get_my_collections()
    doors_collections = df[df["database"].str.contains("doors") == True]
    return list(doors_collections.collection)


def get_dataframe_from_geodb(
        collection: str, database: str, variables: List[str],
        name_of_time_column: str = 'timestamp',
        convert_from_parameters: Dict[str, Any] = None
) -> gpd.GeoDataFrame :
    geodb = _get_client()
    gdf = geodb.get_collection(collection, database=database)

    if convert_from_parameters:
        keys = convert_from_parameters.get("keys")
        value = convert_from_parameters.get("value")
        parameter = convert_from_parameters.get("parameter")
        full = keys + [value]
        for variable in variables:
            sgdf = gdf[gdf[parameter] == variable][full]
            for row, line in sgdf.iterrows():
                loc_row = (gdf[keys[0]] == line[keys[0]])
                for key in keys[1:]:
                    loc_row &= (gdf[key] == line[key])
                gdf.loc[loc_row, variable] = line[value]

    points_gdf = gdf[gdf["geometry"].geom_type == 'Point']
    points_gdf['lon'] = points_gdf.geometry.apply(lambda p: p.x)
    points_gdf['lat'] = points_gdf.geometry.apply(lambda p: p.y)

    sub_gdf_list = ['lat', 'lon', name_of_time_column] + variables
    sub_gdf = points_gdf[sub_gdf_list]

    sub_gdf = sub_gdf.drop_duplicates()

    return sub_gdf
