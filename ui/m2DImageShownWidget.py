import os
from ui.AbstractImageShownWidget import AbstractImageShownWidget
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

        self.initVtkSupportObjects()

    def initVtkSupportObjects(self):
        self.qvtkWidget = QVTKRenderWindowInteractor(self)
        self.qvtkWidget.setFixedSize(self.size())

        self.renImage = vtk.vtkRenderer()
        self.renText = vtk.vtkRenderer()

        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDataByteOrderToLittleEndian()

        self.textActor = vtk.vtkTextActor()
        # self.textActor.GetActualPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
        # self.textActor.GetPosition2Coordinate().SetValue(0.6, 0.1)
        self.textActor.GetTextProperty().SetFontSize(20)
        # self.textActor.GetTextProperty().SetFontFamilyToArial()
        # self.textActor.GetTextProperty().SetJustificationToCentered()
        self.textActor.GetTextProperty().BoldOn()
        # self.textActor.GetTextProperty().ItalicOn()
        self.textActor.GetTextProperty().ShadowOn()
        self.textActor.GetTextProperty().SetColor(1, 1, 1)

        self.imageViewer =  vtk.vtkImageViewer2()
        self.imageViewer.SetInputConnection(self.reader.GetOutputPort())
        self.imageViewer.SetRenderer(self.renImage)
        self.imageViewer.SetRenderWindow(self.qvtkWidget.GetRenderWindow())

    def show2DImageVtkView(self, filePath):
        self.reader.SetFileName(filePath)
        self.reader.Update()

        level,width = getDicomWindowCenterAndLevel(filePath)
        self.imageViewer.SetColorLevel(level)
        self.imageViewer.SetColorWindow(width)
        self.imageViewer.UpdateDisplayExtent()

        self.renImage.SetLayer(0)
        self.renImage.ResetCamera()

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)

    def showImageExtraInfoVtkView(self, text):
        # self.textActor.SetTextScaleModeToProp()
        self.updateImageExtraInfoPos()
        self.textActor.SetInput(self.text)

        self.renText.SetLayer(1)
        self.renText.AddViewProp(self.textActor)

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renText)

    def updateImageExtraInfoPos(self):
        self.textActor.SetDisplayPosition(
            self.calcImageExtraInfoWidthPos(),
            self.calcImageExtraInfoHeightPos()
        )

    # def hideImageExtraInfo(self):
    #     self.qvtkWidget.GetRenderWindow().RemoveRenderer(self.renText)
    #     self.renderVtkWindow(1)

    def calcImageExtraInfoWidthPos(self):
        return 10

    def calcImageExtraInfoHeightPos(self):
        return 10

    def renderVtkWindow(self, layerCount):
        self.imageViewer.SetupInteractor(self.qvtkWidget.GetRenderWindow().GetInteractor())

        self.qvtkWidget.setFixedSize(self.size())
        self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(layerCount)
        self.qvtkWidget.GetRenderWindow().Render()

        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        print("resize: ",self.geometry())
        if self.resizeFlag:
            self.updateImageExtraInfoPos()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.seriesPath = event.mimeData().getImageExtraData()["seriesPath"]
        event.mimeData().setText("")
        fileNames = os.listdir(self.seriesPath)
        self.filePaths = [self.seriesPath + '/' + fileName for fileName in fileNames]
        self.curFilePath = self.filePaths[0]

        self.text = getImageExtraInfoFromDicom(self.curFilePath)

        print("showXZDicom begin")
        self.show2DImageVtkView(self.curFilePath)
        self.showImageExtraInfoVtkView(self.text)
        self.renderVtkWindow(2)
        print("showXZDicom end")