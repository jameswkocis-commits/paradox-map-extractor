from PIL import Image
import numpy as np
from paradox_mapper.extraction.visibility import visible_provinces
from paradox_mapper.extraction.color_sampling import sample_province
from paradox_mapper.extraction.clustering import cluster_observations

def analyze_screenshot(provinces,screenshot,matrix,erosion=2,cluster_eps=10):
    image=np.asarray(Image.open(screenshot).convert('RGB')) if not isinstance(screenshot,np.ndarray) else screenshot
    visible=visible_provinces(provinces,matrix,image.shape[1],image.shape[0])
    if not visible: raise ValueError("No provinces overlap the screenshot viewport")
    observations=[]
    for item in visible:
        try: observations.append(sample_province(image,item,erosion=erosion,source_image=str(screenshot) if not isinstance(screenshot,np.ndarray) else "array"))
        except ValueError: continue
    if not observations: raise ValueError("No visible provinces had a sampleable interior")
    cluster_observations(observations,eps=cluster_eps)
    return observations
