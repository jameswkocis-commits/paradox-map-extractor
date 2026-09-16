from __future__ import annotations
import logging
import numpy as np
import geopandas as gpd
from affine import Affine
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.ops import unary_union
log=logging.getLogger(__name__)

def image_to_gis(x: float, y: float, height: int) -> tuple[float,float]: return float(x), float(height-y)
def gis_to_image(x: float, y: float, height: int) -> tuple[float,float]: return float(x), float(height-y)

def polygonize_provinces(raster: np.ndarray, rgb_to_id: dict[tuple[int,int,int],int]) -> gpd.GeoDataFrame:
    if raster.ndim != 3 or raster.shape[2] != 3: raise ValueError("Province raster must be an RGB array")
    h,w,_=raster.shape
    packed=(raster[:,:,0].astype(np.int32)<<16)|(raster[:,:,1].astype(np.int32)<<8)|raster[:,:,2].astype(np.int32)
    by_id={}
    # Negative Y transform maps pixel top-left (0,0) to GIS (0,h).
    transform=Affine(1,0,0,0,-1,h)
    for geom,value in shapes(packed, transform=transform):
        rgb=((int(value)>>16)&255,(int(value)>>8)&255,int(value)&255)
        pid=rgb_to_id.get(rgb)
        if pid is not None: by_id.setdefault(pid, []).append(shape(geom))
    records=[]
    inverse={v:k for k,v in rgb_to_id.items()}
    for pid, parts in by_id.items():
        geom=unary_union(parts)
        if not geom.is_valid: geom=geom.buffer(0)
        r,g,b=inverse[pid]
        records.append({"province_id":pid,"source_r":r,"source_g":g,"source_b":b,"geometry":geom})
    if not records: raise ValueError("No raster colors match definition.csv")
    return gpd.GeoDataFrame(records, geometry="geometry", crs=None).sort_values("province_id").reset_index(drop=True)
