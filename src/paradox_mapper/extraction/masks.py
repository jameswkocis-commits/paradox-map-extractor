import cv2
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

def _polygons(geom):
    if isinstance(geom,Polygon): return [geom]
    if isinstance(geom,MultiPolygon): return list(geom.geoms)
    return [g for g in getattr(geom,'geoms',[]) if isinstance(g,Polygon)]
def geometry_mask(geometry,width,height,erosion=2):
    mask=np.zeros((height,width),np.uint8)
    for poly in _polygons(geometry):
        exterior=np.rint(poly.exterior.coords).astype(np.int32)
        cv2.fillPoly(mask,[exterior],255)
        for ring in poly.interiors: cv2.fillPoly(mask,[np.rint(ring.coords).astype(np.int32)],0)
    if erosion>0 and mask.any():
        size=max(1,int(round(erosion))*2+1); eroded=cv2.erode(mask,np.ones((size,size),np.uint8))
        if np.count_nonzero(eroded)>=3: mask=eroded
    return mask.astype(bool)
