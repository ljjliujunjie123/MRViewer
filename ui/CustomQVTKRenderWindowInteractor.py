from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
from PyQt5.QtCore import QPoint

class CustomQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):

    def __init__(self, parent = None):
        QVTKRenderWindowInteractor.__init__(self, parent)
        self._TimeDuration = 500

    def wheelEvent(self, ev):
        return

    def CreateTimer(self, obj, event):
       self._Timer.start(self._TimeDuration) # self._Timer.start(10) in orginal

    def CreateRepeatingTimer(self, duration):
    #    self._TimerDuration = duration
       super(CustomQVTKRenderWindowInteractor, self).GetRenderWindow().GetInteractor().CreateRepeatingTimer(duration)
       self._TimeDuration = duration