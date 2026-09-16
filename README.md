# Paradox Map Extractor

Paradox Map Extractor is a local Python desktop and command-line application that turns an **Europa Universalis IV political-map screenshot** into GIS-ready province classifications. The game's province bitmap remains authoritative: the program polygonizes those known provinces, aligns them to a screenshot with user-supplied control points, robustly samples province interiors, clusters perceptually similar colors, and exports the **original province geometry** to GeoPackage, GeoJSON, or Shapefile.

> **MVP scope:** EU4, manual registration, political-color clustering, review/naming, and GIS export. It does not parse saves, recognize text/country tags, automatically geolocate screenshots, or support CK3/Imperator. No copyrighted assets are included; provide files from your own installation.

## Installation

Python 3.12 is recommended (3.10+ supported). Native GIS wheels are available on mainstream platforms.

```bash
git clone <this-repository>
cd paradox-map-extractor
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e '.[gui]'
```

For tests, use `python -m pip install -e '.[gui,dev]'`. If GeoPandas installation is difficult, a conda-forge environment containing `gdal rasterio geopandas pyogrio opencv scikit-learn pyside6` is a practical alternative.

## EU4 inputs

Copy (do not move or redistribute) these files from your own EU4 installation:

* `map/provinces.bmp`
* `map/definition.csv`

The installation is commonly under Steam's `steamapps/common/Europa Universalis IV`; modded maps use the equivalent files in the mod. The definition reader accepts semicolon-separated files, extra columns, blank lines, UTF-8, Windows-1252, and Latin-1. Unmapped raster colors are warnings; mapped provinces still import.

## Desktop workflow

Launch with either:

```bash
paradox-map-gui
# or
paradox-map gui
```

1. Select **Import EU4 Map**, then `provinces.bmp` and `definition.csv`.
2. Add a gameplay screenshot. A boundary reference appears beside it.
3. Click a recognizable point in the screenshot, then the corresponding location in the reference. Repeat at least four times, spread across the visible area. Zoom with the wheel and pan by dragging. Undo/clear if necessary.
4. Select **Calculate Registration**. Inspect the RMS pixel residual; a large residual usually means a mismatched or poorly distributed point.
5. Select **Analyze Screenshot**. Only projected provinces overlapping the screenshot are sampled. Borders are eroded, many interior pixels are used, and color outliers are rejected.
6. Review province ID, RGB, anonymous cluster, confidence, and visible fraction. Select a row, enter a country/entity label, and rename its cluster. Low confidence means a small visible area, few safe pixels, or substantial color dispersion.
7. Export `.gpkg` (recommended), `.geojson`, or `.shp`. A neighboring QGIS `.qml` starter style is generated.

The current GUI performs engine work synchronously; large first-time imports can pause it briefly. Use the CLI preprocessing command for very large maps.

## CLI

```bash
# Polygonize and cache a map as GeoPackage (cache metadata includes a source hash)
paradox-map import-map /path/provinces.bmp /path/definition.csv cache/eu4.gpkg

# Make both original-color and high-contrast boundary references
paradox-map reference /path/provinces.bmp references/

paradox-map --help
```

Registration/extraction are exposed as importable engine APIs (`registration`, `extraction.pipeline`) so reproducible scripts and future CLI subcommands do not depend on Qt.

## Coordinates and registration

Output has **no CRS**: it uses fictional EU4 game-map Cartesian coordinates and must never be treated as EPSG:4326. For an image of height `H`:

```text
GIS_X = image_x
GIS_Y = H - image_y
```

Pixel top-left therefore maps to `(0, H)` and the bottom-left map corner to `(0, 0)`. The GUI converts reference clicks to this coordinate convention before estimating the map-to-screen projective homography. Export always uses these original geometries—not screenshot-derived boundaries.

Four pairs determine a homography. With more pairs, OpenCV RANSAC rejects outliers. Choose coast corners or border intersections, avoid labels/icons, distribute points around the viewport, and do not place most points on one line.

## GIS/QGIS export

GeoPackage contains a `provinces` layer and, where available, dissolved `entities` and `low_confidence` layers. Province attributes include source province RGB, detected political RGB, cluster/entity, confidence, visible fraction, and source image. Drag the `.gpkg` into QGIS, choose `provinces`, and categorize by `entity_name` or `cluster_id`. The generated `.qml` is a minimal style scaffold; use the `red`, `green`, and `blue` fields to refine data-defined fill colors. GeoJSON contains one layer. Shapefile uses abbreviated field names due to its ten-character limitation.

Because the coordinates are a game grid, QGIS may prompt for a CRS: leave it unset. A future explicit georeferencing stage would be required to combine it with real-world datasets.

## Project files and multiple screenshots

The JSON project serializer stores paths (relative when possible), screenshots, control points, homographies, observations, cluster names, manual overrides, and extraction parameters without embedding rasters. The observation model supports several screenshots; confidence-based merging rewards agreement and flags strong high-confidence color conflicts. The initial GUI focuses on one screenshot at a time.

## Troubleshooting

* **No colors match:** confirm the bitmap and CSV come from the same vanilla version/mod and the file is an RGB province map.
* **Degenerate homography:** add four non-collinear pairs spread across the map; clear any accidental mismatches.
* **High registration residual:** replace questionable pairs and use stable geographic intersections.
* **No visible/sampleable provinces:** verify click direction (screenshot first, reference second), screenshot dimensions, and alignment; tiny slivers can legitimately have no safe interior.
* **Odd colors:** use a flat political map mode and hide overlays where possible. The median/outlier rejection handles labels and units, but cannot recover a province entirely covered by UI.
* **GeoPackage driver errors:** install GDAL/pyogrio-compatible GeoPandas wheels or use conda-forge.
* **Qt platform plugin errors on Linux:** install the distribution's common XCB libraries; the engine and CLI work without the GUI extra.

## Development

```bash
python -m pip install -e '.[dev]'
pytest -q
paradox-map import-map /path/to/provinces.bmp /path/to/definition.csv /tmp/eu4.gpkg
```

Tests generate synthetic assets and cover parsing/lookups, polygonization/islands, Y conversion, homography and inverse roundtrip, visibility/masks, robust sampling, LAB clustering/naming, cache, GeoPackage/GeoJSON, pipeline integration, and project roundtrips. They require no game content.

## Architecture

* `games`: adapter boundary and EU4 implementation
* `map`: tolerant definitions, raster/reference handling, polygonization, fingerprinted cache
* `registration`: control pairs, homographies, residual validation
* `extraction`: visibility, masks, robust LAB sampling, confidence, clustering
* `project`: JSON persistence and multi-observation merge
* `export`: GIS layers and QGIS style
* `gui`: thin PySide6 workflow over the independent engine

## Roadmap (not implemented)

Automatic coastline/edge registration and ORB/KAZE refinement; CK3 and Imperator adapters; save ownership; arbitrary map modes and culture/religion/development; historical snapshots; real-world georeferencing; and direct QGIS plugin integration. These extensions must continue to treat known game province geometry as authoritative.

## License and assets

The source is intended for local map-making workflows. Paradox Interactive game assets are not distributed. You are responsible for using files from your licensed installation consistently with applicable terms.
