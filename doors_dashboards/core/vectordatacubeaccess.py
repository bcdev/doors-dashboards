import geopandas as gpd
from typing import List
import xvec

from xcube.core.store import new_data_store

from doors_dashboards.core.constants import LOG

REFERENCE_CRS = "EPSG:4326"
_VECTOR_DATA_CUBES = {}

class VectorDataCubeAccessor:

    def __init__(self):
        self._vdc_stores = {}
        self._vdcs = {}
        self._gdfs = {}
        self._label_to_var = {}

    def _get_store(self, bucket: str):
        if bucket not in self._vdc_stores:
            storage_options = dict(
                anon=False
            )
            store = new_data_store(
                "s3",
                storage_options=storage_options,
                root=bucket
            )
            self._vdc_stores[bucket] = store
        return self._vdc_stores.get(bucket)

    def _get_vdc(self, filename: str, bucket: str):
        data_id = f"{bucket}/{filename}"
        if data_id not in self._vdcs:
            store = self._get_store(bucket)
            vdc = store.open_data(filename)
            try:
                vdc = vdc.xvec.decode_cf()
            except:
                LOG.warning(f"Could not decode dataset '{data_id}'")
            self._vdcs[data_id] = vdc
        return self._vdcs[data_id]

    def get_dataframe_from_vector_data_cube(
        self,
        filename: str,
        bucket: str,
        variables: List[str],
        collection: str,
        time_stamp_name: str = None,
        collection_coord: str = None,
        mask: gpd.GeoDataFrame = None,
    ) -> gpd.GeoDataFrame:
        gdf_id = f"{bucket}/{filename}/{collection}"
        if gdf_id not in self._gdfs:
            vdc = self._get_vdc(filename, bucket)
            for j, coord in enumerate(vdc.xvec.geom_coords):
                geometry_name = coord
                break
            labels = vdc[collection_coord].values
            index = list(labels).index(collection)
            sub_vdc = vdc.isel({geometry_name: index})
            sub_gdf = sub_vdc.xvec.to_geodataframe(geometry=geometry_name)
            sub_gdf = sub_gdf.reset_index()
            LOG.debug("Created sub-geodataframe")
            if sub_gdf.crs != REFERENCE_CRS:
                sub_gdf = sub_gdf.to_crs(REFERENCE_CRS)
            self._gdfs[gdf_id] = sub_gdf
        gdf = self._gdfs[gdf_id]
        variables = variables.copy()
        if "geometry" not in variables:
            variables.append("geometry")
        if time_stamp_name not in variables:
            variables.append(time_stamp_name)
        gdf = gdf[variables]
        if mask is not None:
            gdf = gdf.clip(mask)
        return gdf

    def get_label(
            self,
            filename: str,
            bucket: str,
            collection: str,
            variable: str
    ):
        vdc = self._get_vdc(filename, bucket)
        var_attrs = vdc[variable].attrs
        label = var_attrs.get("long_name", var_attrs.get("description", variable))
        self._label_to_var[f"{collection}_{label}"] = variable
        return label

    def get_var_for_label(
            self,
            collection: str,
            label: str
    ):
        return self._label_to_var.get(f"{collection}_{label}", label)
