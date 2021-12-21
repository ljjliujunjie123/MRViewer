from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt,QEvent

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

    #防止CrossBox遮挡其他应用窗口
    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a1.type() == QEvent.Type.WindowDeactivate and self.isShowContent:
            self.hide()
            #print("hide the red line")
        elif a1.type() == QEvent.Type.WindowActivate and self.isShowContent:
            self.show()
        #print("eventFilter ")
        #print(a1.type())
        return super().eventFilter(a0, a1)