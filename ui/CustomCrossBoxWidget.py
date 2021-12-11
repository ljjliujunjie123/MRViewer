from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

class CustomCrossBoxWidget(QWidget):

    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool |Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground,True)
        self.qp = QPainter()

    def paintEvent(self, ev):
        self.qp.begin(self)
        self.qp.setPen(QPen(Qt.red,10,Qt.SolidLine))
        self.qp.drawRect(0,0,self.width(),self.height())
        self.qp.end()
