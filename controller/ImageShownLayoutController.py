from PyQt5.QtCore import *
from ui.SingleImageShownContainer import SingleImageShownContainer
from ui.SlideshowContainer import SlideshowContainer
from ui.config import uiConfig

from copy import deepcopy
import numpy as np
import sympy as sp
from utils.status import Status
from utils.util import checkSameSeries,checkSameStudy

class ImageShownLayoutController(QObject):

    selectImageShownContainerSignal = pyqtSignal(SingleImageShownContainer,bool)
    initToolsContainerStateSignal = pyqtSignal()
    updateToolsContainerStateSignal = pyqtSignal(int)
    #第一个参数指示发出信号的是哪一个container
    updateCrossViewSignal = pyqtSignal(SingleImageShownContainer)

    #此处imageShownContainerLayout类型是ui.CustomDecoratedLayout
    def __init__(
            self,
            imageShownContainerWidget,
            imageShownContainerLayout
    ):
        QObject.__init__(self)
        self.imageShownContainerWidget = imageShownContainerWidget
        self.imageShownContainerLayout = imageShownContainerLayout

        self.curlayout = (0, 0, 1, 1)
        self.imageShownWidgetPool = { }
        self.selectedImageShownContainer = None
        self.imageSlideshow = None
        self.selectImageShownContainerSignal.connect(self.selectImageShownContainerHandler)
        self.updateCrossViewSignal.connect(self.updateCrossViewSignalHandler)
        self.imageSlideShowPlayFlag = False

    def selectImageShownContainerHandler(self, container, isInit):
        if self.selectedImageShownContainer is not None:
            self.tryQuitImageSlideShow()
            if self.selectedImageShownContainer is not container:
                self.selectedImageShownContainer.resetSelectState()
                self.selectedImageShownContainer = container
        else:
            self.selectedImageShownContainer = container

        if isInit:
            self.initToolsContainerStateSignal.emit()
        else:
            self.updateToolsContainerStateSignal.emit(container.curMode)

    def tryQuitImageSlideShow(self):
        # if self.imageSlideshow is not None: self.imageSlideshow.close()
        if self.imageSlideShowPlayFlag:
            self.imageSlideShowPlayFlag = not self.imageSlideShowPlayFlag
            self.selectedImageShownContainer.mImageShownWidget.controlSlideShow(self.imageSlideShowPlayFlag)

    def initLayoutParams(self):
        self.imageShownContainerLayout.getLayout().setContentsMargins(uiConfig.shownContainerMargins)
        self.imageShownContainerLayout.getLayout().setSpacing(uiConfig.shownContainerContentSpace)

    def initWidget(self):
        for col in range(uiConfig.toolsSelectRegionCol):
            for row in range(uiConfig.toolsSelectRegionRow):
                self.imageShownWidgetPool[(row, col)] = SingleImageShownContainer(self.selectImageShownContainerSignal, self.updateCrossViewSignal)
                self.addWidget(self.imageShownWidgetPool[(row, col)], row, col)

    def addWidget(self, childWidget, row, col, rowSpan = 1, colSpan = 1):
        self.imageShownContainerLayout.getLayout().addWidget(childWidget, row, col, rowSpan, colSpan)

    def updateLayout(self, layoutTuple):
        if layoutTuple == self.curlayout: return
        self.curlayout = deepcopy(layoutTuple)

        topRow, leftCol, bottomRow, rightCol = layoutTuple

        #从Layout移除所有子Widget
        self.imageShownContainerLayout.clearLayout()

        for row in range(topRow, bottomRow + 1):
            for col in range(leftCol, rightCol + 1):
                childWidget = self.imageShownWidgetPool[(row, col)]
                self.addWidget(childWidget, row, col)
                print("childWidget ", childWidget.geometry())

    #crossView 逻辑控制
    def updateCrossViewSignalHandler(self, emitContainer):
        self.imageShownContainerLayout.mapWidgetsFunc(self.updateCrossViewSignalSCHandler, emitContainer)

    def updateCrossViewSignalSCHandler(self, handleContainer, emitContainerTuple):
        emitContainer, = emitContainerTuple
        if handleContainer is emitContainer\
            or handleContainer.curMode != SingleImageShownContainer.m2DMode\
            or len(handleContainer.imageData.curFilePath) < 1:return
        if (emitContainer.curMode != SingleImageShownContainer.m2DMode) \
            and (emitContainer.curMode != SingleImageShownContainer.mRTMode):
            handleContainer.mImageShownWidget.tryHideCrossBoxWidget()
            return

        df1 = handleContainer.imageData.getDcmDataByIndex(handleContainer.imageData.currentIndex)
        df2 = emitContainer.imageData.getDcmDataByIndex(emitContainer.imageData.currentIndex)
        isSameStudy = checkSameStudy(df1,df2)
        isSameSeries = checkSameSeries(df1, df2)
        if (not isSameStudy) or isSameSeries:
            handleContainer.mImageShownWidget.tryHideCrossBoxWidget()
            return

        crossViewPointRatios = self.calcCrossViewDisPos(handleContainer,emitContainer)

        if crossViewPointRatios == Status.bad:
            #交线为空
            handleContainer.mImageShownWidget.tryHideCrossBoxWidget()
            return
        #由自定义CrossView绘制交点之间的连线
        #这里的point是比例值
        handleContainer.mImage2DShownData.showCrossFlag = True
        handleContainer.mImage2DShownData.crossViewRatios = crossViewPointRatios
        handleContainer.tryUpdateCrossBoxWidget()

    def calcCrossViewDisPos(self,handleContainer,emitContainer):
        #建立世界坐标系
        index1,index2 = handleContainer.imageData.currentIndex, emitContainer.imageData.currentIndex
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= handleContainer.imageData.getBasePosInfo(index1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = emitContainer.imageData.getBasePosInfo(index2)

        if (normalvector1 == normalvector2).all():
            #平面平行
            return Status.bad

        #建立交线方程组
        sp.init_printing(use_unicode=True)
        x, y, z = sp.symbols('x, y, z')
        eq=[normalvector1[0] * (x - ImagePosition1[0]) + normalvector1[1] * (y - ImagePosition1[1]) + normalvector1[2] * (z - ImagePosition1[2]),\
            normalvector2[0] * (x - ImagePosition2[0]) + normalvector2[1] * (y - ImagePosition2[1]) + normalvector2[2] * (z - ImagePosition2[2])]

        #求世界坐标系下的交线方程
        lineExpr = list(sp.linsolve(eq, [x, y, z]))
        if len(lineExpr) < 1:
            #平面虽然不平行，但非常接近平行，单精度浮点下无法建立交线方程
            return Status.bad
        #获得交线上两个定点
        fixPoint1,fixPoint2 = self.getWorldPointOnCrossLine(lineExpr,0,0,0),self.getWorldPointOnCrossLine(lineExpr,1,1,1)

        #获得两个定点在handleContainer图像坐标系下的坐标
        fixPoint1_x,fixPoint1_y = self.getCrossPointOnImagePlane(
            fixPoint1, ImagePosition1, ImageOrientationX1, ImageOrientationY1, PixelSpacing1[0], PixelSpacing1[1]
        )
        fixPoint2_x,fixPoint2_y = self.getCrossPointOnImagePlane(
            fixPoint2, ImagePosition1, ImageOrientationX1, ImageOrientationY1, PixelSpacing1[0], PixelSpacing1[1]
        )

        #在图像坐标系下建立交线方程，并求其与图像边界的交点
        x, y = sp.symbols('x, y')
        crossLine = (y - fixPoint1_y) * (fixPoint2_x - fixPoint1_x) - (x - fixPoint1_x) * (fixPoint2_y - fixPoint1_y)
        res = []
        for line in [x-Rows1,y-Cols1,x,y]:
            eq = [crossLine, line]
            point = list(sp.linsolve(eq, [x,y]))
            if len(point) < 1:continue
            point = point[0]
            pointx,pointy = int(point[0]),int(point[1])
            if pointx < 0 or pointx > Rows1 or pointy < 0 or pointy > Cols1:continue
            res.append(QPoint(pointx,pointy))
        if len(res) < 2:return  Status.bad
        #计算交点的屏幕坐标
        imageDisPos,imageDisWidth,imageDisHeight = self.getImageDisplayInfo(handleContainer.mImageShownWidget)
        kImgToDisW,kImgToDisH = imageDisHeight/Rows1,imageDisWidth/Cols1
        # print("Rows1,Cols1 ",Rows1,Cols1)
        resDis = [QPoint(int(point.x() * kImgToDisW),int(point.y()*kImgToDisH)) + imageDisPos for point in res]

        #将绝对坐标转为相对ImageContainer的比例值
        size = handleContainer.mImageShownWidget.size()
        resDis = [(point.x() / size.width(),point.y() / size.height()) for point in resDis]

        return resDis

    def getWorldPointOnCrossLine(self,lineExpr,*args):
        x_tmp,y_tmp,z_tmp, = args
        x, y, z = sp.symbols('x, y, z')
        x_expr,y_expr,z_expr = lineExpr[0][0],lineExpr[0][1],lineExpr[0][2]
        point = (
            x_expr.evalf(subs={x:x_tmp,y:y_tmp,z:z_tmp}),
            y_expr.evalf(subs={x:x_tmp,y:y_tmp,z:z_tmp}),
            z_expr.evalf(subs={x:x_tmp,y:y_tmp,z:z_tmp})
        )
        return point

    def getCrossPointOnImagePlane(self, fixPoint, originPos, axisX, axisY, pixelSpaceX, pixelSpaceY):
        vectorOtoP = np.array(fixPoint) - originPos
        x = np.dot(vectorOtoP,axisX) / pixelSpaceX
        y = np.dot(vectorOtoP,axisY) / pixelSpaceY
        return (x,y)

    def getImageDisplayInfo(self, m2DWidget):
        """ 目前该函数只支持缩放中心点在视图正中央的情况，如果image被拖动到其他位置，计算错误"""

        bounds = m2DWidget.imageViewer.GetImageActor().GetBounds()
        #图像右下角
        colBound,rowBound = bounds[1],bounds[3]
        z = m2DWidget.renImage.GetZ(int(colBound),int(rowBound))
        m2DWidget.renImage.SetWorldPoint(colBound,rowBound,z,0)
        m2DWidget.renImage.WorldToDisplay()
        imageBoundPoint = m2DWidget.renImage.GetDisplayPoint()
        #图像左上角
        colBound2,rowBound2 = bounds[0],bounds[2]
        z = m2DWidget.renImage.GetZ(int(colBound2),int(rowBound2))
        m2DWidget.renImage.SetWorldPoint(colBound2,rowBound2,z,0)
        m2DWidget.renImage.WorldToDisplay()
        imageBoundPoint2 = m2DWidget.renImage.GetDisplayPoint()

        # print("bounds: ",imageBoundPoint,imageBoundPoint2)
        imageBoundPoint = np.array(imageBoundPoint[:2])
        imageBoundPoint2 = np.array(imageBoundPoint2[:2])
        width,height = tuple(imageBoundPoint - imageBoundPoint2)
        pos = QPoint(imageBoundPoint2[0],imageBoundPoint2[1])
        # print("左上角坐标：", pos,width,height)
        return pos,width,height

    def controlMoveEvent(self):
        self.imageShownContainerLayout.mapWidgetsFunc(
                lambda handleContainer,*args:handleContainer.tryUpdateCrossBoxWidget(),
                None
        )

    #走马灯播放控制器(得搬到container里)evermg42
    def imageSlideshowControl(self,isShown):
        if(isShown):
            
            self.imageSlideshow=SlideshowContainer(
                self.imageSlideShowSlowHandler,
                self.imageSlideShowPlayHandler,
                self.imageSlideShowFasterHandler
            )

            self.imageSlideshow.setWindowFlags(
                Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint
            )#隐藏标题栏|在主窗口前
            #self.dialog.setWindowModality(Qt.ApplicationModal)#只有该dialog关闭，才可以关闭父界面

            self.imageSlideshow.setWindowModality(Qt.NonModal)
            self.imageSlideshow.show()
        else:
            self.tryQuitImageSlideShow()
            self.imageSlideshow.close()#直觉如此

    def checkSelectContainerCanSlideShow(self):
        if self.selectedImageShownContainer is None or\
            self.selectedImageShownContainer.curMode is not SingleImageShownContainer.m2DMode or\
            self.selectedImageShownContainer.mImageShownWidget is None: return False
        else: return True

    def imageSlideShowPlayHandler(self):
        print("播放button")
        if not self.checkSelectContainerCanSlideShow():return
        if self.selectedImageShownContainer.mImageShownWidget.canSlideShow():
            self.imageSlideShowPlayFlag = not self.imageSlideShowPlayFlag
            print("申请控制slideShow")
            self.selectedImageShownContainer.mImageShownWidget.controlSlideShow(self.imageSlideShowPlayFlag)

    def imageSlideShowSlowHandler(self):
        if not self.checkSelectContainerCanSlideShow():return
        print("slow")
        self.selectedImageShownContainer.mImageShownWidget.controlSlideShowSpeed(0.1)

    def imageSlideShowFasterHandler(self):
        if not self.checkSelectContainerCanSlideShow():return
        print("fast")
        self.selectedImageShownContainer.mImageShownWidget.controlSlideShowSpeed(-0.1)

    #模式切换
    def imageModeSelectHandler(self, mode):
        if self.selectedImageShownContainer.curMode ==  mode: return
        self.tryQuitImageSlideShow() # 退出跑马灯
        if self.selectedImageShownContainer.switchImageContainerMode(mode) == Status.bad: return # 渲染不出就不渲染了
        self.updateToolsContainerStateSignal.emit(self.selectedImageShownContainer.curMode)

    #imageExtraInfo开关
    def imageExtraInfoStateHandler(self, isShow):
        self.selectedImageShownContainer.controlImageExtraInfoState(isShow)

    def closeEvent(self, QCloseEvent):
        for col in range(uiConfig.toolsSelectRegionCol):
            for row in range(uiConfig.toolsSelectRegionRow):
                self.imageShownWidgetPool[(row,col)].closeEvent(QCloseEvent)
        if self.imageSlideshow is not None: self.imageSlideshow.closeEvent(QCloseEvent)

    def clearViews(self):
        self.selectedImageShownContainer = None
        self.imageShownContainerLayout.mapWidgetsFunc(lambda container,*args:container.close(),None)
        self.imageShownContainerLayout.clearLayout()
        self.imageShownWidgetPool.clear()
        self.initWidget()
