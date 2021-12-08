from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
import os
from ui.AbstractImageShownWidget import AbstractImageShownWidget
from ui.config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
import vtkmodules.all as vtk
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom,getImageTileInfoFromDicom
from utils.cycleSyncThread import CycleSyncThread

class m2DImageShownWidget(AbstractImageShownWidget):

    sigWheelChanged = pyqtSignal(object)
    update2DImageShownSignal = pyqtSignal()

    def __init__(self):
        AbstractImageShownWidget.__init__(self)
        #初始化GUI配置
        self.setTileText("This is a 2D series list.")
        #初始化数据
        self.seriesPath = ""
        self.filePaths = []
        self.curFilePath = ""
        self.currentIndex = 0
        self.crossViewColRatio = 0
        self.crossViewRowRatio = 0
        #初始化逻辑
        self.reader = None
        self.imageViewer = None
        self.qvtkWidget = None
        self.renImage = None
        self.renText = None
        self.textActor = None

        self.timerThread = None

        self.sigWheelChanged.connect(self.wheelChangeEvent)

    def show2DImageVtkView(self):
        if self.qvtkWidget is None:self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)
        if self.reader is None: self.reader = vtk.vtkDICOMImageReader()
        if self.imageViewer is None:self.imageViewer =  vtk.vtkImageViewer2()
        if self.renImage is None:self.renImage = vtk.vtkRenderer()
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetFileName(self.curFilePath)
        self.reader.Update()

        self.imageViewer.SetInputConnection(self.reader.GetOutputPort())
        level,width = getDicomWindowCenterAndLevel(self.curFilePath)
        self.imageViewer.SetColorLevel(level)
        self.imageViewer.SetColorWindow(width)
        self.imageViewer.SetRenderer(self.renImage)
        self.imageViewer.SetRenderWindow(self.qvtkWidget.GetRenderWindow())
        self.imageViewer.UpdateDisplayExtent()
        self.imageViewer.SetupInteractor(self.qvtkWidget.GetRenderWindow().GetInteractor())

        self.renImage.SetLayer(0)
        self.renImage.ResetCamera()

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)

    def showImageExtraInfoVtkView(self):
        if self.qvtkWidget is None:self.qvtkWidget = CustomQVTKRenderWindowInteractor(self.imageContainer)
        if self.renText is None:self.renText = vtk.vtkRenderer()
        if self.textActor is None:self.textActor = vtk.vtkTextActor()

        #添加文本注释
        # self.textActor.SetTextScaleModeToProp()
        self.textActor.SetDisplayPosition(
            self.calcImageExtraInfoWidthPos(),
            self.calcImageExtraInfoHeightPos()
        )
        self.textActor.SetInput(getImageExtraInfoFromDicom(self.curFilePath))
        # self.textActor.GetActualPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
        # self.textActor.GetPosition2Coordinate().SetValue(0.6, 0.1)
        self.textActor.GetTextProperty().SetFontSize(20)
        # self.textActor.GetTextProperty().SetFontFamilyToArial()
        # self.textActor.GetTextProperty().SetJustificationToCentered()
        self.textActor.GetTextProperty().BoldOn()
        # self.textActor.GetTextProperty().ItalicOn()
        self.textActor.GetTextProperty().ShadowOn()
        self.textActor.GetTextProperty().SetColor(1, 1, 1)

        self.renText.SetLayer(1)
        self.renText.AddViewProp(self.textActor)

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renText)

    def showCrossView(self):
        #方法一
        # self.crossView = CustomCrossBoxWidget()
        # self.crossView.setParent(self)
        # self.crossView.raise_()
        # self.crossView.show()
        #方法二
        # if self.crossView is None: self.crossView = vtk.vtkBoxWidget()
        # self.crossView.SetInteractor(self.qvtkWidget.GetRenderWindow().GetInteractor())
        # # self.crossView.CreateDefaultRepresentation()
        # self.renCrossView = vtk.vtkRenderer()
        # self.renCrossView.SetLayer(1)
        # self.crossView.SetCurrentRenderer(self.renCrossView)
        # self.qvtkWidget.GetRenderWindow().AddRenderer(self.renCrossView)
        # self.crossView.On()
        # self.renderVtkWindow()
        #方法三
        self.crossView = vtk.vtkBorderWidget()
        self.crossView.SetInteractor(self.qvtkWidget.GetRenderWindow().GetInteractor())
        self.crossView.CreateDefaultRepresentation()
        if self.crossViewColRatio is not None:
            self.crossView.GetRepresentation().SetPosition(self.crossViewColRatio,0.05)
            self.crossView.GetRepresentation().SetPosition2(0.01,0.9)
        elif self.crossViewRowRatio is not None:
            self.crossView.GetRepresentation().SetPosition(0.05,self.crossViewRowRatio)
            self.crossView.GetRepresentation().SetPosition2(0.9,0.01)
        self.crossView.GetRepresentation().GetBorderProperty().SetColor(1,0,0)
        self.crossView.GetRepresentation().GetBorderProperty().SetLineWidth(3)
        self.crossView.GetRepresentation().SetMinimumSize(100, 100)
        self.crossView.GetRepresentation().SetMaximumSize(200, 200)
        self.crossView.ResizableOn()
        self.crossView.SelectableOff()
        self.crossView.On()
        self.renderVtkWindow()

    def renderVtkWindow(self):
        self.qvtkWidget.setFixedSize(self.imageContainer.size())
        self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(2)
        self.qvtkWidget.GetRenderWindow().Render()

        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)

    def updateImageExtraInfo(self):
        self.showImageExtraInfoVtkView()
        self.renText.Render()

    def calcImageExtraInfoWidthPos(self):
        return uiConfig.shownTextInfoMarginWidth

    def calcImageExtraInfoHeightPos(self):
        return uiConfig.shownTextInfoMarginHeight

    def dropEvent(self, event):
        super().dropEvent(event)
        self.seriesPath = event.mimeData().getImageExtraData()["seriesPath"]
        event.mimeData().setText("")
        fileNames = os.listdir(self.seriesPath)
        self.filePaths = [self.seriesPath + '/' + fileName for fileName in fileNames]
        self.curFilePath = self.filePaths[0]
        self.currentIndex = 0

        print("showXZDicom begin")
        self.setTileText(getImageTileInfoFromDicom(self.curFilePath))
        self.showImageExtraInfoVtkView()
        self.show2DImageVtkView()
        self.update2DImageShownSignal.emit()
        self.renderVtkWindow()
        print("showXZDicom end")

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        print("resize: ",self.geometry())
        if self.resizeFlag:
            self.updateImageExtraInfo()

    #滚轮调用sigWheelChanged
    def wheelEvent(self, ev):
        if len(self.filePaths) <= 0:
            return
        print("wheelEvent")
        self.sigWheelChanged.emit(ev.angleDelta())

    #滚轮改变事件
    def wheelChangeEvent(self, angleDelta):
        self.setCurrentIndex(self.currentIndex+(angleDelta.y()//120))

    #切换到第ind张图
    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        #ind调节到可用范围
        print("set current index")
        ind = ind % len(self.filePaths)
        if ind < 0: 
            ind = ind + len(self.filePaths)
        self.currentIndex = ind
        self.curFilePath = self.filePaths[self.currentIndex]
        self.show2DImageVtkView()
        self.showImageExtraInfoVtkView()
        self.update2DImageShownSignal.emit()
        self.renderVtkWindow()
        #print("setIndex")

    def canSlideShow(self):
        if self.qvtkWidget is None:
            return False
        if len(self.filePaths) <= 0:
            return False
        return True

    def setCurrentIndexMore(self, val):
        self.setCurrentIndex(self.currentIndex + 1)

    def controlSlideShow(self, flag):
        if flag:
            self.timerThread = CycleSyncThread(0.3)
            self.timerThread.signal.connect(lambda x:self.setCurrentIndex(self.currentIndex + 1))
            self.timerThread.start()
        else:
            self.timerThread.requestInterruption()
            self.timerThread.quit()
            self.timerThread.wait()

    def controlSlideShowSpeed(self, delta):
        if self.timerThread is not None:
            newSpeed = self.timerThread.interval + delta
            newSpeed = max(min(newSpeed,1),0.1)
            self.timerThread.interval = newSpeed

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.timerThread is not None and not self.timerThread.isFinished():
            self.timerThread.requestInterruption()
            self.timerThread.quit()
            self.timerThread.wait()