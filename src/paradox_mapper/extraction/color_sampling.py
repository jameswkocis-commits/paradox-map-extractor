import cv2
import numpy as np
from paradox_mapper.models import ProvinceObservation
from paradox_mapper.extraction.masks import geometry_mask
from paradox_mapper.extraction.confidence import observation_confidence

def rgb_to_lab(rgb):
    arr=np.asarray(rgb,np.uint8).reshape(1,1,3)
    lab=cv2.cvtColor(arr,cv2.COLOR_RGB2LAB).reshape(3).astype(float)
    return (lab[0]*100/255, lab[1]-128, lab[2]-128)

def sample_province(image, visible, erosion=2, max_samples=5000, source_image=""):
    h,w=image.shape[:2]; mask=geometry_mask(visible.screen_geometry,w,h,erosion)
    pixels=np.asarray(image,dtype=np.uint8)[mask]
    if len(pixels)==0: raise ValueError(f"Province {visible.province_id} has no sampleable interior pixels")
    if len(pixels)>max_samples:
        idx=np.linspace(0,len(pixels)-1,max_samples,dtype=int); pixels=pixels[idx]
    median=np.median(pixels,axis=0)
    distances=np.linalg.norm(pixels.astype(float)-median,axis=1)
    cutoff=np.percentile(distances,85)
    kept=pixels[distances<=cutoff] if len(pixels)>6 else pixels
    representative=np.rint(np.median(kept,axis=0)).clip(0,255).astype(int)
    dispersion=float(np.median(np.linalg.norm(kept.astype(float)-representative,axis=1)))
    rgb=tuple(map(int,representative)); lab=rgb_to_lab(rgb)
    confidence=observation_confidence(len(kept),dispersion,visible.visible_fraction)
    return ProvinceObservation(visible.province_id,rgb,lab,len(kept),dispersion,visible.visible_fraction,confidence,source_image)
