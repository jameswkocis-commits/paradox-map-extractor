from __future__ import annotations
import cv2
import numpy as np
from shapely.ops import transform as shapely_transform
from paradox_mapper.models import ControlPoint

def calculate_homography(points: list[ControlPoint]):
    if len(points)<4: raise ValueError("At least four control-point pairs are required")
    src=np.asarray([p.map_point for p in points],np.float64)
    dst=np.asarray([p.screen_point for p in points],np.float64)
    method=cv2.RANSAC if len(points)>4 else 0
    h,mask=cv2.findHomography(src,dst,method,3.0)
    if h is None or not np.isfinite(h).all() or abs(np.linalg.det(h))<1e-12: raise ValueError("Control points produce a degenerate homography")
    pred=transform_points(src,h)
    errors=np.linalg.norm(pred-dst,axis=1)
    return h, errors, (mask.ravel().astype(bool) if mask is not None else np.ones(len(points),bool))

def transform_points(points, matrix):
    p=np.asarray(points,dtype=np.float64).reshape(-1,1,2)
    return cv2.perspectiveTransform(p,matrix).reshape(-1,2)

def inverse_homography(matrix):
    try: inv=np.linalg.inv(np.asarray(matrix,dtype=float))
    except np.linalg.LinAlgError as exc: raise ValueError("Homography is not invertible") from exc
    return inv/inv[2,2]

def transform_geometry(geometry,matrix):
    def fn(x,y,z=None):
        out=transform_points(np.column_stack((x,y)),matrix)
        return out[:,0],out[:,1]
    return shapely_transform(fn,geometry)
