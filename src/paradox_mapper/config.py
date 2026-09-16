from dataclasses import dataclass

@dataclass(slots=True)
class ExtractionConfig:
    erosion_pixels: float = 2.0
    max_samples: int = 5000
    min_pixels: int = 9
    cluster_eps: float = 10.0
    low_confidence: float = 0.4
