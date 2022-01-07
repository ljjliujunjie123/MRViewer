from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame
import os
from ui.config import uiConfig
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from utils.BaseImageData import BaseImageData
from utils.cycleSyncThread import CycleSyncThread
import vtkmodules.all as vtk
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom,getImageTileInfoFromDicom
from utils.cycleSyncThread import CycleSyncThread

class mRealTimeImageShownWidget(QFrame, ImageShownWidgetInterface):

    update2DImageShownSignal = pyqtSignal()
    updateCrossViewSubSignal = pyqtSignal()

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None
        #初始化逻辑
        self.imageShownData = None

        self.qvtkWidget = QVTKRenderWindowInteractor(self)
        self.iren = self.qvtkWidget.GetRenderWindow().GetInteractor()
        self.qvtkWidget.GetRenderWindow().SetInteractor(self.iren)
        self.vtkStyle = vtk.vtkInteractorStyleImage()
        self.iren.SetInteractorStyle(self.vtkStyle)
        self.reader = vtk.vtkDICOMImageReader()
        self.imageViewer =  vtk.vtkImageViewer2()
        self.imageViewer.SetupInteractor(self.iren)
        self.renImage = vtk.vtkRenderer()
        self.renText = vtk.vtkRenderer()

    def initBaseData(self, imageData):
        self.imageData = BaseImageData()
        self.imageData.seriesPath = r'/zzNAS/Projects/RealtimeMRI/outputs/dicom_ljj'
        # self.imageData.seriesPath = r'D:\respository\MRViewer_Scource\mock_folder'
        self.imageData.filePaths = [self.imageData.seriesPath + '/' + fileName for fileName in os.listdir(self.imageData.seriesPath)]
        self.imageData.seriesImageCount = len(self.imageData.filePaths)
        self.imageData.currentIndex = 0

    def showAllViews(self):
        self.timerThread = CycleSyncThread(0.05)
        self.timerThread.signal.connect(self.tryUpdate2DImageVtkView)
        self.timerThread.start()

    def tryUpdate2DImageVtkView(self):
        tmpFileNames = os.listdir(self.imageData.seriesPath)
        if len(tmpFileNames) > self.imageData.seriesImageCount:
            print(tmpFileNames)
            self.imageData.seriesImageCount = len(tmpFileNames)
            self.imageData.currentIndex = self.imageData.seriesImageCount - 1
            self.imageData.curFilePath = self.imageData.seriesPath + '/' + tmpFileNames[-1]
            self.show2DImageVtkView()
            self.renderVtkWindow()
            print("更新",tmpFileNames[-1], self.imageData.curFilePath)

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

        self.renImage.SetLayer(0)
        self.renImage.ResetCamera()

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)

    def renderVtkWindow(self, layerCount = 1):
        self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(layerCount)
        self.qvtkWidget.Initialize()
        self.qvtkWidget.Start()
        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)

    def clearViews(self):
        self.timerThread.requestInterruption()
        self.timerThread.quit()
        self.qvtkWidget.Finalize()

    def resizeEvent(self, *args, **kwargs):
        self.qvtkWidget.setFixedSize(self.size())
