from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame
from ui.config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
import vtkmodules.all as vtk
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom
from utils.cycleSyncThread import CycleSyncThread

class m2DImageShownWidget(QFrame, ImageShownWidgetInterface):

    sigWheelChanged = pyqtSignal(object)
    update2DImageShownSignal = pyqtSignal()

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None
        self.crossViewColRatio = 0
        self.crossViewRowRatio = 0
        #初始化逻辑
        self.reader = None
        self.imageViewer = None
        self.qvtkWidget = None
        self.renImage = None
        self.renText = None
        self.textActor = None

        self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)
        self.reader = vtk.vtkDICOMImageReader()
        self.imageViewer =  vtk.vtkImageViewer2()
        self.renImage = vtk.vtkRenderer()
        self.renText = vtk.vtkRenderer()
        self.textActor = vtk.vtkTextActor()

        self.timerThread = None

        self.sigWheelChanged.connect(self.wheelChangeEvent)

    def initBaseData(self, imageData):
        self.imageData = imageData

    def showAllViews(self):
        self.show2DImageVtkView()
        self.showImageExtraInfoVtkView()
        # self.showCrossView()
        self.renderVtkWindow()

    def show2DImageVtkView(self):
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetFileName(self.imageData.curFilePath)
        self.reader.Update()

        self.imageViewer.SetInputConnection(self.reader.GetOutputPort())
        level,width = getDicomWindowCenterAndLevel(self.imageData.curFilePath)
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
        #添加文本注释
        # self.textActor.SetTextScaleModeToProp()
        self.textActor.SetDisplayPosition(
            self.calcImageExtraInfoWidthPos(),
            self.calcImageExtraInfoHeightPos()
        )
        self.textActor.SetInput(getImageExtraInfoFromDicom(self.imageData.curFilePath))
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

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        print("resize: ",self.geometry())
        self.qvtkWidget.setFixedSize(self.size())
        # if self.resizeFlag:
        #     self.updateImageExtraInfo()

    #滚轮调用sigWheelChanged
    def wheelEvent(self, ev):
        if len(self.imageData.filePaths) <= 0:
            return
        print("wheelEvent")
        self.sigWheelChanged.emit(ev.angleDelta())

    #滚轮改变事件
    def wheelChangeEvent(self, angleDelta):
        self.setCurrentIndex(self.imageData.currentIndex+(angleDelta.y()//120))

    #切换到第ind张图
    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        #ind调节到可用范围
        print("set current index")
        ind %= len(self.imageData.filePaths)
        if ind < 0: 
            ind += len(self.imageData.filePaths)
        self.imageData.currentIndex = ind
        self.imageData.curFilePath = self.imageData.filePaths[self.imageData.currentIndex]
        self.showAllViews()
        self.update2DImageShownSignal.emit()

    def canSlideShow(self):
        return len(self.imageData.filePaths) > 0

    def setCurrentIndexMore(self, val):
        self.setCurrentIndex(self.imageData.currentIndex + 1)

    def controlSlideShow(self, flag):
        if flag:
            self.timerThread = CycleSyncThread(uiConfig.shownSlideSpeedDefault)
            self.timerThread.signal.connect(lambda x:self.setCurrentIndex(self.imageData.currentIndex + 1))
            self.timerThread.start()
        else:
            self.timerThread.requestInterruption()
            self.timerThread.quit()
            self.timerThread.wait()

    def controlSlideShowSpeed(self, delta):
        if self.timerThread is not None:
            newSpeed = self.timerThread.interval + delta
            newSpeed = max(min(newSpeed,uiConfig.shownSlideSpeedMin),uiConfig.shownSlideSpeedMax)
            self.timerThread.interval = newSpeed

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.qvtkWidget.Finalize()
        if self.timerThread is not None and not self.timerThread.isFinished():
            self.timerThread.requestInterruption()
            self.timerThread.quit()
            self.timerThread.wait()

    def clearViews(self):
        self.qvtkWidget.Finalize()