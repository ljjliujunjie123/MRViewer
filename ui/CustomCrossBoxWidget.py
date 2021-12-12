from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

class CustomCrossBoxWidget(QWidget):

    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool |Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground,True)
        self.qp = QPainter()
        self.isShowContent = False
        self.pos1 = None
        self.pos2 = None

    def setPos(self,pos1,pos2):
        self.pos1,self.pos2=pos1,pos2

    def paintEvent(self, ev):
        print("crossView paint ",self.pos1,self.pos2)
        self.qp.begin(self)
        self.qp.setPen(QPen(Qt.red,10,Qt.SolidLine))
        # self.qp.drawRect(0,0,self.width(),self.height())
        if self.isShowContent:
            self.qp.drawLine(self.pos1,self.pos2)
        self.qp.end()
