from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QFileDialog,QTabWidget,QMessageBox,QProgressDialog
from PySide6.QtCore import Qt
from paradox_mapper.games.eu4 import EU4Adapter
from paradox_mapper.map.raster_loader import boundary_reference
from paradox_mapper.extraction.pipeline import analyze_screenshot
from paradox_mapper.export.gis import export_results
from paradox_mapper.project.project_file import save_project, load_project
from paradox_mapper.gui.registration_widget import RegistrationWidget
from paradox_mapper.gui.review_widget import ReviewWidget
from paradox_mapper.gui.export_widget import ExportWidget
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Paradox Map Extractor — EU4'); self.resize(1200,800); self.provinces=None; self.raster_path=''; self.definition_path=''; self.screenshot=''; self.h=None; self.observations=[]
        root=QWidget(); layout=QVBoxLayout(root); controls=QHBoxLayout()
        for text,fn in [('Import EU4 Map',self.import_map),('Add Screenshot',self.add_screenshot),('Save Project',self.save),('Load Project',self.load),('Analyze Screenshot',self.analyze)]:
            b=QPushButton(text); b.clicked.connect(fn); controls.addWidget(b)
        layout.addLayout(controls); self.tabs=QTabWidget(); self.registration=RegistrationWidget(); self.registration.registrationReady.connect(lambda h:setattr(self,'h',h)); self.review=ReviewWidget(); self.exporter=ExportWidget(self.export)
        self.tabs.addTab(self.registration,'1. Registration'); self.tabs.addTab(self.review,'2. Review'); self.tabs.addTab(self.exporter,'3. Export'); layout.addWidget(self.tabs); self.setCentralWidget(root)
    def import_map(self):
        raster,_=QFileDialog.getOpenFileName(self,'Select provinces.bmp','','Bitmap (*.bmp *.png)');
        if not raster:return
        definition,_=QFileDialog.getOpenFileName(self,'Select definition.csv','','CSV (*.csv)');
        if not definition:return
        try:
            arr,_,self.provinces=EU4Adapter().import_map(raster,definition); self.raster_path=raster; self.definition_path=definition; ref=Path.home()/'.cache/paradox-map-extractor/reference.png'; ref.parent.mkdir(parents=True,exist_ok=True); Image.fromarray(boundary_reference(arr)).save(ref); self.registration.reference.set_image(ref)
        except Exception as e:QMessageBox.critical(self,'Import failed',str(e))
    def add_screenshot(self):
        path,_=QFileDialog.getOpenFileName(self,'Select gameplay screenshot','','Images (*.png *.jpg *.jpeg *.bmp)')
        if path:self.screenshot=path; self.registration.screen.set_image(path)
    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save project', '', 'Paradox project (*.json)')
        if not path:
            return
        shot = {'path': self.screenshot, 'control_points': self.registration.points, 'homography': self.h}
        save_project(path, {'province_raster': self.raster_path, 'definition_csv': self.definition_path,
                            'cached_vector': '', 'screenshots': [shot] if self.screenshot else [],
                            'observations': self.observations, 'cluster_names': {},
                            'manual_overrides': {}, 'extraction_parameters': {'erosion': 2}})
    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load project', '', 'Paradox project (*.json)')
        if not path:
            return
        try:
            project = load_project(path)
            self.raster_path = project.get('province_raster', '')
            self.definition_path = project.get('definition_csv', '')
            if self.raster_path and self.definition_path:
                arr, _, self.provinces = EU4Adapter().import_map(self.raster_path, self.definition_path)
                ref = Path.home()/'.cache/paradox-map-extractor/reference.png'
                ref.parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray(boundary_reference(arr)).save(ref)
                self.registration.reference.set_image(ref)
            shots = project.get('screenshots', [])
            if shots:
                self.screenshot = shots[0]['path']; self.registration.screen.set_image(self.screenshot)
                self.registration.points = shots[0].get('control_points', [])
                if shots[0].get('homography') is not None:
                    import numpy as np
                    self.h = np.asarray(shots[0]['homography'], dtype=float)
            self.observations = project.get('observations', []); self.review.set_observations(self.observations)
        except Exception as e:
            QMessageBox.critical(self, 'Load failed', str(e))
    def analyze(self):
        if self.provinces is None or not self.screenshot or self.h is None: QMessageBox.warning(self,'Not ready','Import a map, add a screenshot, and calculate registration first.'); return
        try:self.observations=analyze_screenshot(self.provinces,self.screenshot,self.h); self.review.set_observations(self.observations); self.tabs.setCurrentWidget(self.review)
        except Exception as e:QMessageBox.critical(self,'Analysis failed',str(e))
    def export(self,path):
        if not path or self.provinces is None:return
        try:export_results(self.provinces,self.observations,path); QMessageBox.information(self,'Export complete',path)
        except Exception as e:QMessageBox.critical(self,'Export failed',str(e))
