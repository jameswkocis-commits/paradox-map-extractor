from __future__ import annotations
from dataclasses import dataclass
from shapely.geometry import box
from paradox_mapper.registration.transforms import transform_geometry
@dataclass(slots=True)
class VisibleProvince:
    province_id:int
    screen_geometry:object
    visible_fraction:float
    reliable:bool

def visible_provinces(provinces,matrix,screen_width,screen_height,min_area=9.0):
    viewport=box(0,0,screen_width,screen_height); result=[]
    for row in provinces.itertuples():
        projected=transform_geometry(row.geometry,matrix)
        if projected.is_empty or not projected.is_valid: projected=projected.buffer(0)
        clipped=projected.intersection(viewport)
        if clipped.is_empty or projected.area<=0: continue
        fraction=min(1.0,float(clipped.area/projected.area))
        result.append(VisibleProvince(int(row.province_id),clipped,fraction,clipped.area>=min_area))
    return result
