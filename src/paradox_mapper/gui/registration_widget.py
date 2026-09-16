from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QPushButton,QLabel
from paradox_mapper.gui.image_viewer import ImageViewer
from paradox_mapper.models import ControlPoint
from paradox_mapper.registration.transforms import calculate_homography
from paradox_mapper.registration.validation import registration_quality
class RegistrationWidget(QWidget):
    registrationReady=Signal(object)
    def __init__(self):
        super().__init__(); self.screen=ImageViewer(); self.reference=ImageViewer(); self.points=[]; self.pending=None
        views=QHBoxLayout(); views.addWidget(self.screen); views.addWidget(self.reference)
        self.status=QLabel('Click screenshot, then corresponding reference point (minimum 4 pairs).')
        buttons=QHBoxLayout();
        for text,fn in [('Undo',self.undo),('Clear',self.clear),('Calculate Registration',self.calculate)]:
            b=QPushButton(text); b.clicked.connect(fn); buttons.addWidget(b)
        layout=QVBoxLayout(self); layout.addLayout(views); layout.addWidget(self.status); layout.addLayout(buttons)
        self.screen.pointClicked.connect(self._screen_point); self.reference.pointClicked.connect(self._map_point)
    def _screen_point(self,x,y): self.pending=(x,y); self.screen.add_point(x,y); self.status.setText('Now click the matching point on the reference map.')
    def _map_point(self,x,y):
        if self.pending is None:return
        self.reference.add_point(x,y); self.points.append(ControlPoint((x,self.reference.image_height-y),self.pending)); self.pending=None; self.status.setText(f'{len(self.points)} correspondence(s)')
    def undo(self):
        if self.points:self.points.pop()
        self.status.setText(f'{len(self.points)} correspondence(s); reload images to clear drawn marker.')
    def clear(self): self.points.clear(); self.pending=None; self.status.setText('Correspondences cleared; reload images to clear markers.')
    def calculate(self):
        try:
            h,errors,_=calculate_homography(self.points); quality=registration_quality(errors); self.status.setText(f"RMS residual {quality['rms_error']:.2f}px"+(' — poor registration' if quality['poor'] else '')); self.registrationReady.emit(h)
        except ValueError as e:self.status.setText(str(e))
