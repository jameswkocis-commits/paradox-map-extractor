from pathlib import Path
import hashlib, json
import geopandas as gpd

def source_fingerprint(path: str | Path) -> dict:
    p=Path(path); stat=p.stat()
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return {"size":stat.st_size,"mtime_ns":stat.st_mtime_ns,"sha256":h.hexdigest()}

def save_cache(frame: gpd.GeoDataFrame, cache_path: str | Path, raster_path: str | Path) -> None:
    p=Path(cache_path); p.parent.mkdir(parents=True,exist_ok=True)
    frame.to_file(p, layer="provinces", driver="GPKG")
    p.with_suffix(p.suffix+".json").write_text(json.dumps(source_fingerprint(raster_path)),encoding="utf8")

def load_cache(cache_path: str | Path, raster_path: str | Path) -> gpd.GeoDataFrame | None:
    p=Path(cache_path); meta=p.with_suffix(p.suffix+".json")
    if not p.exists() or not meta.exists(): return None
    if json.loads(meta.read_text()) != source_fingerprint(raster_path): return None
    return gpd.read_file(p, layer="provinces")
