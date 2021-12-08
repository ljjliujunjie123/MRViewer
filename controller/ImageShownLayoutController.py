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

class ImageShownLayoutController(QObject):

    selectImageShownContainerSignal = pyqtSignal(SingleImageShownContainer,bool)
    updateToolsContainerStateSignal = pyqtSignal(bool)
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
        self.imageSlideShowPlayFlag = False

    def selectImageShownContianerHandler(self, container, isSelected):
        if self.selectedImageShownContainer is not None:
            self.tryQuitImageSlideShow()
            self.selectedImageShownContainer.resetSelectState()
        if self.selectedImageShownContainer is container:
            print("select same")
            self.selectedImageShownContainer = None
        else:
            print("select different")
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
        self.firstImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal)
        self.secondImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal)
        self.thirdImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal)
        self.fourthImageShownContainer = SingleImageShownContainer(self.selectImageShownContainerSignal)

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

    def controlCrossView(self):
        crossXZFile = self.thirdImageShownContainer.curFilePath
        crossYZFile = self.fourthImageShownContainer.curFilePath

        if len(crossXZFile) < 1 or len(crossYZFile) < 1:return
        res = self.getCrossPos(crossXZFile, crossYZFile)
        if res == Status.bad: return
        self.thirdImageShownContainer.crossViewColRatio, self.thirdImageShownContainer.crossViewRowRatio, \
        self.fourthImageShownContainer.crossViewColRatio, self.fourthImageShownContainer.crossViewRowRatio = res

        self.thirdImageShownContainer.showCrossView()
        self.fourthImageShownContainer.showCrossView()

    def getinfo(self,img_file):
        RefDs = pydicom.read_file(img_file)
        img_array = RefDs.pixel_array# indexes are z,y,x
        ImagePosition =np.array(RefDs.ImagePositionPatient)
        ImageOrientation=np.array(RefDs.ImageOrientationPatient,dtype = int)
        PixelSpacing =RefDs.PixelSpacing
        SliceThickness=RefDs.SliceThickness
        ImageOrientationX=ImageOrientation[0:3]
        ImageOrientationY=ImageOrientation[3:6]

        Rows = RefDs.Rows
        Cols = RefDs.Columns

        #z轴(X与Y的叉积)
        normalvector=np.cross(ImageOrientationX,ImageOrientationY)
        return img_array,normalvector,ImagePosition,PixelSpacing,ImageOrientationX,ImageOrientationY,Rows,Cols

    def getCrossPos(self,f1,f2):
        #get info
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= self.getinfo(f1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = self.getinfo(f2)

        #建立方程组
        sp.init_printing(use_unicode=True)
        x, y, z = sp.symbols('x, y, z')
        eq=[normalvector1[0] * (x - ImagePosition1[0]) + normalvector1[1] * (y - ImagePosition1[1]) + normalvector1[2] * (z - ImagePosition1[2]),\
            normalvector2[0] * (x - ImagePosition2[0]) + normalvector2[1] * (y - ImagePosition2[1]) + normalvector2[2] * (z - ImagePosition2[2])]

         #解方程
        s = list(sp.linsolve(eq, [x, y, z]))
        if len(s) < 1: return Status.bad

        #求2d交线
        x, y, z = sp.symbols('x, y, z')
        x1_3d = s[0][0]
        y1_3d = s[0][1]
        z1_3d = s[0][2]

        pos=[x1_3d,y1_3d,z1_3d]

        differ1=pos-ImagePosition1
        differ1_x=np.dot(differ1,ImageOrientationX1)
        x1 = differ1_x/PixelSpacing1[0]
        differ1_y=np.dot(differ1,ImageOrientationY1)
        y1 = differ1_y/PixelSpacing1[1]

        differ2=pos-ImagePosition2
        differ2_x=np.dot(differ2,ImageOrientationX2)
        x2 = differ2_x/PixelSpacing2[0]
        differ2_y=np.dot(differ2,ImageOrientationY2)
        y2 = differ2_y/PixelSpacing2[1]

        #这样能拿到中心点坐标
        imageCenterPoint1,imageBoundPoint1 = self.getImageCenterAndBoundPos(self.thirdImageShownContainer)
        imageWidth1 = 2 * (imageBoundPoint1[0] - imageCenterPoint1[0])
        imageHeight1 = 2 * (imageBoundPoint1[1] - imageCenterPoint1[1])
        imageCenterPoint2,imageBoundPoint2 = self.getImageCenterAndBoundPos(self.fourthImageShownContainer)
        imageWidth2 = 2 * (imageBoundPoint2[0] - imageCenterPoint2[0])
        imageHeight2 = 2 * (imageBoundPoint2[1] - imageCenterPoint2[1])

        #计算Display坐标系的比例
        if sp.sign(x1) == 1:
            x1 = int((x1 / Cols1)*imageWidth1 + imageCenterPoint1[0] - imageWidth1/2) / self.thirdImageShownContainer.width()
        else: x1 = None
        if sp.sign(y1) == 1:
            y1 = int((y1 / Rows1)*imageHeight1 + imageCenterPoint1[1] - imageHeight1/2) / self.thirdImageShownContainer.height()
            y1 = 1 - y1
        else: y1 = None
        if sp.sign(x2) == 1:
            x2 = int((x2 / Cols2)*imageWidth2 + imageCenterPoint2[0] - imageWidth2/2) / self.fourthImageShownContainer.width()
        else: x2 = None
        if sp.sign(y2) == 1:
            y2 = int((y2 / Rows2)*imageHeight2 + imageCenterPoint2[1] - imageHeight2/2) / self.fourthImageShownContainer.height()
            y2 = 1 - y2
        else: y2 = None

        return (x1,y1,x2,y2)

    def getImageCenterAndBoundPos(self, m2DWidget):
        focal = m2DWidget.renImage.GetActiveCamera().GetFocalPoint()
        m2DWidget.renImage.SetWorldPoint(focal[0],focal[1],focal[2],0)
        m2DWidget.renImage.WorldToDisplay()
        imageCenterPoint = m2DWidget.renImage.GetDisplayPoint()

        bounds = m2DWidget.imageViewer.GetImageActor().GetBounds()
        colBound,rowBound = bounds[1],bounds[3]
        m2DWidget.renImage.SetWorldPoint(colBound,rowBound,focal[2],0)
        m2DWidget.renImage.WorldToDisplay()
        imageBoundPoint = m2DWidget.renImage.GetDisplayPoint()

        return (imageCenterPoint,imageBoundPoint)

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

    def closeEvent(self, QCloseEvent):
        self.firstImageShownContainer.closeEvent(QCloseEvent)
        self.secondImageShownContainer.closeEvent(QCloseEvent)
        self.thirdImageShownContainer.closeEvent(QCloseEvent)
        self.fourthImageShownContainer.closeEvent(QCloseEvent)
        if self.imageSlideshow is not None:self.imageSlideshow.closeEvent(QCloseEvent)

