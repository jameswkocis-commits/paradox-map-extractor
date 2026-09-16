from PySide6.QtWidgets import QWidget,QHBoxLayout,QLineEdit,QPushButton,QFileDialog
class ExportWidget(QWidget):
    def __init__(self,callback):
        super().__init__(); self.path=QLineEdit(); self.path.setPlaceholderText('campaign_map.gpkg'); browse=QPushButton('Browse'); browse.clicked.connect(self.browse); export=QPushButton('Export'); export.clicked.connect(lambda:callback(self.path.text()))
        layout=QHBoxLayout(self); layout.addWidget(self.path); layout.addWidget(browse); layout.addWidget(export)
    def browse(self):
        path,_=QFileDialog.getSaveFileName(self,'Export GIS','','GeoPackage (*.gpkg);;GeoJSON (*.geojson);;Shapefile (*.shp)')
        if path:self.path.setText(path)
