from PySide6.QtCore import Signal, Qt, QPointF
from PySide6.QtGui import QPixmap, QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsView,QGraphicsScene
class ImageViewer(QGraphicsView):
    pointClicked=Signal(float,float)
    def __init__(self):
        super().__init__(); self.setScene(QGraphicsScene(self)); self.setDragMode(self.ScrollHandDrag); self._points=[]; self._pix=None; self.image_height=0
    def set_image(self,path):
        pix=QPixmap(str(path));
        if pix.isNull(): raise ValueError(f'Unable to read image: {path}')
        self.scene().clear(); self.image_height=pix.height(); self._pix=self.scene().addPixmap(pix); self._points=[]; self.reset_view()
    def reset_view(self):
        if self._pix:self.fitInView(self._pix,Qt.KeepAspectRatio)
    def wheelEvent(self,event):
        self.scale(1.2 if event.angleDelta().y()>0 else 1/1.2,1.2 if event.angleDelta().y()>0 else 1/1.2)
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton and self._pix:
            p=self.mapToScene(event.position().toPoint()); self.pointClicked.emit(p.x(),p.y()); return
        super().mousePressEvent(event)
    def add_point(self,x,y,label=''):
        r=4; self.scene().addEllipse(x-r,y-r,2*r,2*r,QPen(QColor('yellow'),2),QBrush(QColor('red'))); self._points.append((x,y))
