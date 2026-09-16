import argparse, json, logging
from pathlib import Path
from PIL import Image
from paradox_mapper.games.eu4 import EU4Adapter
from paradox_mapper.map.cache import save_cache
from paradox_mapper.map.raster_loader import boundary_reference

def parser():
    p=argparse.ArgumentParser(prog='paradox-map',description='EU4 screenshot to GIS extraction tools'); p.add_argument('-v','--verbose',action='store_true')
    sub=p.add_subparsers(dest='command',required=True)
    imp=sub.add_parser('import-map',help='validate and polygonize EU4 map files'); imp.add_argument('raster'); imp.add_argument('definition'); imp.add_argument('output')
    ref=sub.add_parser('reference',help='generate province and boundary reference PNGs'); ref.add_argument('raster'); ref.add_argument('output_dir')
    gui=sub.add_parser('gui',help='launch desktop interface')
    return p

def main(argv=None):
    args=parser().parse_args(argv); logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    if args.command=='gui':
        from paradox_mapper.gui.app import main as gui_main; return gui_main()
    if args.command=='import-map':
        raster,definition,frame=EU4Adapter().import_map(args.raster,args.definition); save_cache(frame,args.output,args.raster)
        print(json.dumps({'provinces':len(frame),'warnings':definition.warnings,'cache':str(args.output)})); return 0
    if args.command=='reference':
        from paradox_mapper.map.raster_loader import load_province_raster
        raster=load_province_raster(args.raster); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
        Image.fromarray(raster).save(out/'province_colors.png'); Image.fromarray(boundary_reference(raster)).save(out/'boundaries.png'); return 0
if __name__=='__main__': raise SystemExit(main())
