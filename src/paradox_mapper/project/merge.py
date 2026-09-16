from collections import defaultdict
import numpy as np

def merge_observations(observations,color_conflict_distance=20.0):
    grouped=defaultdict(list)
    for obs in observations:
        if not obs.excluded: grouped[obs.province_id].append(obs)
    merged={}
    for pid,items in grouped.items():
        winner=max(items,key=lambda x:x.confidence)
        if len(items)>1:
            labs=np.asarray([x.lab for x in items]); conflicts=np.max(np.linalg.norm(labs-labs[0],axis=1))>color_conflict_distance
            winner.conflict=bool(conflicts and sum(x.confidence>=.6 for x in items)>1)
            if not winner.conflict: winner.confidence=min(1.0,winner.confidence+0.1*(len(items)-1))
        merged[pid]=winner
    return merged
