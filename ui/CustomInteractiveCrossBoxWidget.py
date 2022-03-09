from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPen,QPainter
from PyQt5.QtCore import QRectF,Qt
from ui.mGraphicRectItem import mGraphicParallelogramItem, mGraphicParallelogramParams

class CustomInteractiveCrossBoxWidget(QGraphicsView):

    def __init__(self,
        interactiveSubSignal,
        parent = None
    ):
        QGraphicsView.__init__(self, parent)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground,True)
        self.setStyleSheet("background:transparent;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.painter = QPainter(self)

        sceneRect = self.calcSceneRect()
        self.scene = QGraphicsScene(sceneRect)
        self.setScene(self.scene)

        #将border View和CrossView组装入scene
        params = mGraphicParallelogramParams()
        params.setTopLeftPoint((-239,-137))
        params.setTopRightPoint((290,89))
        params.setBottomLeftPoint((-120,230))
        params.setBottomRightPoint((400,220))
        self.crossBoxItem = mGraphicParallelogramItem(params, interactiveSubSignal)
        self.scene.addItem(self.crossBoxItem)
        self.borderItem = QGraphicsRectItem(sceneRect)
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setWidth(10)
        self.borderItem.setPen(pen)
        self.scene.addItem(self.borderItem)

    def calcSceneRect(self):
        width,height = self.width(),self.height()
        return QRectF(-1*width/2,-1*height/2,width,height)

    def getCustomICrossBoxParams(self):
        return self.crossBoxItem.getGraphicParallelogramParams()

    def updateCrossBoxItem(self, params: mGraphicParallelogramParams):
        self.crossBoxItem.updateWithParams(params)

    def resizeEvent(self, QResizeEvent):
        self.scene.setSceneRect(self.calcSceneRect())
        self.borderItem.setRect(self.calcSceneRect())
        self.scene.update()