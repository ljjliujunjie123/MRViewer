from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QPointF,QRectF,QLineF
from PyQt5.QtGui import QPen,QPolygonF,QBrush,QColor
from math import sin,cos,pi,sqrt
from enum import Enum
from functools import singledispatch
from utils.InteractiveType import InteractiveType

class STATE_FLAG(Enum):
    DEFAULT_FLAG=0
    MOV_LEFT_LINE=1 #标记当前为用户按下矩形的左边界区域
    MOV_TOP_LINE=2 #标记当前为用户按下矩形的上边界区域
    MOV_RIGHT_LINE=3 #标记当前为用户按下矩形的右边界区域
    MOV_BOTTOM_LINE=4 #标记当前为用户按下矩形的下边界区域
    MOV_RECT=6 #标记当前为鼠标拖动图片移动状态
    ROTATE=7 #标记当前为旋转状态
    MOV_TOP_LEFT_POINT = 8
    MOV_TOP_RIGHT_POINT = 9
    MOV_BOTTOM_LEFT_POINT = 10
    MOV_BOTTOM_RIGHT_POINT = 11

class mGraphicParallelogramParams():

    UnDefined = -1

    def __init__(self):
        self.keyPointTopLeft = self.UnDefined
        self.keyPointTopRight = self.UnDefined
        self.keyPointBottomLeft= self.UnDefined
        self.keyPointBottomRight = self.UnDefined

    def setTopLeftPoint(self, obj):
        @singledispatch
        def setPoint(obj):
            return NotImplemented

        @setPoint.register(tuple)
        def _(obj):
            x,y = obj
            self.keyPointTopLeft = QPointF(x,y)

        @setPoint.register(QPointF)
        def _(obj):
            self.keyPointTopLeft = obj

        setPoint(obj)

    def setTopRightPoint(self, obj):
        @singledispatch
        def setPoint(obj):
            return NotImplemented

        @setPoint.register(tuple)
        def _(obj):
            x,y = obj
            self.keyPointTopRight = QPointF(x,y)

        @setPoint.register(QPointF)
        def _(obj):
            self.keyPointTopRight = obj

        setPoint(obj)

    def setBottomLeftPoint(self, obj):
        @singledispatch
        def setPoint(obj):
            return NotImplemented

        @setPoint.register(tuple)
        def _(obj):
            x,y = obj
            self.keyPointBottomLeft = QPointF(x,y)

        @setPoint.register(QPointF)
        def _(obj):
            self.keyPointBottomLeft = obj

        setPoint(obj)

    def setBottomRightPoint(self, obj):
        @singledispatch
        def setPoint(obj):
            return NotImplemented

        @setPoint.register(tuple)
        def _(obj):
            x,y = obj
            self.keyPointBottomRight = QPointF(x,y)

        @setPoint.register(QPointF)
        def _(obj):
            self.keyPointBottomRight = obj

        setPoint(obj)

