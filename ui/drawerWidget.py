import os
from PyQt5.QtCore import QTimer,QSize,QRect,QMargins
import numpy as np
import pydicom
from PyQt5 import Qt
from PyQt5.QtWidgets import QFrame, QWidget
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from utils.util import getDicomWindowCenterAndLevel,getImageTileInfoFromDicom

class drawerWidget(QWidget):
    def __init__(self,parent,flags):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.timer = QTimer()
        self.scalingFactor
        mLength = self.width()
        minimumLength = 0
        maximumLength = mLength

        mIsBtn = False
        super().__init__(parent=parent, flags=flags)

    def showBtn(self):
        self.rect = QRect()
        self.rect.setX(100)  #弹出位置
        self.rect.setY(200)
        self.rect.setHeight(self.height())
        self.rect.setWidth(self.minimumLength)
        self.setGeometry(self.rect)
        self.show()
        self.minimumLength += self.scalingFactor
        if (self.minimumLength >= self.mLength):
            self.timer.stop()
        self.update()
