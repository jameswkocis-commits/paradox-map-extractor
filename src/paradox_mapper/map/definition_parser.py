from __future__ import annotations
import csv
import logging
from pathlib import Path
from paradox_mapper.models import Definition
log = logging.getLogger(__name__)

_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")

def parse_definition(path: str | Path) -> Definition:
    path = Path(path)
    if not path.is_file(): raise FileNotFoundError(f"Definition file not found: {path}")
    text = None
    for encoding in _ENCODINGS:
        try: text = path.read_text(encoding=encoding); break
        except UnicodeDecodeError: continue
    if text is None: raise ValueError(f"Cannot decode definition file: {path}")
    rgb_to_id, id_to_rgb, warnings = {}, {}, []
    for line_no, row in enumerate(csv.reader(text.splitlines(), delimiter=";"), 1):
        if not row or not any(v.strip() for v in row): continue
        if len(row) < 4:
            warnings.append(f"line {line_no}: expected at least 4 columns"); continue
        try: pid, r, g, b = map(lambda x: int(x.strip()), row[:4])
        except ValueError:
            if line_no == 1: continue
            warnings.append(f"line {line_no}: invalid numeric fields"); continue
        if pid < 0 or any(not 0 <= v <= 255 for v in (r,g,b)):
            warnings.append(f"line {line_no}: values out of range"); continue
        rgb=(r,g,b)
        if rgb in rgb_to_id and rgb_to_id[rgb] != pid:
            warnings.append(f"line {line_no}: duplicate RGB {rgb}"); continue
        if pid in id_to_rgb and id_to_rgb[pid] != rgb:
            warnings.append(f"line {line_no}: duplicate province ID {pid}"); continue
        rgb_to_id[rgb]=pid; id_to_rgb[pid]=rgb
    if not id_to_rgb: raise ValueError(f"No valid province definitions in {path}")
    for warning in warnings: log.warning(warning)
    return Definition(rgb_to_id, id_to_rgb, warnings)
