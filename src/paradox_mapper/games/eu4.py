import logging
from paradox_mapper.games.base import GameAdapter
from paradox_mapper.map.definition_parser import parse_definition
from paradox_mapper.map.raster_loader import load_province_raster, validate_raster_colors
from paradox_mapper.map.polygonizer import polygonize_provinces
log=logging.getLogger(__name__)
class EU4Adapter(GameAdapter):
    def import_map(self, raster_path, definition_path):
        definition=parse_definition(definition_path); raster=load_province_raster(raster_path)
        missing=validate_raster_colors(raster, definition.rgb_to_id)
        if missing: log.warning("%d raster colors are absent from definition.csv: %s",len(missing),missing[:10])
        return raster, definition, polygonize_provinces(raster,definition.rgb_to_id)
    def metadata(self): return {"id":"eu4","name":"Europa Universalis IV","coordinate_system":"EU4 game-map coordinates"}
