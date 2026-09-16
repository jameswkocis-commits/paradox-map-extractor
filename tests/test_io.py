import json

import geopandas as gpd
from shapely.geometry import box
from paradox_mapper.models import ProvinceObservation,ControlPoint
from paradox_mapper.export.gis import export_results
from paradox_mapper.project.project_file import save_project,load_project

def observation(): return ProvinceObservation(1,(1,2,3),(1.,2.,3.),20,1.,.9,.8,'shot.png','cluster_001','Rome')
def test_geojson_and_gpkg_export(tmp_path):
    gdf=gpd.GeoDataFrame({'province_id':[1],'source_r':[10],'source_g':[20],'source_b':[30],'geometry':[box(0,0,2,2)]},crs=None)
    for name in ('out.geojson','out.gpkg'):
        path=tmp_path/name; export_results(gdf,[observation()],path); loaded=gpd.read_file(path,layer='provinces' if name.endswith('gpkg') else None)
        assert loaded.iloc[0].province_id==1; assert loaded.iloc[0].entity_name=='Rome'
        if name.endswith('gpkg'):
            assert loaded.crs is None
        else:
            # GeoJSON has no general-purpose "undefined/game coordinates" CRS.
            # GDAL therefore reports RFC 7946 GeoJSON without a `crs` member as
            # EPSG:4326 on read, even though the exporter did not assign one.
            document = json.loads(path.read_text(encoding='utf-8'))
            assert 'crs' not in document

def test_project_roundtrip_relative_paths(tmp_path):
    raster=tmp_path/'provinces.bmp'; raster.write_bytes(b'x'); path=tmp_path/'campaign.pme.json'
    project={'province_raster':str(raster),'definition_csv':str(tmp_path/'definition.csv'),'cached_vector':'','screenshots':[{'path':str(tmp_path/'shot.png'),'control_points':[ControlPoint((1,2),(3,4))],'homography':[[1,0,0],[0,1,0],[0,0,1]]}],'observations':[observation()],'cluster_names':{'cluster_001':'Rome'},'manual_overrides':{},'extraction_parameters':{'erosion':2}}
    save_project(path,project); loaded=load_project(path)
    assert loaded['province_raster']==str(raster.resolve()); assert loaded['screenshots'][0]['control_points'][0].map_point==(1,2); assert loaded['observations'][0].rgb==(1,2,3)
