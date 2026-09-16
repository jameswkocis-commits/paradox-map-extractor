from paradox_mapper.models import ProvinceObservation

def observation_from_dict(data):
    d=dict(data); d['rgb']=tuple(d['rgb']); d['lab']=tuple(d['lab'])
    return ProvinceObservation(**d)
