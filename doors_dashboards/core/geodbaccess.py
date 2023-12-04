from typing import List

from xcube_geodb.core.geodb import GeoDBClient

from .point import Point


def get_points_from_geodb(
        collection: str, database: str, variables: List[str],
        name_of_time_column: str = 'timestamp'
) -> List[Point] :
    geodb = GeoDBClient(
        auth_aud='https://xcube-users.brockmann-consult.de/api/v2'
    )
    gdf = geodb.get_collection(collection, database=database)
    points_gdf = gdf[gdf["geometry"].geom_type == 'Point']
    points_gdf['lon'] = points_gdf.geometry.apply(lambda p: p.x)
    points_gdf['lat'] = points_gdf.geometry.apply(lambda p: p.y)

    sub_gdf_list = ['lat', 'lon', name_of_time_column] + variables
    sub_gdf = points_gdf[sub_gdf_list]

    points = []

    for i, row in sub_gdf.iterrows():
        dic = row.to_dict()
        res = ''
        for k, v in dic.items():
            res += f'{k}: {v}<br>'
        points.append((row.lon, row.lat, res[:-4], dic))

    return points