class mGraphicParallelogramItem(QGraphicsItem):

    borderEventAreaSize = 10.0
    rotateEventAreaSize = 20.0 #半径

    transformScale = 0.8

    interactiveSubSignal = None

    def __init__(self, params:mGraphicParallelogramParams, interactiveSubSignal:InteractiveType, calcBoundingRect, parent = None):
        super(mGraphicParallelogramItem, self).__init__(parent)

        self.keyPointsList = []
        #定义平行四边形的四个顶点
        self.keyPointTopLeft = QPointF()
        self.keyPointTopRight = QPointF()
        self.keyPointBottomLeft= QPointF()
        self.keyPointBottomRight = QPointF()
        #定义平行四边形的中心点
        self.mCenterPoint = QPointF()

        #初始化所有keyPoint
        self.params = params
        self.initKeyPoints(self.params)

        #定义平行四边形的边框polygon
        self.mBorderPolygon = QPolygonF()
        #定义贴附于平行四边形四边的四个梯形响应区
        self.mLeftPolygon = QPolygonF()
        self.mTopPolygon = QPolygonF()
        self.mRightPolygon = QPolygonF()
        self.mBottomPolygon = QPolygonF()
        #定义贴附于平行四边形顶点的四个三角形响应区
        self.mTopLeftPolygon = QPolygonF()
        self.mTopRightPolygon = QPolygonF()
        self.mBottomRightPolygon = QPolygonF()
        self.mBottomLeftPolygon = QPolygonF()
        #定义位于平行四边形中心的旋转响应区
        self.mRotatePolygon = QPolygonF()

        #初始化所有Polygon
        self.initPolygons()

        #定义辅助变量
        self.mStateFlag = STATE_FLAG.DEFAULT_FLAG
        self.mStartPos = QPointF(0,0)
        self.mRotateAngle = 0
        self.interactiveSubSignal = interactiveSubSignal
        self.calcBoundingRect = calcBoundingRect

        #初始化位置
        self.setPos(-1*self.mCenterPoint.x(),-1*self.mCenterPoint.y())
        #设置GUI配置
        self.setToolTip("Click and drag me!")
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return self.calcBoundingRect()
        # return self.mBorderPolygon.boundingRect()

    def resetConfigs(self):
        self.mStateFlag = STATE_FLAG.DEFAULT_FLAG
        self.mStartPos = QPointF()
        self.mRotateAngle = 0

    def updateWithParams(self, params:mGraphicParallelogramParams):
        self.initKeyPoints(params)
        self.initPolygons()
        self.resetConfigs()
        self.scene().update()
        self.show()

    def getGraphicParallelogramParams(self):
        self.params.keyPointTopLeft = self.keyPointTopLeft
        self.params.keyPointTopRight = self.keyPointTopRight
        self.params.keyPointBottomRight = self.keyPointBottomRight
        self.params.keyPointBottomLeft = self.keyPointBottomLeft
        return self.params

    def initKeyPoints(self, params: mGraphicParallelogramParams):
        """
        根据外部输入来确定平行四边形的位置和大小
        """
        def checkPointUnDefined(fromPoint, toPoint:QPointF, x, y):
            if fromPoint is mGraphicParallelogramParams.UnDefined:
                toPoint.setX(x)
                toPoint.setY(y)
            else:
                toPoint.setX(fromPoint.x())
                toPoint.setY(fromPoint.y())

        checkPointUnDefined(params.keyPointTopLeft,self.keyPointTopLeft, 0.0, 0.0)
        checkPointUnDefined(params.keyPointTopRight, self.keyPointTopRight, 100.0, 0.0)
        checkPointUnDefined(params.keyPointBottomLeft, self.keyPointBottomLeft, 0.0, 100.0)
        checkPointUnDefined(params.keyPointBottomRight, self.keyPointBottomRight, 100.0, 100.0)
        self.mCenterPoint = self.calcCenterPoint(self.keyPointTopLeft, self.keyPointBottomRight)

    def calcCenterPoint(self, aPoint:QPointF, bPoint:QPointF):
        return QPointF((aPoint.x() + bPoint.x())/2, (aPoint.y() + bPoint.y())/2)

    def initPolygons(self):
        self.mBorderPolygon = QPolygonF(
            [self.keyPointTopLeft, self.keyPointTopRight, self.keyPointBottomRight, self.keyPointBottomLeft]
        )
        topLeftTopPoint = self.calcOptionalPointFromEndPoints(self.keyPointTopLeft, self.keyPointTopRight, self.borderEventAreaSize)
        topLeftLeftPoint = self.calcOptionalPointFromEndPoints(self.keyPointTopLeft, self.keyPointBottomLeft, self.borderEventAreaSize)
        topRightTopPoint = self.calcOptionalPointFromEndPoints(self.keyPointTopRight, self.keyPointTopLeft, self.borderEventAreaSize)
        topRightRightPoint = self.calcOptionalPointFromEndPoints(self.keyPointTopRight, self.keyPointBottomRight, self.borderEventAreaSize)
        bottomLeftLeftPoint = self.calcOptionalPointFromEndPoints(self.keyPointBottomLeft, self.keyPointTopLeft, self.borderEventAreaSize)
        bottomLeftBottomPoint = self.calcOptionalPointFromEndPoints(self.keyPointBottomLeft, self.keyPointBottomRight, self.borderEventAreaSize)
        bottomRightRightPoint = self.calcOptionalPointFromEndPoints(self.keyPointBottomRight, self.keyPointTopRight, self.borderEventAreaSize)
        bottomRightBottomPoint = self.calcOptionalPointFromEndPoints(self.keyPointBottomRight, self.keyPointBottomLeft, self.borderEventAreaSize)
        self.mLeftPolygon = QPolygonF(
            [topLeftTopPoint, bottomLeftBottomPoint, bottomLeftLeftPoint, topLeftLeftPoint]
        )
        self.mTopPolygon = QPolygonF(
            [topLeftLeftPoint, topRightRightPoint, topRightTopPoint, topLeftTopPoint]
        )
        self.mRightPolygon = QPolygonF(
            [topRightTopPoint, bottomRightBottomPoint, bottomRightRightPoint, topRightRightPoint]
        )
        self.mBottomPolygon = QPolygonF(
            [bottomLeftLeftPoint, bottomRightRightPoint, bottomRightBottomPoint, bottomLeftBottomPoint]
        )
        self.mTopLeftPolygon = QPolygonF([self.keyPointTopLeft, topLeftTopPoint, topLeftLeftPoint])
        self.mTopRightPolygon = QPolygonF([self.keyPointTopRight, topRightRightPoint, topRightTopPoint])
        self.mBottomRightPolygon = QPolygonF([self.keyPointBottomRight, bottomRightBottomPoint, bottomRightRightPoint])
        self.mBottomLeftPolygon = QPolygonF([self.keyPointBottomLeft, bottomLeftLeftPoint, bottomLeftBottomPoint])

        x,y = self.mCenterPoint.x(), self.mCenterPoint.y()
        rotateTopLeft = QPointF(x - self.rotateEventAreaSize, y - self.rotateEventAreaSize)
        rotateTopRight = QPointF(x + self.rotateEventAreaSize, y - self.rotateEventAreaSize)
        rotateBottomLeft = QPointF(x - self.rotateEventAreaSize, y + self.rotateEventAreaSize)
        rotateBottomRight = QPointF(x + self.rotateEventAreaSize, y + self.rotateEventAreaSize)
        self.mRotatePolygon = QPolygonF([rotateTopLeft, rotateTopRight, rotateBottomRight, rotateBottomLeft])

    def calcOptionalPointFromEndPoints(self, startPoint: QPointF, endPoint: QPointF, vectorLength):
        """
        计算从startPoint和endPoint构成的射线上，距离startPoint距离vectorLength的点的坐标
        """
        resPoint = QPointF()
        totalLength2 = self.calcDisBetweenPoints(startPoint, endPoint, isSqrt=False)
        vectorLength2 = vectorLength*vectorLength
        ratio = sqrt(vectorLength2 / totalLength2)
        resPoint.setX(startPoint.x() + ratio * (endPoint.x() - startPoint.x()))
        resPoint.setY(startPoint.y() + ratio * (endPoint.y() - startPoint.y()))
        return resPoint

    def calcDisBetweenPoints(self, aPoint:QPointF, bPoint:QPointF, isSqrt:bool = True):
        dis2 = (bPoint.y() - aPoint.y())**2 + (bPoint.x() - aPoint.x())**2
        if isSqrt:
            return sqrt(dis2)
        else:
            return dis2

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mStartPos = event.pos()
            if self.mRotatePolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.PointingHandCursor)
                self.mStateFlag = STATE_FLAG.ROTATE
                return
            elif self.mLeftPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeHorCursor)
                self.mStateFlag = STATE_FLAG.MOV_LEFT_LINE
                return
            elif self.mTopPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeVerCursor)
                self.mStateFlag = STATE_FLAG.MOV_TOP_LINE
                return
            elif self.mRightPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeHorCursor)
                self.mStateFlag = STATE_FLAG.MOV_RIGHT_LINE
                return
            elif self.mBottomPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeVerCursor)
                self.mStateFlag = STATE_FLAG.MOV_BOTTOM_LINE
                return
            elif self.mTopLeftPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeFDiagCursor)
                self.mStateFlag = STATE_FLAG.MOV_TOP_LEFT_POINT
                return
            elif self.mTopRightPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeBDiagCursor)
                self.mStateFlag = STATE_FLAG.MOV_TOP_RIGHT_POINT
                return
            elif self.mBottomLeftPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeBDiagCursor)
                self.mStateFlag = STATE_FLAG.MOV_BOTTOM_LEFT_POINT
                return
            elif self.mBottomRightPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeFDiagCursor)
                self.mStateFlag = STATE_FLAG.MOV_BOTTOM_RIGHT_POINT
                return
            elif self.mBorderPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.ClosedHandCursor)
                self.mStateFlag = STATE_FLAG.MOV_RECT
                return
            else:
                self.mStateFlag = STATE_FLAG.DEFAULT_FLAG
                return

    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent):
        pos = event.pos()
        if self.mStateFlag == STATE_FLAG.ROTATE:
            lineBegin = QLineF(self.mCenterPoint, self.mStartPos)
            lineEnd = QLineF(self.mCenterPoint, pos)
            mouseAngle = (360 - lineBegin.angleTo(lineEnd))%360*pi/180
            self.rotateHandler(mouseAngle)
            self.mStartPos = pos
            return

        dis = self.transformScale * self.calcDisBetweenPoints(self.mStartPos, pos)
        #移动距离过小跳过
        posToCenterPoint = pos - self.mCenterPoint
        startToCenterPoint = self.mStartPos - self.mCenterPoint
        direction = 1 if posToCenterPoint.manhattanLength() > startToCenterPoint.manhattanLength() else -1

        if self.mStateFlag == STATE_FLAG.MOV_RECT:
            self.moveRectHandler(pos)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_LEFT_LINE:
            #向外变大为正方向
            self.moveLineHandler(direction, dis, self.keyPointTopLeft, self.keyPointTopRight, self.keyPointBottomLeft, self.keyPointBottomRight)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_TOP_LINE:
            self.moveLineHandler(direction, dis, self.keyPointTopLeft, self.keyPointBottomLeft, self.keyPointTopRight, self.keyPointBottomRight)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_RIGHT_LINE:
            self.moveLineHandler(direction, dis, self.keyPointTopRight, self.keyPointTopLeft, self.keyPointBottomRight, self.keyPointBottomLeft)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_BOTTOM_LINE:
            self.moveLineHandler(direction, dis, self.keyPointBottomLeft, self.keyPointTopLeft, self.keyPointBottomRight, self.keyPointTopRight)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_TOP_LEFT_POINT:
            self.moveKeyPointHandler(direction, dis, self.keyPointTopLeft, self.keyPointBottomRight, self.keyPointTopRight, self.keyPointBottomLeft)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_TOP_RIGHT_POINT:
            self.moveKeyPointHandler(direction, dis, self.keyPointTopRight, self.keyPointBottomLeft, self.keyPointTopLeft, self.keyPointBottomRight)
            self.mStartPos = pos

        elif self.mStateFlag == STATE_FLAG.MOV_BOTTOM_LEFT_POINT:
            self.moveKeyPointHandler(direction, dis, self.keyPointBottomLeft, self.keyPointTopRight, self.keyPointTopLeft, self.keyPointBottomRight)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_BOTTOM_RIGHT_POINT:
            self.moveKeyPointHandler(direction, dis, self.keyPointBottomRight, self.keyPointTopLeft, self.keyPointTopRight, self.keyPointBottomLeft)
            self.mStartPos = pos
            return

    def moveLineHandler(self, direction, dis, keyPointA, keyPointB, keyPointC, keyPointD):
        """
        A,C是基准点，B,D是参考点
        direction为正在变大，此时基准点远离参考点，反之接近参考点
        """
        if direction < 0:
            newKeyPointA = self.calcOptionalPointFromEndPoints(
                keyPointA,keyPointB, dis
            )
            keyPointA.setX(newKeyPointA.x())
            keyPointA.setY(newKeyPointA.y())

            newKeyPointC = self.calcOptionalPointFromEndPoints(
                keyPointC, keyPointD, dis
            )
            keyPointC.setX(newKeyPointC.x())
            keyPointC.setY(newKeyPointC.y())
        else:
            newKeyPointA = self.calcOptionalPointFromEndPoints(
                keyPointB,
                keyPointA,
                dis + self.calcDisBetweenPoints(keyPointA, keyPointB)
            )
            keyPointA.setX(newKeyPointA.x())
            keyPointA.setY(newKeyPointA.y())
            newKeyPointC = self.calcOptionalPointFromEndPoints(
                keyPointD,
                keyPointC,
                dis + self.calcDisBetweenPoints(keyPointC, keyPointD)
            )
            keyPointC.setX(newKeyPointC.x())
            keyPointC.setY(newKeyPointC.y())
        self.mCenterPoint = self.calcCenterPoint(self.keyPointTopLeft, self.keyPointBottomRight)
        self.initPolygons()
        self.scene().update()
        self.interactiveSubSignal.emit(InteractiveType.ZOOM)

    def moveKeyPointHandler(self, direction, dis, keyPointMoving, keyPointAcross, keyPointNextA, keyPointNextB):
        """
        moving是正在移动的点，across是与之不共线的顶点，nextA,B是与之共线的两个顶点
        direction为正表示变大，远离across，相反接近
        """
        def calcNextPoints(direction, dis, keyPointAcross, keyPointNext):
            if direction > 0:
                _keyPointNext = self.calcOptionalPointFromEndPoints(
                    keyPointAcross,
                    keyPointNext,
                    dis + self.calcDisBetweenPoints(keyPointAcross, keyPointNext)
                )
            else:
                availableDis = self.calcDisBetweenPoints(keyPointNext, keyPointAcross) - self.rotateEventAreaSize * 2
                if dis > availableDis:
                    #防越界处理
                    dis = int(availableDis*0.9)
                _keyPointNext = self.calcOptionalPointFromEndPoints(
                    keyPointNext,
                    keyPointAcross,
                    dis
                )
            keyPointNext.setX(_keyPointNext.x())
            keyPointNext.setY(_keyPointNext.y())
        calcNextPoints(direction, dis, keyPointAcross, keyPointNextA)
        calcNextPoints(direction, dis, keyPointAcross, keyPointNextB)

        self.mCenterPoint = self.calcCenterPoint(keyPointNextA, keyPointNextB)
        _keyPointMoving = self.calcOptionalPointFromEndPoints(
            keyPointAcross,
            self.mCenterPoint,
            2 * self.calcDisBetweenPoints(keyPointAcross, self.mCenterPoint)
        )
        keyPointMoving.setX(_keyPointMoving.x())
        keyPointMoving.setY(_keyPointMoving.y())
        self.initPolygons()
        self.scene().update()
        self.interactiveSubSignal.emit(InteractiveType.ZOOM)

    def rotateHandler(self, rotateAngle):
        keyPoints = [
            self.keyPointTopLeft, self.keyPointTopRight, self.keyPointBottomRight, self.keyPointBottomLeft
        ]
        cX,cY = self.mCenterPoint.x(), self.mCenterPoint.y()
        for point in keyPoints:
            _point = QPointF(
                (point.x() - cX)*cos(rotateAngle) - (point.y() - cY)*sin(rotateAngle) + cX,
                (point.x() - cX)*sin(rotateAngle) + (point.y() - cY)*cos(rotateAngle) + cY
            )
            point.setX(_point.x())
            point.setY(_point.y())
        self.initPolygons()
        self.scene().update()
        self.interactiveSubSignal.emit(InteractiveType.ROTATE)

    def moveRectHandler(self, pos):
        pf = pos - self.mStartPos
        keyPoints = [
            self.keyPointTopLeft, self.keyPointTopRight, self.keyPointBottomRight, self.keyPointBottomLeft
        ]
        for point in keyPoints:
            point.setX(point.x() + pf.x())
            point.setY(point.y() + pf.y())
        self.mCenterPoint = self.calcCenterPoint(self.keyPointTopLeft, self.keyPointBottomRight)
        self.initPolygons()
        self.scene().update()
        self.interactiveSubSignal.emit(InteractiveType.TRANSLATE)

    def mouseReleaseEvent(self, event:QGraphicsSceneMouseEvent):
        self.setCursor(Qt.ArrowCursor)
        if self.mStateFlag == STATE_FLAG.MOV_RECT:
            self.mStateFlag = STATE_FLAG.DEFAULT_FLAG

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        #绘制旋转的圆形标识
        pf = self.mCenterPoint
        rect = QRectF(pf.x()-self.rotateEventAreaSize,pf.y()-self.rotateEventAreaSize,2*self.rotateEventAreaSize,2*self.rotateEventAreaSize)
        mBrush = QBrush(QColor(0,0,0,1))
        QPainter.setBrush(mBrush)
        QPainter.fillRect(rect, mBrush)
        mPen = QPen(Qt.green)
        mPen.setWidth(4)
        QPainter.setPen(mPen)
        QPainter.drawEllipse(pf, self.rotateEventAreaSize, self.rotateEventAreaSize)
        QPainter.drawPoint(pf)

        #在四个顶点处绘制字符标识
        # QPainter.drawText(self.keyPointTopLeft,"TL")
        # QPainter.drawText(self.keyPointTopRight,"TR")
        # QPainter.drawText(self.keyPointBottomLeft,"BL")
        # QPainter.drawText(self.keyPointBottomRight,"BR")

        #绘制边框
        mPen.setColor(Qt.yellow)
        QPainter.setPen(mPen)
        QPainter.drawPolygon(self.mBorderPolygon)

        #绘制提示区域
        # QPainter.drawPolygon(self.mLeftPolygon)
        # QPainter.drawPolygon(self.mRightPolygon)
        # QPainter.drawPolygon(self.mBottomPolygon)
        # QPainter.drawPolygon(self.mTopPolygon)
        # QPainter.drawPolygon(self.mTopLeftPolygon)
        # QPainter.drawPolygon(self.mTopRightPolygon)
        # QPainter.drawPolygon(self.mBottomLeftPolygon)
        # QPainter.drawPolygon(self.mBottomRightPolygon)


