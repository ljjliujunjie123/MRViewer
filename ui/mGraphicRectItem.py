from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QPointF,QRectF
from PyQt5.QtGui import QPen,QPolygonF,QBrush,QColor
from math import atan,atan2,sin,cos,pi,sqrt
from enum import Enum

class STATE_FLAG(Enum):
    DEFAULT_FLAG=0
    MOV_LEFT_LINE=1 #标记当前为用户按下矩形的左边界区域
    MOV_TOP_LINE=2 #标记当前为用户按下矩形的上边界区域
    MOV_RIGHT_LINE=3 #标记当前为用户按下矩形的右边界区域
    MOV_BOTTOM_LINE=4 #标记当前为用户按下矩形的下边界区域
    MOV_RECT=6 #标记当前为鼠标拖动图片移动状态
    ROTATE=7 #标记当前为旋转状态

class mGraphicRectItem(QGraphicsItem):

    def __init__(self, parent = None):
        super(QGraphicsItem,self).__init__(parent)
        self.mStateFlag = STATE_FLAG.DEFAULT_FLAG
        self.mOldRect = QRectF(0,0,300,300)
        self.mOldRectPolygon = QPolygonF()
        self.mRotateCenter = QPointF()
        self.mRotateAreaRect = QRectF()
        self.mSmallRotateRect = QRectF()
        self.mSmallRotatePolygon = QPolygonF()
        self.mInsicedRect = QRectF()
        self.mInsicedPolygon = QPolygonF()
        self.mLeftRect = QRectF()
        self.mRightRect = QRectF()
        self.mTopRect = QRectF()
        self.mBottomRect = QRectF()
        self.mLeftPolygon = QPolygonF()
        self.mTopPolygon = QPolygonF()
        self.mRightPolygon = QPolygonF()
        self.mBottomPolygon = QPolygonF()
        self.mStartPos = QPointF()
        self.mRotateAngle = 0
        self.isResize = False
        self.isRotate = False

        self.setPos(-1*self.mOldRect.width()/2,-1*self.mOldRect.height()/2)
        self.setRectSize(self.mOldRect)
        self.setToolTip("Click and drag me!")
        self.mPointFofSmallRotateRect = []
        self.setRotate(0)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        boundingRectF = self.mOldRectPolygon.boundingRect()
        return QRectF(boundingRectF.x() - 40, boundingRectF.y() - 40,
                      boundingRectF.width() + 80, boundingRectF.height() + 80)

    def setRectSize(self, rect: QRectF, isResetRotateCenter = True):
        self.mOldRect = rect
        if isResetRotateCenter:
            self.mRotateCenter.setX(self.mOldRect.x() + self.mOldRect.width() / 2)
            self.mRotateCenter.setY(self.mOldRect.y() + self.mOldRect.height() / 2)
        self.mOldRectPolygon = self.getRotatePolygonFromRect(self.mRotateCenter, self.mOldRect, self.mRotateAngle)

        self.mInsicedRect = QRectF(self.mOldRect.x() + 8, self.mOldRect.y() + 8, self.mOldRect.width() - 16, self.mOldRect.height() - 16)
        self.mInsicedPolygon = self.getRotatePolygonFromRect(self.mRotateCenter, self.mInsicedRect, self.mRotateAngle)

        self.mLeftRect = QRectF(self.mOldRect.x(),self.mOldRect.y(),8,self.mOldRect.height()-8)
        self.mLeftPolygon = self.getRotatePolygonFromRect(self.mRotateCenter,self.mLeftRect,self.mRotateAngle)

        self.mTopRect = QRectF(self.mOldRect.x()+8,self.mOldRect.y(),self.mOldRect.width()-8,8)
        self.mTopPolygon = self.getRotatePolygonFromRect(self.mRotateCenter,self.mTopRect,self.mRotateAngle)

        self.mRightRect = QRectF(self.mOldRect.right()-8,self.mOldRect.y()+8,8,self.mOldRect.height()-16)
        self.mRightPolygon = self.getRotatePolygonFromRect(self.mRotateCenter,self.mRightRect,self.mRotateAngle)

        self.mBottomRect = QRectF(self.mOldRect.x(),self.mOldRect.bottom()-8,self.mOldRect.width()-8,8)
        self.mBottomPolygon = self.getRotatePolygonFromRect(self.mRotateCenter,self.mBottomRect,self.mRotateAngle)

        self.mSmallRotateRect = self.getSmallRotateRect(rect.topLeft(),rect.topRight())
        self.mSmallRotatePolygon = self.getRotatePolygonFromRect(self.mRotateCenter,self.mSmallRotateRect,self.mRotateAngle)

        print("init icView polygon ", self.boundingRect())
        print("init left polygon ", self.mLeftPolygon.boundingRect())
        print("init right polygon ", self.mRightPolygon.boundingRect())
        print("init top polygon ", self.mTopPolygon.boundingRect())
        print("init bottom polygon ", self.mBottomPolygon.boundingRect())
        print("init rotate polygon ", self.mSmallRotatePolygon.boundingRect())

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        pf = self.getSmallRotateRectCenter(self.mOldRectPolygon[0],self.mOldRectPolygon[1])
        rect = QRectF(pf.x()-10,pf.y()-10,20,20)

        mBrush = QBrush(QColor(0,0,0,1))
        QPainter.setBrush(mBrush)
        QPainter.fillRect(rect, mBrush)
        QPainter.drawPolygon(self.mOldRectPolygon)

        mPen = QPen(Qt.green)
        mPen.setWidth(2)
        QPainter.setPen(mPen)
        pf = self.getSmallRotateRectCenter(self.mOldRectPolygon[0],self.mOldRectPolygon[1])
        rect = QRectF(pf.x()-10,pf.y()-10,20,20)
        QPainter.drawEllipse(rect)
        QPainter.drawPoint(pf)
        mPen.setColor(Qt.yellow)
        QPainter.setPen(mPen)
        QPainter.drawPolygon(self.mOldRectPolygon)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        print("graphicRect press")
        if event.button() == Qt.LeftButton:
            self.mStartPos = event.pos()
            print("press point ", self.mStartPos)
            print(self.mSmallRotatePolygon.boundingRect())
            if self.mSmallRotatePolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.PointingHandCursor)
                self.mStateFlag = STATE_FLAG.ROTATE
            elif self.mInsicedPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.ClosedHandCursor)
                self.mStateFlag = STATE_FLAG.MOV_RECT
            elif self.mLeftPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeHorCursor)
                self.mStateFlag = STATE_FLAG.MOV_LEFT_LINE
            elif self.mTopPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeVerCursor)
                self.mStateFlag = STATE_FLAG.MOV_TOP_LINE
            elif self.mRightPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeHorCursor)
                self.mStateFlag = STATE_FLAG.MOV_RIGHT_LINE
            elif self.mBottomPolygon.containsPoint(self.mStartPos, Qt.WindingFill):
                self.setCursor(Qt.SizeVerCursor)
                self.mStateFlag = STATE_FLAG.MOV_BOTTOM_LINE
            else:
                self.mStateFlag = STATE_FLAG.DEFAULT_FLAG

        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent):
        print("graphicRect move")
        pos = event.pos()
        if self.mStateFlag == STATE_FLAG.ROTATE:
            rotateAngle = atan2(
                    (pos.x() - self.mRotateCenter.x()),
                    (pos.y() - self.mRotateCenter.y())
            )*180/pi
            self.setRotate(180 - rotateAngle)
            self.setRectSize(self.mOldRect)

        elif self.mStateFlag == STATE_FLAG.MOV_RECT:
            pf = event.pos() - self.mStartPos
            self.moveBy(pf.x(), pf.y())
            self.setRectSize(self.mOldRect)
            self.scene().update()

        elif self.mStateFlag == STATE_FLAG.MOV_LEFT_LINE:
            pf = QPointF(
                    (self.mOldRectPolygon.at(1).x()+self.mOldRectPolygon.at(2).x())/2,
                    (self.mOldRectPolygon.at(1).y()+self.mOldRectPolygon.at(2).y())/2
            )
            dis = sqrt((pos.x()-pf.x())**2 +(pos.y()-pf.y())**2)
            dis2LT = sqrt((pos.x()-self.mOldRectPolygon.at(0).x())**2 + (pos.y()-self.mOldRectPolygon.at(0).y())**2)
            dis2RT = sqrt((pos.x()-self.mOldRectPolygon.at(1).x())**2 + (pos.y()-self.mOldRectPolygon.at(1).y())**2)

            if dis<16 or dis2LT>dis2RT : return

            newRect = QRectF(self.mOldRect)
            newRect.setLeft(self.mOldRect.right()-dis)
            newRect.setRight(self.mOldRect.right())
            self.setRectSize(newRect,False)
            self.mRotateCenter=QPointF(
                    (self.mOldRectPolygon.at(0).x()+self.mOldRectPolygon.at(2).x())/2,
                    (self.mOldRectPolygon.at(0).y()+self.mOldRectPolygon.at(2).y())/2
            )
            self.mOldRect.moveCenter(self.mRotateCenter)
            self.setRectSize(self.mOldRect)
            self.scene().update()

        elif self.mStateFlag == STATE_FLAG.MOV_TOP_LINE:
            pf = QPointF(
                    (self.mOldRectPolygon.at(2).x()+self.mOldRectPolygon.at(3).x())/2,
                    (self.mOldRectPolygon.at(2).y()+self.mOldRectPolygon.at(3).y())/2
            )
            dis = sqrt((pos.x()-pf.x())**2 +(pos.y()-pf.y())**2)
            dis2LT = sqrt((pos.x()-self.mOldRectPolygon.at(0).x())**2 + (pos.y()-self.mOldRectPolygon.at(0).y())**2)
            dis2LB = sqrt((pos.x()-self.mOldRectPolygon.at(3).x())**2 + (pos.y()-self.mOldRectPolygon.at(3).y())**2)

            if dis<16 or dis2LT>dis2LB : return

            newRect = QRectF(self.mOldRect)
            newRect.setTop(self.mOldRect.bottom()-dis)
            newRect.setBottom(self.mOldRect.bottom())
            self.setRectSize(newRect,False)
            self.mRotateCenter=QPointF(
                    (self.mOldRectPolygon.at(0).x()+self.mOldRectPolygon.at(2).x())/2,
                    (self.mOldRectPolygon.at(0).y()+self.mOldRectPolygon.at(2).y())/2
            )
            self.mOldRect.moveCenter(self.mRotateCenter)
            self.setRectSize(self.mOldRect)
            self.scene().update()

        elif self.mStateFlag == STATE_FLAG.MOV_RIGHT_LINE:
            pf = QPointF(
                    (self.mOldRectPolygon.at(0).x()+self.mOldRectPolygon.at(3).x())/2,
                    (self.mOldRectPolygon.at(0).y()+self.mOldRectPolygon.at(3).y())/2
            )
            dis = sqrt((pos.x()-pf.x())**2 +(pos.y()-pf.y())**2)
            dis2LT = sqrt((pos.x()-self.mOldRectPolygon.at(0).x())**2 + (pos.y()-self.mOldRectPolygon.at(0).y())**2)
            dis2RT = sqrt((pos.x()-self.mOldRectPolygon.at(1).x())**2 + (pos.y()-self.mOldRectPolygon.at(1).y())**2)

            if dis<16 or dis2LT<dis2RT : return

            newRect = QRectF(self.mOldRect)
            newRect.setLeft(self.mOldRect.left())
            newRect.setRight(self.mOldRect.left()+dis)
            self.setRectSize(newRect,False)
            self.mRotateCenter=QPointF(
                    (self.mOldRectPolygon.at(0).x()+self.mOldRectPolygon.at(2).x())/2,
                    (self.mOldRectPolygon.at(0).y()+self.mOldRectPolygon.at(2).y())/2
            )
            self.mOldRect.moveCenter(self.mRotateCenter)
            self.setRectSize(self.mOldRect)
            self.scene().update()

        elif self.mStateFlag == STATE_FLAG.MOV_BOTTOM_LINE:
            pf = QPointF(
                    (self.mOldRectPolygon.at(0).x()+self.mOldRectPolygon.at(1).x())/2,
                    (self.mOldRectPolygon.at(0).y()+self.mOldRectPolygon.at(1).y())/2
            )
            dis = sqrt((pos.x()-pf.x())**2 +(pos.y()-pf.y())**2)
            dis2LT = sqrt((pos.x()-self.mOldRectPolygon.at(0).x())**2 + (pos.y()-self.mOldRectPolygon.at(0).y())**2)
            dis2LB = sqrt((pos.x()-self.mOldRectPolygon.at(3).x())**2 + (pos.y()-self.mOldRectPolygon.at(3).y())**2)

            if dis<16 or dis2LT<dis2LB : return

            newRect = QRectF(self.mOldRect)
            newRect.setTop(self.mOldRect.top())
            newRect.setBottom(self.mOldRect.top()+dis)
            self.setRectSize(newRect,False)
            self.mRotateCenter=QPointF(
                    (self.mOldRectPolygon.at(0).x()+self.mOldRectPolygon.at(2).x())/2,
                    (self.mOldRectPolygon.at(0).y()+self.mOldRectPolygon.at(2).y())/2
            )
            self.mOldRect.moveCenter(self.mRotateCenter)
            self.setRectSize(self.mOldRect)
            self.scene().update()

    def mouseReleaseEvent(self, event:QGraphicsSceneMouseEvent):
        print("graphicRect release")
        self.setCursor(Qt.ArrowCursor)
        if self.mStateFlag == STATE_FLAG.MOV_RECT:
            self.mStateFlag = STATE_FLAG.DEFAULT_FLAG
        else:
            super().mouseReleaseEvent(event)

    def setRotate(self, rotateAngle, ptCenter = QPointF(-999,-999)):
        self.isRotate = True
        if ptCenter.x == -999 and ptCenter.y() == -999:
            self.mRotateCenter = QPointF(
                    (self.mOldRect.x() + self.mOldRect.width()/2),
                    (self.mOldRect.y() + self.mOldRect.height()/2)
            )
        else:
            self.mRotateCenter = ptCenter
        self.mRotateAngle = rotateAngle
        self.update()

    def getRotatePoint(self, ptCenter, ptIn: QPointF, angle):
        dx,dy = ptCenter.x(),ptCenter.y()
        x,y = ptIn.x(),ptIn.y()
        xx = (x-dx)*cos(angle*pi/180) - (y-dy)*sin(angle*pi/180) + dx
        yy = (x-dx)*sin(angle*pi/180) + (y-dy)*cos(angle*pi/180) + dy
        return QPointF(xx,yy)

    def getRotatePoints(self, ptCenter, ptIns: list, angle):
        lstPt = []
        for i in range(len(ptIns)):
            lstPt.append(self.getRotatePoint(ptCenter,ptIns[i],angle))
        return lstPt

    def getRotatePolygonFromRect(self, ptCenter, rectIn:QRectF, angle):
        pts = []
        pts.append(self.getRotatePoint(ptCenter,rectIn.topLeft(),angle))
        pts.append(self.getRotatePoint(ptCenter,rectIn.topRight(),angle))
        pts.append(self.getRotatePoint(ptCenter,rectIn.bottomRight(),angle))
        pts.append(self.getRotatePoint(ptCenter,rectIn.bottomLeft(),angle))
        return QPolygonF(pts)

    def getCrtPosRectToScreen(self):
        return QRectF(
            self.mOldRect.x() + self.pos().x(),
            self.mOldRect.y() + self.pos().y(),
            self.mOldRect.width(),
            self.mOldRect.height()
        )

    def getSmallRotateRect(self, ptA: QPointF, ptB: QPointF):
        pt = self.getSmallRotateRectCenter(ptA, ptB)
        return QRectF(pt.x() - 10, pt.y() - 10, 20, 20)

    def getSmallRotateRectCenter(self, ptA: QPointF, ptB: QPointF):
        ptCenter = QPointF((ptA.x() + ptB.x())/2, (ptA.y() + ptB.y())/2)
        x,y = 0,0
        if abs(ptB.y() - ptA.y())<0.1:
            x = ptCenter.x()
            if ptA.x() < ptB.x():
                y = ptCenter.y() - 20
            else:
                y = ptCenter.y() + 20

        else:
            k = (ptA.x() - ptB.x()) / (ptB.y() - ptA.y())
            b = (ptA.y() + ptB.y())/2 - k * (ptA.x() + ptB.x())/2
            if ptB.y() > ptA.y():
                x = 20*cos(atan(k)) + ptCenter.x()
            elif ptB.y() < ptA.y():
                x = -20*cos(atan(k)) + ptCenter.x()
            y = k * x + b
        return QPointF(x,y)