from __future__ import annotations

import atexit
import base64
import io
import secrets
import shutil
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file, session
from PIL import Image

from paradox_mapper.extraction.pipeline import analyze_screenshot
from paradox_mapper.export.gis import export_results
from paradox_mapper.games.eu4 import EU4Adapter
from paradox_mapper.map.raster_loader import boundary_reference
from paradox_mapper.models import ControlPoint
from paradox_mapper.registration.transforms import calculate_homography

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}
_work_root = Path(tempfile.mkdtemp(prefix="paradox-map-web-"))
_states: dict[str, dict] = {}
atexit.register(lambda: shutil.rmtree(_work_root, ignore_errors=True))


def _state() -> dict:
    token = session.get("workspace")
    if not token:
        token = secrets.token_urlsafe(18)
        session["workspace"] = token
    return _states.setdefault(token, {})


def _save_upload(upload, destination: Path, extensions: set[str]) -> None:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in extensions:
        raise ValueError(f"Unsupported file type: {suffix or 'none'}")
    upload.save(destination)


def _data_url(array) -> str:
    output = io.BytesIO()
    Image.fromarray(array).save(output, "PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(SECRET_KEY=secrets.token_hex(32), MAX_CONTENT_LENGTH=100 * 1024 * 1024)
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/assets")
    def assets():
        try:
            files = {name: request.files.get(name) for name in ("raster", "definition", "screenshot")}
            if not all(files.values()):
                raise ValueError("Choose a province raster, definition CSV, and screenshot.")
            token = session.get("workspace") or secrets.token_urlsafe(18)
            session["workspace"] = token
            folder = _work_root / token
            shutil.rmtree(folder, ignore_errors=True)
            folder.mkdir(parents=True)
            raster_path, definition_path, screenshot_path = folder / "provinces.bmp", folder / "definition.csv", folder / "screenshot.png"
            _save_upload(files["raster"], raster_path, {".bmp", ".png"})
            _save_upload(files["definition"], definition_path, {".csv"})
            _save_upload(files["screenshot"], screenshot_path, IMAGE_EXTENSIONS)
            raster, definition, provinces = EU4Adapter().import_map(raster_path, definition_path)
            with Image.open(screenshot_path) as shot:
                screenshot_size = list(shot.size)
            _states[token] = {"folder": folder, "provinces": provinces, "screenshot": screenshot_path,
                              "map_height": int(raster.shape[0]), "observations": None}
            return jsonify(reference=_data_url(boundary_reference(raster)), reference_size=[int(raster.shape[1]), int(raster.shape[0])],
                           screenshot_size=screenshot_size, provinces=len(provinces), warnings=definition.warnings)
        except Exception as exc:
            return jsonify(error=str(exc)), 400

    @app.post("/api/analyze")
    def analyze():
        try:
            state = _state()
            if "provinces" not in state:
                raise ValueError("Upload the three input files first.")
            pairs = (request.get_json(silent=True) or {}).get("points", [])
            height = state["map_height"]
            points = [ControlPoint((float(p["map"][0]), height - float(p["map"][1])),
                                   (float(p["screen"][0]), float(p["screen"][1]))) for p in pairs]
            matrix, errors, inliers = calculate_homography(points)
            observations = analyze_screenshot(state["provinces"], state["screenshot"], matrix)
            state["observations"] = observations
            return jsonify(observations=[o.to_dict() for o in observations],
                           rms=float((errors ** 2).mean() ** .5), inliers=int(inliers.sum()))
        except Exception as exc:
            return jsonify(error=str(exc)), 400

    @app.get("/api/download")
    def download():
        try:
            state = _state()
            if not state.get("observations"):
                raise ValueError("Analyze a screenshot before downloading.")
            output = state["folder"] / "extracted-map.geojson"
            export_results(state["provinces"], state["observations"], output, qml=False)
            return send_file(output, as_attachment=True, download_name="extracted-map.geojson")
        except Exception as exc:
            return jsonify(error=str(exc)), 400

    return app


def main(host: str = "127.0.0.1", port: int = 5000) -> None:
    create_app().run(host=host, port=port)


if __name__ == "__main__":
    main()
