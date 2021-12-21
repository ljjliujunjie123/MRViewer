from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import vtkmodules.all as vtk
from ui.SingleImageShownContainer import SingleImageShownContainer
from ui.SlideshowContainer import SlideshowContainer
from ui.config import uiConfig

from copy import deepcopy
import numpy as np
import sympy as sp
import pydicom
from utils.status import Status
from utils.util import checkSameSeries,checkSameStudy

class ImageShownLayoutController(QObject):

    selectImageShownContainerSignal = pyqtSignal(SingleImageShownContainer,bool)
    updateToolsContainerStateSignal = pyqtSignal(bool)

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
        self.selectImageShownContainerSignal.connect(self.selectImageShownContianerHandler)
        self.updateCrossViewSignal.connect(self.updateCrossViewSignalHandler)
        self.imageSlideShowPlayFlag = False

    def selectImageShownContianerHandler(self, container, isSelected):
        if self.selectedImageShownContainer is not None:
            self.tryQuitImageSlideShow()
            if self.selectedImageShownContainer is not container:
                self.selectedImageShownContainer.resetSelectState()
                self.selectedImageShownContainer = container
        else:
            self.selectedImageShownContainer = container
        self.updateToolsContainerStateSignal.emit(isSelected)

    def tryQuitImageSlideShow(self):
        # if self.imageSlideshow is not None: self.imageSlideshow.close()
        if self.imageSlideShowPlayFlag:
            self.imageSlideShowPlayFlag = not self.imageSlideShowPlayFlag
            self.selectedImageShownContainer.mImageShownWidget.controlSlideShow(self.imageSlideShowPlayFlag)

    def initLayoutParams(self, uiConfig):
        self.imageShownContainerLayout.getLayout().setContentsMargins(uiConfig.shownContainerMargins)
        self.imageShownContainerLayout.getLayout().setSpacing(uiConfig.shownContainerContentSpace)

    def initWidget(self):
        self.firstImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal, self.updateCrossViewSignal)
        self.secondImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal, self.updateCrossViewSignal)
        self.thirdImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal, self.updateCrossViewSignal)
        self.fourthImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal, self.updateCrossViewSignal)

        self.addWidget(self.firstImageShownContainer, 0, 0)
        self.addWidget(self.secondImageShownContainer, 0, 1)
        self.addWidget(self.thirdImageShownContainer, 1, 0)
        self.addWidget(self.fourthImageShownContainer, 1, 1)

        self.imageShownWidgetPool[(0, 0)] = self.firstImageShownContainer
        self.imageShownWidgetPool[(0, 1)] = self.secondImageShownContainer
        self.imageShownWidgetPool[(1, 0)] = self.thirdImageShownContainer
        self.imageShownWidgetPool[(1, 1)] = self.fourthImageShownContainer

        # self.crossXZContainer.update2DImageShownSignal.connect(self.controlCrossView)
        # self.crossYZContainer.update2DImageShownSignal.connect(self.controlCrossView)

    def addWidget(self, childWidget, row, col, rowSpan = 1, colSpan = 1):
        self.imageShownContainerLayout.getLayout().addWidget(childWidget, row, col, rowSpan, colSpan)

    def updateLayout(self, layoutTuple):
        if layoutTuple == self.curlayout: return
        self.curlayout = deepcopy(layoutTuple)

        topRow, leftCol, bottomRow, rightCol = layoutTuple

        #从Layout移除所有子Widget
        self.imageShownContainerLayout.clearLayout()

        #重新向Layout中添加子Widget
        rowSpan = uiConfig.toolsSelectRegionRow - bottomRow
        colSpan = uiConfig.toolsSelectRegionCol - rightCol
        for row in range(topRow, bottomRow + 1):
            for col in range(leftCol, rightCol + 1):
                childWidget = self.imageShownWidgetPool[(row, col)]
                self.addWidget(childWidget, row, col, rowSpan, colSpan)

    #crossView 逻辑控制
    def updateCrossViewSignalHandler(self, emitContainer):
        self.imageShownContainerLayout.mapWidgetsFunc(self.updateCrossViewSignalSCHandler, emitContainer)

    def updateCrossViewSignalSCHandler(self, handleContainer, emitContainerTuple):
        emitContainer, = emitContainerTuple
        if handleContainer is emitContainer\
            or handleContainer.curMode != SingleImageShownContainer.m2DMode\
            or len(handleContainer.imageData.curFilePath) < 1:return
        if emitContainer.curMode != SingleImageShownContainer.m2DMode:
            handleContainer.mImageShownWidget.tryHideCrossBoxWidget()
            return
        isSameStudy = checkSameStudy(handleContainer.imageData.curFilePath, emitContainer.imageData.curFilePath)
        isSameSeries = checkSameSeries(handleContainer.imageData.curFilePath, emitContainer.imageData.curFilePath)
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
        handleContainer.m2DImageShownData.showCrossFlag = True
        handleContainer.m2DImageShownData.crossViewRatios = crossViewPointRatios
        handleContainer.tryUpdateCrossBoxWidget()

    def calcCrossViewDisPos(self,handleContainer,emitContainer):
        #建立世界坐标系
        f1,f2 = handleContainer.imageData.curFilePath, emitContainer.imageData.curFilePath
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= self.getBasePosInfoFromDcm(f1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = self.getBasePosInfoFromDcm(f2)

        if (normalvector1 == normalvector2).all():
            #平面平行
            return Status.bad

        # ImageOrientationX1 = np.array([0.707,0,0.707])
        # normalvector1 = np.array([-0.707,0,0.707])
        # ImageOrientationX2 = np.array([0.707,0.707,0])
        # normalvector2 = np.array([-0.707,0.707,0])

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
        print("Rows1,Cols1 ",Rows1,Cols1)
        resDis = [QPoint(int(point.x() * kImgToDisW),int(point.y()*kImgToDisH)) + imageDisPos for point in res]

        #将绝对坐标转为相对ImageContainer的比例值
        size = handleContainer.mImageShownWidget.size()
        resDis = [(point.x() / size.width(),point.y() / size.height()) for point in resDis]

        return resDis

    def getBasePosInfoFromDcm(self, filePath):
        RefDs = pydicom.read_file(filePath)
        img_array = RefDs.pixel_array# indexes are z,y,x
        ImagePosition =np.array(RefDs.ImagePositionPatient,dtype=float)
        ImageOrientation=np.array(RefDs.ImageOrientationPatient,dtype = float)
        PixelSpacing =RefDs.PixelSpacing
        # SliceThickness=RefDs.SliceThickness
        ImageOrientationX=ImageOrientation[0:3]
        ImageOrientationY=ImageOrientation[3:6]
        Rows = RefDs.Rows
        Cols = RefDs.Columns
        #图像平面法向量(X与Y的叉积)
        normalvector=np.cross(ImageOrientationX,ImageOrientationY)
        return img_array,normalvector,ImagePosition,PixelSpacing,ImageOrientationX,ImageOrientationY,Rows,Cols

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
        # focal = m2DWidget.renImage.GetActiveCamera().GetFocalPoint()
        # m2DWidget.renImage.SetWorldPoint(focal[0],focal[1],focal[2],0)
        # m2DWidget.renImage.WorldToDisplay()
        # imageCenterPoint = m2DWidget.renImage.GetDisplayPoint()

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

        print("bounds: ",imageBoundPoint,imageBoundPoint2)
        imageBoundPoint = np.array(imageBoundPoint[:2])
        imageBoundPoint2 = np.array(imageBoundPoint2[:2])
        width,height = tuple(imageBoundPoint - imageBoundPoint2)
        pos = QPoint(imageBoundPoint2[0],imageBoundPoint2[1])
        print("左上角坐标：", pos,width,height)
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
        if not self.checkSelectContainerCanSlideShow():return
        if self.selectedImageShownContainer.mImageShownWidget.canSlideShow():
            self.imageSlideShowPlayFlag = not self.imageSlideShowPlayFlag
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
        if self.selectedImageShownContainer.curMode ==  mode:
            return
        self.selectedImageShownContainer.switchImageContainerMode(mode)

    #imageExtraInfo开关
    def imageExtraInfoStateHandler(self, isShow):
        self.selectedImageShownContainer.controlImageExtraInfoState(isShow)

    def closeEvent(self, QCloseEvent):
        self.firstImageShownContainer.closeEvent(QCloseEvent)
        self.secondImageShownContainer.closeEvent(QCloseEvent)
        self.thirdImageShownContainer.closeEvent(QCloseEvent)
        self.fourthImageShownContainer.closeEvent(QCloseEvent)
        if self.imageSlideshow is not None:self.imageSlideshow.closeEvent(QCloseEvent)

