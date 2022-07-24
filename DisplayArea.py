from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QMouseEvent, QIcon
from DataBaseDisplayer import DataBaseDisplayer
from ImageDisplayer import PreImageDisplayer#, IntraImageDisplayer
from Model.ImagesDataModel import ImagesDataModel
from enum import IntEnum

# Image mode selection
class ImageMode(IntEnum):
    pre = 1
    intra = 2
    # post = 3


class DisplayArea(QFrame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.stackedLayout = QStackedLayout()
        self.setLayout(self.stackedLayout)

        self.currentMode = ImageMode.pre
        self.dataBaseDisplayer = DataBaseDisplayer(self)
        self.preImageDisplayer = PreImageDisplayer(self)
        # self.intraImageDisplayer = IntraImageDisplayer(self)
        self.stackedLayout.addWidget(self.dataBaseDisplayer)
        self.stackedLayout.addWidget(self.preImageDisplayer)
        # self.stackedLayout.addWidget(self.intraImageDisplayer)


        self.ShiftToDatabase()
        self.ShiftToImage()

    def ShiftToDatabase(self):
        self.stackedLayout.setCurrentIndex(0)
    
    def ShiftToImage(self):
        self.stackedLayout.setCurrentIndex(1)
        if self.currentMode==ImageMode.pre:
            self.preImageDisplayer.imageShownLayoutController.reAddInPool()
        if self.currentMode==ImageMode.intra:
            self.preImageDisplayer.imageShownLayoutController.switchToIntra()
            

    def setCurrentMode(self,imageMode):
        print("shift image mode to",int(imageMode))
        self.currentMode = imageMode
        self.ShiftToImage()
