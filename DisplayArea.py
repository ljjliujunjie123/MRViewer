from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QMouseEvent, QIcon
from DataBaseDisplayer import DataBaseDisplayer
from ImageDisplayer import ImageDisplayer
    
class DisplayArea(QFrame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.stackedLayout = QStackedLayout()
        self.setLayout(self.stackedLayout)

        self.dataBaseDisplayer = DataBaseDisplayer()
        self.imageDisplayer = ImageDisplayer()
        self.stackedLayout.addWidget(self.dataBaseDisplayer)
        self.stackedLayout.addWidget(self.imageDisplayer)

    def ShiftToDatabase(self):
        self.stackedLayout.setCurrentIndex(0)
    
    def ShiftToImage(self):
        self.stackedLayout.setCurrentIndex(1)