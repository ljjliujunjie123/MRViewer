from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPen,QPainter
from PyQt5.QtCore import QRectF,Qt
from ui.mGraphicCrossBoxItem import mGraphicParallelogramItem, mGraphicParallelogramParams, mGraphicRectItem

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
        self.crossBoxProjectionItem = mGraphicParallelogramItem(params, interactiveSubSignal)
        self.crossBoxProjectionItem.hide()
        self.scene.addItem(self.crossBoxProjectionItem)

        self.crossBoxProjectionOrthonormalItem = mGraphicRectItem(params, interactiveSubSignal)
        self.crossBoxProjectionOrthonormalItem.hide()
        self.scene.addItem(self.crossBoxProjectionOrthonormalItem)

        pen = QPen()
        pen.setColor(Qt.yellow)
        pen.setWidth(5)

        self.crossBoxIntersectionItem = QGraphicsLineItem()
        self.crossBoxIntersectionItem.setPen(pen)
        self.crossBoxIntersectionItem.hide()
        self.scene.addItem(self.crossBoxIntersectionItem)

        self.borderItem = QGraphicsRectItem(sceneRect)
        self.borderItem.setPen(pen)
        self.scene.addItem(self.borderItem)

    def calcSceneRect(self):
        width,height = self.width(),self.height()
        return QRectF(-1*width/2,-1*height/2,width,height)

    def getCustomICrossBoxParams(self):
        return self.crossBoxProjectionItem.getGraphicParallelogramParams()

    def hideCrossBoxItems(self):
        self.crossBoxIntersectionItem.hide()
        self.crossBoxProjectionItem.hide()
        self.crossBoxProjectionOrthonormalItem.hide()

    def updateProjectionCrossBoxItem(self, params: mGraphicParallelogramParams):
        self.hideCrossBoxItems()
        self.crossBoxProjectionItem.updateWithParams(params)

    def updateInterscetionCrossBoxItem(self, startPoint, endPoint):
        self.hideCrossBoxItems()
        self.crossBoxIntersectionItem.setLine(startPoint.x(), startPoint.y(), endPoint.x(), endPoint.y())
        self.scene.update()
        self.crossBoxIntersectionItem.show()

    def updateProjectionOrthonormalCrossBoxItem(self, params: mGraphicParallelogramParams):
        self.hideCrossBoxItems()
        self.crossBoxProjectionOrthonormalItem.updateWithParams(params)

    def resizeEvent(self, QResizeEvent):
        self.scene.setSceneRect(self.calcSceneRect())
        self.borderItem.setRect(self.calcSceneRect())
        self.scene.update()