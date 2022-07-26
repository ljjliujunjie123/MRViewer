from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame
import os
from Config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from utils.BaseImageData import BaseImageData
from utils.cycleSyncThread import CycleSyncThread
import vtkmodules.all as vtk

class mRealTimeImageShownWidget(QFrame, ImageShownWidgetInterface):

    update2DImageShownSignal = pyqtSignal()
    updateCrossViewSubSignal = pyqtSignal()

    def __init__(self, path):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None
        self.path = path
        self.imageShownData = None

        self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)
        self.iren = self.qvtkWidget.GetRenderWindow().GetInteractor()
        self.qvtkWidget.GetRenderWindow().SetInteractor(self.iren)
        self.vtkStyle = vtk.vtkInteractorStyleImage()
        self.iren.SetInteractorStyle(self.vtkStyle)
        self.reader = vtk.vtkDICOMImageReader()
        self.imageViewer =  vtk.vtkImageViewer2()
        self.imageViewer.SetupInteractor(self.iren)
        self.renImage = vtk.vtkRenderer()
        self.renText = vtk.vtkRenderer()
        self.imageData = BaseImageData()
        self.initBaseData(self.path)
        self.flag = 0

    def initBaseData(self, imageData):
        self.imageData.seriesPath = self.path #r'/home/zhongsijie/MRViewer_old/mock_dicoms'
        # self.imageData.seriesPath = r'E:/research/MRViewer_test/MRNewUI/mock_dicoms'
        self.imageData.filePaths = [self.imageData.seriesPath + '/' + fileName for fileName in os.listdir(self.imageData.seriesPath)]
        self.imageData.seriesImageCount = len(self.imageData.filePaths)
        self.imageData.currentIndex = 0

    def showAllViews(self):
        self.timerThread = CycleSyncThread(0.01)
        self.timerThread.signal.connect(self.tryUpdate2DImageVtkView)
        self.timerThread.start()

    def tryUpdate2DImageVtkView(self):
        tmpFileNames = os.listdir(self.imageData.seriesPath)

        if len(tmpFileNames) > self.imageData.seriesImageCount:
            tmpFileNames.sort(key=lambda fn:os.path.getmtime(self.imageData.seriesPath + "/" + fn))
            self.imageData.seriesImageCount = len(tmpFileNames)
            self.imageData.curFilePath = self.imageData.seriesPath + '/' + tmpFileNames[-1]
            if self.flag == 0:
                self.show2DImageVtkView()
                self.flag = 1
            else:
                self.reader.SetFileName(self.imageData.curFilePath)
                self.reader.Update()
            self.imageData.currentIndex = self.imageData.currentIndex + 1
            self.renderVtkWindow()
            print("更新",tmpFileNames[-1], self.imageData.curFilePath)
            print("waiting")
        elif len(tmpFileNames) < self.imageData.seriesImageCount:
            self.initBaseData(self.path)

    def show2DImageVtkView(self):
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetFileName(self.imageData.curFilePath)
        self.reader.Update()

        self.imageViewer.SetInputConnection(self.reader.GetOutputPort())
        self.imageViewer.SetColorLevel(5000)
        self.imageViewer.SetColorWindow(10000)
        self.imageViewer.SetRenderer(self.renImage)
        self.imageViewer.SetRenderWindow(self.qvtkWidget.GetRenderWindow())
        self.imageViewer.UpdateDisplayExtent()

        self.renImage.SetLayer(0)
        self.renImage.ResetCamera()
        self.renImage.GetActiveCamera().Roll(180)

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

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.qvtkWidget.setFixedSize(self.size())

    def closeEvent(self, QCloseEvent):
            super().closeEvent(QCloseEvent)
            self.qvtkWidget.Finalize()