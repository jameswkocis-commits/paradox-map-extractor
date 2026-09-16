from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError

def load_province_raster(path: str | Path) -> np.ndarray:
    try:
        with Image.open(path) as image: return np.asarray(image.convert("RGB"), dtype=np.uint8)
    except (FileNotFoundError, UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"Unable to read province raster {path}: {exc}") from exc

def validate_raster_colors(raster: np.ndarray, rgb_to_id: dict, background=((0,0,0),)) -> list[tuple[int,int,int]]:
    colors = {tuple(map(int, x)) for x in np.unique(raster.reshape(-1,3), axis=0)}
    return sorted(colors - set(rgb_to_id) - set(background))

def boundary_reference(raster: np.ndarray) -> np.ndarray:
    edge=np.zeros(raster.shape[:2], bool)
    edge[1:] |= np.any(raster[1:] != raster[:-1], axis=2)
    edge[:,1:] |= np.any(raster[:,1:] != raster[:,:-1], axis=2)
    out=np.full_like(raster, 235); out[edge]=(25,25,25)
    return out
