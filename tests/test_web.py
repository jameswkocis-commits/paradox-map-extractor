import io

import numpy as np
from PIL import Image

from paradox_mapper.web.app import create_app


def _image_bytes(array, format="PNG"):
    output = io.BytesIO()
    Image.fromarray(array).save(output, format)
    return output.getvalue()


def test_web_workflow_upload_analyze_and_download():
    app = create_app({"TESTING": True, "SECRET_KEY": "test"})
    client = app.test_client()
    assert client.get("/").status_code == 200

    raster = np.zeros((20, 40, 3), np.uint8)
    raster[:, :20] = (10, 20, 30)
    raster[:, 20:] = (40, 50, 60)
    screenshot = np.zeros_like(raster)
    screenshot[:, :20] = (160, 30, 30)
    screenshot[:, 20:] = (30, 30, 160)
    response = client.post("/api/assets", data={
        "raster": (io.BytesIO(_image_bytes(raster, "BMP")), "provinces.bmp"),
        "definition": (io.BytesIO(b"1;10;20;30\n2;40;50;60\n"), "definition.csv"),
        "screenshot": (io.BytesIO(_image_bytes(screenshot)), "screenshot.png"),
    })
    assert response.status_code == 200
    assert response.json["provinces"] == 2
    assert response.json["reference"].startswith("data:image/png;base64,")

    response = client.post("/api/analyze", json={"points": [
        {"map": [0, 0], "screen": [0, 0]},
        {"map": [40, 0], "screen": [40, 0]},
        {"map": [40, 20], "screen": [40, 20]},
        {"map": [0, 20], "screen": [0, 20]},
    ]})
    assert response.status_code == 200
    assert len(response.json["observations"]) == 2
    assert response.json["rms"] < 1e-5

    download = client.get("/api/download")
    assert download.status_code == 200
    assert download.headers["Content-Disposition"].endswith("extracted-map.geojson")


def test_web_reports_incomplete_upload():
    client = create_app({"TESTING": True}).test_client()
    response = client.post("/api/assets", data={})
    assert response.status_code == 400
    assert "Choose" in response.json["error"]
