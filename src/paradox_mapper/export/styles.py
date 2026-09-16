from pathlib import Path
def write_qml(path,field='cluster_id'):
    content=f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'><qgis version="3"><renderer-v2 type="categorizedSymbol" attr="{field}"/></qgis>'''
    Path(path).write_text(content,encoding='utf8')
