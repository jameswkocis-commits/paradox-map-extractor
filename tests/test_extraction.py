import numpy as np
import geopandas as gpd
from shapely.geometry import box
from paradox_mapper.extraction.masks import geometry_mask
from paradox_mapper.extraction.visibility import VisibleProvince,visible_provinces
from paradox_mapper.extraction.color_sampling import sample_province
from paradox_mapper.extraction.clustering import cluster_observations,rename_cluster

def test_interior_mask_and_robust_color():
    image=np.full((20,20,3),(100,40,20),np.uint8); image[5,5]=(255,255,255)
    v=VisibleProvince(7,box(2,2,18,18),.8,True); mask=geometry_mask(v.screen_geometry,20,20,2)
    assert mask[10,10] and not mask[2,2]
    obs=sample_province(image,v,erosion=2); assert obs.rgb==(100,40,20); assert obs.sample_count>10; assert 0<=obs.confidence<=1

def test_visibility_and_clustering():
    gdf=gpd.GeoDataFrame({'province_id':[1,2],'geometry':[box(0,0,10,10),box(30,30,40,40)]})
    visible=visible_provinces(gdf,np.eye(3),15,15); assert [v.province_id for v in visible]==[1]
    image=np.zeros((20,20,3),np.uint8)
    items=[]
    for pid,color in [(1,(100,20,20)),(2,(104,22,20)),(3,(20,20,140))]:
        image[:]=color; items.append(sample_province(image,VisibleProvince(pid,box(1,1,18,18),1,True)))
    cluster_observations(items,eps=8); assert items[0].cluster_id==items[1].cluster_id!=items[2].cluster_id
    rename_cluster(items,items[0].cluster_id,'Byzantium'); assert items[1].entity_name=='Byzantium'
