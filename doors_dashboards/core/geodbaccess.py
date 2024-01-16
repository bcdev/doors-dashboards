import geopandas as gpd
from typing import List

from xcube_geodb.core.geodb import GeoDBClient

from .point import Point


_GEODB_CLIENT = None


def _get_client() -> GeoDBClient:
    if _GEODB_CLIENT is None:
        _GEODB_CLIENT = GeoDBClient(
            auth_aud='https://xcube-users.brockmann-consult.de/api/v2'
        )
    global _GEODB_CLIENT
    return _GEODB_CLIENT


def get_collection_names_from_geodb():
    geodb = _get_client()
    df = geodb.get_my_collections()
    doors_collections = df[df["database"].str.contains("doors") == True]
    return list(doors_collections.collection)


def get_points_from_geodb(
        collection: str, database: str, variables: List[str],
        name_of_time_column: str = 'timestamp'
) -> List[Point] :
    sub_gdf = get_dataframe_from_geodb(
        collection, database, variables, name_of_time_column
    )

    points = []

    for i, row in sub_gdf.iterrows():
        dic = row.to_dict()
        res = ''
        for k, v in dic.items():
            res += f'{k}: {v}<br>'
        points.append((row.lon, row.lat, res[:-4], dic))

    return points


def get_dataframe_from_geodb(
        collection: str, database: str, variables: List[str],
        name_of_time_column: str = 'timestamp'
) -> gpd.GeoDataFrame :
    geodb = _get_client()
    gdf = geodb.get_collection(collection, database=database)
    points_gdf = gdf[gdf["geometry"].geom_type == 'Point']
    points_gdf['lon'] = points_gdf.geometry.apply(lambda p: p.x)
    points_gdf['lat'] = points_gdf.geometry.apply(lambda p: p.y)

    sub_gdf_list = ['lat', 'lon', name_of_time_column] + variables
    sub_gdf = points_gdf[sub_gdf_list]

    return sub_gdf
