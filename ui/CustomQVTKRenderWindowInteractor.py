from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
from PyQt5.QtCore import QPoint

class CustomQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):

    def __init__(self, parent = None):
        QVTKRenderWindowInteractor.__init__(self, parent)

        # self.crossView = CustomCrossBoxWidget()
        # self.crossView.setParent(self)
        # self.crossView.setGeometry(200,200,100,100)
        # self.crossViewLastPos = QPoint(250,250)

    def wheelEvent(self, ev):
        return

    # def mousePressEvent(self, ev):
    #     if self.crossView.underMouse():
    #         pos = ev.pos()
    #         if self.crossViewLastPos != pos:
    #             colDelta, rowDelta = pos.x() - self.crossViewLastPos.x(), pos.y() - self.crossViewLastPos.y()
    #             self.crossView.setGeometry(
    #                 self.crossView.geometry().x() + colDelta,
    #                 self.crossView.geometry().y() + rowDelta,
    #                 self.crossView.width(),
    #                 self.crossView.height()
    #             )
    #             self.crossViewLastPos = pos
    #     super().mousePressEvent(ev)