class mGraphicRectItem(mGraphicParallelogramItem):

    borderEventAreaSize = 5

    def __init__(self, params:mGraphicParallelogramParams, interactiveSubSignal, parent = None):
        super(mGraphicRectItem, self).__init__(params, interactiveSubSignal, parent)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mStartPos = event.pos()
            if self.mLeftPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.ClosedHandCursor)
                self.mStateFlag = STATE_FLAG.MOV_LEFT_LINE
                return
            if self.mRightPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.ClosedHandCursor)
                self.mStateFlag = STATE_FLAG.MOV_RIGHT_LINE
                return
            else:
                self.mStateFlag = STATE_FLAG.DEFAULT_FLAG
                return

    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent):
        pos = event.pos()
        dis = self.transformScale * self.calcDisBetweenPoints(self.mStartPos, pos)
        #移动距离过小跳过
        posToCenterPoint = pos - self.mCenterPoint
        startToCenterPoint = self.mStartPos - self.mCenterPoint
        direction = 1 if posToCenterPoint.manhattanLength() > startToCenterPoint.manhattanLength() else -1

        if self.mStateFlag == STATE_FLAG.MOV_LEFT_LINE:
            #向外变大为正方向
            self.moveLineHandler(direction, dis, self.keyPointTopLeft, self.keyPointTopRight, self.keyPointBottomLeft, self.keyPointBottomRight)
            self.mStartPos = pos
            return

        elif self.mStateFlag == STATE_FLAG.MOV_RIGHT_LINE:
            self.moveLineHandler(direction, dis, self.keyPointTopRight, self.keyPointTopLeft, self.keyPointBottomRight, self.keyPointBottomLeft)
            self.mStartPos = pos
            return

    def moveLineHandler(self, direction, dis, keyPointA, keyPointB, keyPointC, keyPointD):
        """
        A,C是基准点，B,D是参考点
        direction为正在变大，此时基准点远离参考点，反之接近参考点
        """
        if direction < 0:
            newKeyPointA = self.calcOptionalPointFromEndPoints(
                keyPointA,keyPointB, dis
            )
            keyPointA.setX(newKeyPointA.x())
            keyPointA.setY(newKeyPointA.y())

            newKeyPointC = self.calcOptionalPointFromEndPoints(
                keyPointC, keyPointD, dis
            )
            keyPointC.setX(newKeyPointC.x())
            keyPointC.setY(newKeyPointC.y())
        else:
            newKeyPointA = self.calcOptionalPointFromEndPoints(
                keyPointB,
                keyPointA,
                dis + self.calcDisBetweenPoints(keyPointA, keyPointB)
            )
            keyPointA.setX(newKeyPointA.x())
            keyPointA.setY(newKeyPointA.y())
            newKeyPointC = self.calcOptionalPointFromEndPoints(
                keyPointD,
                keyPointC,
                dis + self.calcDisBetweenPoints(keyPointC, keyPointD)
            )
            keyPointC.setX(newKeyPointC.x())
            keyPointC.setY(newKeyPointC.y())
        self.mCenterPoint = self.calcCenterPoint(self.keyPointTopLeft, self.keyPointBottomRight)
        self.initPolygons()
        self.scene().update()
        self.interactiveSubSignal.emit(InteractiveType.ADJUST_THICKNESS)

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        #绘制旋转的圆形标识
        pf = self.mCenterPoint
        rect = QRectF(pf.x()-self.rotateEventAreaSize,pf.y()-self.rotateEventAreaSize,2*self.rotateEventAreaSize,2*self.rotateEventAreaSize)
        mBrush = QBrush(QColor(0,0,0,1))
        QPainter.setBrush(mBrush)
        QPainter.fillRect(rect, mBrush)
        mPen = QPen(Qt.green)
        mPen.setWidth(4)
        QPainter.setPen(mPen)

        #绘制边框
        mPen.setColor(Qt.yellow)
        QPainter.setPen(mPen)
        QPainter.drawPolygon(self.mBorderPolygon)

        #绘制提示区域
        # QPainter.drawPolygon(self.mLeftPolygon)
        # QPainter.drawPolygon(self.mRightPolygon)