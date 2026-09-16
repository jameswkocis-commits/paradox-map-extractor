from dataclasses import dataclass, field
from paradox_mapper.models import ControlPoint
@dataclass
class ControlPointSet:
    points: list[ControlPoint]=field(default_factory=list)
    def add(self,map_point,screen_point): self.points.append(ControlPoint(tuple(map_point),tuple(screen_point)))
    def undo(self):
        if self.points: return self.points.pop()
    def clear(self): self.points.clear()
