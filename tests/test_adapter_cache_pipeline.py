import numpy as np
from PIL import Image
from paradox_mapper.games.eu4 import EU4Adapter
from paradox_mapper.map.cache import save_cache,load_cache
from paradox_mapper.extraction.pipeline import analyze_screenshot

def test_adapter_cache_and_pipeline(tmp_path):
    raster=np.zeros((10,20,3),np.uint8); raster[:,:10]=(10,20,30); raster[:,10:]=(40,50,60)
    bmp=tmp_path/'provinces.bmp'; Image.fromarray(raster).save(bmp); csv=tmp_path/'definition.csv'; csv.write_text('1;10;20;30\n2;40;50;60\n')
    arr,defs,gdf=EU4Adapter().import_map(bmp,csv); assert len(gdf)==2
    cache=tmp_path/'cache.gpkg'; save_cache(gdf,cache,bmp); assert len(load_cache(cache,bmp))==2
    screenshot=np.zeros_like(raster); screenshot[:,:10]=(150,20,20); screenshot[:,10:]=(20,20,150)
    # GIS raster extent y=0..10; identity corresponds when screenshot content is vertically symmetric.
    observations=analyze_screenshot(gdf,screenshot,np.eye(3),erosion=1,cluster_eps=8)
    assert len(observations)==2; assert len({o.cluster_id for o in observations})==2
