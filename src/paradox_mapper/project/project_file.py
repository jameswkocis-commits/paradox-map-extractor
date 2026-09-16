from __future__ import annotations
import json
from pathlib import Path
from paradox_mapper.models import ControlPoint, ProvinceObservation
from paradox_mapper.project.observations import observation_from_dict

def _relative(value,base):
    if not value:return value
    p=Path(value)
    try:return str(p.resolve().relative_to(base.resolve()))
    except ValueError:return str(p)
def _resolved(value,base):
    if not value:return value
    p=Path(value); return str((base/p).resolve()) if not p.is_absolute() else str(p)

def save_project(path,project):
    path=Path(path); base=path.parent
    data=dict(project)
    for key in ('province_raster','definition_csv','cached_vector'):
        if key in data:data[key]=_relative(data[key],base)
    data['screenshots']=[]
    for shot in project.get('screenshots',[]):
        item=dict(shot); item['path']=_relative(item.get('path',''),base)
        item['control_points']=[{'map_point':list(p.map_point),'screen_point':list(p.screen_point)} if isinstance(p,ControlPoint) else p for p in item.get('control_points',[])]
        if hasattr(item.get('homography'),'tolist'): item['homography']=item['homography'].tolist()
        data['screenshots'].append(item)
    data['observations']=[o.to_dict() if isinstance(o,ProvinceObservation) else o for o in project.get('observations',[])]
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2),encoding='utf8')
def load_project(path):
    path=Path(path); data=json.loads(path.read_text(encoding='utf8')); base=path.parent
    for key in ('province_raster','definition_csv','cached_vector'):
        if key in data:data[key]=_resolved(data[key],base)
    for shot in data.get('screenshots',[]):
        shot['path']=_resolved(shot.get('path',''),base)
        shot['control_points']=[ControlPoint(tuple(p['map_point']),tuple(p['screen_point'])) for p in shot.get('control_points',[])]
    data['observations']=[observation_from_dict(o) for o in data.get('observations',[])]
    return data
