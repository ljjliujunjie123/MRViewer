import os
from ui.AbstractImageShownWidget import AbstractImageShownWidget
from ui.config import uiConfig
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom

class m2DImageShownWidget(AbstractImageShownWidget):

    def __init__(self):
        AbstractImageShownWidget.__init__(self)
        #初始化GUI配置
        # self.setFixedSize(500,500)
        #初始化数据
        self.seriesPath = ""
        self.filePaths = []
        self.curFilePath = ""
        self.text = "2D"
        #初始化逻辑
        self.update2DImageShownSignal = None
        self.reader = None
        self.imageViewer = None
        self.qvtkWidget = None
        self.renImage = None
        self.renText = None
        self.textActor = None

    def show2DImageVtkView(self):
        if self.qvtkWidget is None:self.qvtkWidget = QVTKRenderWindowInteractor(self)
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
        if self.qvtkWidget is None:self.qvtkWidget = QVTKRenderWindowInteractor(self)
        if self.renText is None:self.renText = vtk.vtkRenderer()
        if self.textActor is None:self.textActor = vtk.vtkTextActor()

        #添加文本注释
        # self.textActor.SetTextScaleModeToProp()
        self.textActor.SetDisplayPosition(
            self.calcImageExtraInfoWidthPos(),
            self.calcImageExtraInfoHeightPos()
        )
        self.textActor.SetInput(self.text)
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

    def renderVtkWindow(self):
        self.qvtkWidget.setFixedSize(self.size())
        self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(2)
        self.qvtkWidget.GetRenderWindow().Render()

        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)

    def updateImageExtraInfo(self):
        self.showImageExtraInfoVtkView(self.text)
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

        self.text = getImageExtraInfoFromDicom(self.curFilePath)

        print("showXZDicom begin")
        self.showImageExtraInfoVtkView()
        self.show2DImageVtkView()
        self.renderVtkWindow()
        print("showXZDicom end")

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        print("resize: ",self.geometry())
        if self.resizeFlag:
            self.updateImageExtraInfo()