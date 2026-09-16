from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import box, MultiPolygon
from paradox_mapper.map.definition_parser import parse_definition
from paradox_mapper.map.raster_loader import validate_raster_colors,boundary_reference
from paradox_mapper.map.polygonizer import polygonize_provinces,image_to_gis,gis_to_image
from paradox_mapper.models import ControlPoint
from paradox_mapper.registration.transforms import calculate_homography,transform_points,inverse_homography

def test_definition_tolerates_header_extra_blank_and_encoding(tmp_path):
    p=tmp_path/'definition.csv'; p.write_bytes('province;red;green;blue;name\n1;10;20;30;Caf\xe9\n\n2;40;50;60;x\n'.encode('latin1'))
    d=parse_definition(p); assert d.rgb_to_id[(10,20,30)]==1; assert d.id_to_rgb[2]==(40,50,60)

def test_raster_polygonization_combines_islands_and_coordinates():
    raster=np.zeros((4,5,3),np.uint8); raster[0:2,0:2]=(10,20,30); raster[3,4]=(10,20,30); raster[:,2:4]=(40,50,60)
    gdf=polygonize_provinces(raster,{(10,20,30):1,(40,50,60):2})
    assert set(gdf.province_id)=={1,2}; assert isinstance(gdf.loc[gdf.province_id==1,'geometry'].iloc[0],MultiPolygon)
    assert gdf.total_bounds.tolist()==[0,0,5,4]
    assert image_to_gis(3,1,4)==(3,3); assert gis_to_image(3,3,4)==(3,1)
    assert validate_raster_colors(raster,{(10,20,30):1,(40,50,60):2})==[]

def test_boundary_reference():
    a=np.zeros((2,2,3),np.uint8); a[:,1:]=1; out=boundary_reference(a); assert tuple(out[0,1])==(25,25,25)

def test_homography_roundtrip():
    src=np.array([[0,0],[10,0],[10,10],[0,10],[5,5]],float); dst=src*np.array([2,3])+np.array([7,9])
    points=[ControlPoint(tuple(a),tuple(b)) for a,b in zip(src,dst)]
    h,errors,inliers=calculate_homography(points); assert errors.max()<1e-5; assert inliers.all()
    assert np.allclose(transform_points(transform_points(src,h),inverse_homography(h)),src,atol=1e-6)
