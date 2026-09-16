import numpy as np
from sklearn.cluster import DBSCAN

def cluster_observations(observations,eps=10.0,min_samples=1):
    if not observations: return {}
    labels=DBSCAN(eps=eps,min_samples=min_samples).fit_predict(np.asarray([o.lab for o in observations]))
    # Stable anonymous IDs ordered by first occurrence; DBSCAN noise gets its own cluster.
    mapping={}; next_id=1
    for obs,label in zip(observations,labels):
        key=("noise",obs.province_id) if label<0 else ("label",int(label))
        if key not in mapping: mapping[key]=f"cluster_{next_id:03d}"; next_id+=1
        obs.cluster_id=mapping[key]
    return {o.province_id:o.cluster_id for o in observations}

def rename_cluster(observations,cluster_id,name):
    for obs in observations:
        if obs.cluster_id==cluster_id: obs.entity_name=name.strip()
