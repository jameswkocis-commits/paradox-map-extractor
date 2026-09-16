from PySide6.QtWidgets import QWidget,QVBoxLayout,QTableWidget,QTableWidgetItem,QHBoxLayout,QLineEdit,QPushButton,QLabel
from paradox_mapper.extraction.clustering import rename_cluster
class ReviewWidget(QWidget):
    def __init__(self):
        super().__init__(); self.observations=[]; self.table=QTableWidget(); self.name=QLineEdit(); self.name.setPlaceholderText('Entity name for selected cluster'); b=QPushButton('Rename cluster'); b.clicked.connect(self.rename)
        bar=QHBoxLayout(); bar.addWidget(QLabel('Selected cluster:')); bar.addWidget(self.name); bar.addWidget(b)
        layout=QVBoxLayout(self); layout.addLayout(bar); layout.addWidget(self.table)
    def set_observations(self,items): self.observations=items; self.refresh()
    def refresh(self):
        headers=['Province','RGB','Cluster','Entity','Confidence','Visible']; self.table.setColumnCount(len(headers)); self.table.setHorizontalHeaderLabels(headers); self.table.setRowCount(len(self.observations))
        for row,o in enumerate(self.observations):
            vals=[o.province_id,str(o.rgb),o.cluster_id,o.entity_name,f'{o.confidence:.2f}',f'{o.visible_fraction:.2f}']
            for col,val in enumerate(vals):self.table.setItem(row,col,QTableWidgetItem(str(val)))
    def rename(self):
        row=self.table.currentRow()
        if row>=0: rename_cluster(self.observations,self.observations[row].cluster_id,self.name.text()); self.refresh()
