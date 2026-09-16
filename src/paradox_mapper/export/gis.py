from pathlib import Path
import geopandas as gpd
from paradox_mapper.export.styles import write_qml

def results_frame(provinces,observations):
    lookup={o.province_id:o for o in observations if not o.excluded}
    frame=provinces.copy()
    attrs=[]
    for pid in frame.province_id:
        o=lookup.get(int(pid)); attrs.append({
          'entity_name':o.entity_name if o else '', 'cluster_id':o.cluster_id if o else '',
          'red':o.rgb[0] if o else None,'green':o.rgb[1] if o else None,'blue':o.rgb[2] if o else None,
          'confidence':o.confidence if o else 0.0,'visible_fraction':o.visible_fraction if o else 0.0,
          'source_image':o.source_image if o else ''})
    for key in attrs[0] if attrs else []: frame[key]=[x[key] for x in attrs]
    return frame

def export_results(provinces,observations,path,dissolve=True,qml=True):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); frame=results_frame(provinces,observations)
    suffix=path.suffix.lower()
    try:
        if suffix=='.gpkg':
            frame.to_file(path,layer='provinces',driver='GPKG')
            if dissolve:
                classified=frame[frame.cluster_id!=''].copy()
                if len(classified): classified.dissolve(by='entity_name' if classified.entity_name.ne('').all() else 'cluster_id',as_index=False).to_file(path,layer='entities',driver='GPKG')
            low=frame[(frame.visible_fraction>0)&(frame.confidence<0.4)]
            if len(low): low.to_file(path,layer='low_confidence',driver='GPKG')
        elif suffix in ('.geojson','.json'): frame.to_file(path,driver='GeoJSON')
        elif suffix=='.shp':
            short=frame.rename(columns={'province_id':'prov_id','entity_name':'entity','cluster_id':'cluster','confidence':'conf','visible_fraction':'vis_frac','source_image':'source'})
            short.to_file(path,driver='ESRI Shapefile')
        else: raise ValueError('Output must end in .gpkg, .geojson, or .shp')
    except Exception as exc: raise RuntimeError(f'Failed to export {path}: {exc}') from exc
    if qml: write_qml(path.with_suffix('.qml'))
    return frame
