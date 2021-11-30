from PyQt5.QtCore import pyqtSignal
import os
from ui.AbstractImageShownWidget import AbstractImageShownWidget
from ui.config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
import vtkmodules.all as vtk
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom

class m2DImageShownWidget(AbstractImageShownWidget):

    sigWheelChanged = pyqtSignal(object)
    update2DImageShownSignal = pyqtSignal()

    def __init__(self):
        AbstractImageShownWidget.__init__(self)
        #初始化GUI配置
        # self.setFixedSize(500,500)
        #初始化数据
        self.seriesPath = ""
        self.filePaths = []
        self.curFilePath = ""
        self.currentIndex = 0
        self.crossViewColRatio = 0
        #初始化逻辑
        self.reader = None
        self.imageViewer = None
        self.qvtkWidget = None
        self.renImage = None
        self.renText = None
        self.textActor = None

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
        if self.qvtkWidget is None:self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)
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
        self.crossView = vtk.vtkBorderWidget()
        self.crossView.SetInteractor(self.qvtkWidget.GetRenderWindow().GetInteractor())
        self.crossView.CreateDefaultRepresentation()
        self.crossView.GetRepresentation().SetPosition(self.crossViewColRatio,0.05)
        self.crossView.GetRepresentation().SetPosition2(0.01,0.9)
        self.crossView.GetRepresentation().GetBorderProperty().SetColor(1,0,0)
        self.crossView.GetRepresentation().GetBorderProperty().SetLineWidth(3)
        self.crossView.ResizableOff()
        # self.crossView.SelectableOff() 设置是否可拖动
        self.crossView.On()
        # self.renCrossView = vtk.vtkRenderer()
        # self.renCrossView.SetLayer(1)
        # self.crossView.SetCurrentRenderer(self.renCrossView)
        # self.qvtkWidget.GetRenderWindow().AddRenderer(self.renCrossView)
        self.renderVtkWindow()

    def renderVtkWindow(self):
        self.qvtkWidget.setFixedSize(self.size())
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

    def wheelEvent(self, ev):
        print("wheelEvent")
        self.sigWheelChanged.emit(ev.angleDelta())

    def wheelChangeEvent(self, angleDelta):
        self.setCurrentIndex(self.currentIndex+(angleDelta.y()//120))
        # print(angleDelta.y()//120)
        # print(self.currentIndex+(angleDelta.y()//120))

    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        while ind >= len(self.filePaths): ind = ind - len(self.filePaths)
        while ind < 0: ind = ind + len(self.filePaths)
        self.curFilePath = self.filePaths[ind]
        self.currentIndex = ind
        self.show2DImageVtkView()
        self.showImageExtraInfoVtkView()
        self.update2DImageShownSignal.emit()
        self.renderVtkWindow()
        print("setIndex")