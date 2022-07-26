from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame
import os
from Config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from utils.BaseImageData import BaseImageData
from utils.cycleSyncThread import CycleSyncThread
import vtkmodules.all as vtk
from ErrorObserver import *

error_observer = ErrorObserver()

class mMock3DImageShownWidget(QFrame, ImageShownWidgetInterface):

    update2DImageShownSignal = pyqtSignal()
    updateCrossViewSubSignal = pyqtSignal()

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None
        self.path = uiConfig.mainPath
        self.imageShownData = None

        self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)

        self.iren = self.qvtkWidget.GetRenderWindow().GetInteractor()
        self.qvtkWidget.GetRenderWindow().SetInteractor(self.iren)

        self.reader = vtk.vtkNIFTIImageReader()
        self.imageViewer =  vtk.vtkImageViewer2()
        self.imageViewer.SetupInteractor(self.iren)
        self.renImage = vtk.vtkRenderer()
        self.renText = vtk.vtkRenderer()
        self.imageData = BaseImageData()
        self.initBaseData(self.path)
        self.flag = 0

    def initBaseData(self, imageData):
        self.imageData.seriesPath = self.path
        self.imageData.filePaths = [self.imageData.seriesPath + fileName for fileName in os.listdir(self.imageData.seriesPath)]
        self.imageData.seriesImageCount = len(self.imageData.filePaths)
        self.imageData.currentIndex = 0

    def showAllViews(self):
        self.timerThread = CycleSyncThread(0.01)
        self.timerThread.signal.connect(self.tryUpdate3DImageVtkView)
        self.timerThread.start()

    def tryUpdate3DImageVtkView(self):
        tmpFileNames = os.listdir(self.imageData.seriesPath)

        if len(tmpFileNames) > self.imageData.seriesImageCount:
            tmpFileNames.sort(key=lambda fn:os.path.getmtime(self.imageData.seriesPath + fn))
            self.imageData.seriesImageCount = len(tmpFileNames)
            self.imageData.curFilePath = self.imageData.seriesPath + tmpFileNames[-1]
            
            self.reader.SetFileName(self.imageData.curFilePath)
            # self.reader.SetFileNameSliceOffset(1)
            self.reader.SetDataByteOrderToBigEndian()
            self.reader.Update()
            if self.flag == 0:
                self.show3DImageVtkView()
                self.flag = 1

            self.imageData.currentIndex = self.imageData.currentIndex + 1
            self.renderVtkWindow()
            print("更新",tmpFileNames[-1], self.imageData.curFilePath)
            print("waiting")
        elif len(tmpFileNames) < self.imageData.seriesImageCount:
            self.initBaseData(self.path)

    def show3DImageVtkView(self):
        mapper = vtk.vtkGPUVolumeRayCastMapper()
        mapper.SetInputData(self.reader.GetOutput())

        volume = vtk.vtkVolume()
        volume.SetMapper(mapper)

        property = vtk.vtkVolumeProperty()

        popacity = vtk.vtkPiecewiseFunction()
        # popacity.AddPoint(-10000, 0.0)
        # popacity.AddPoint(0, 0.01)
        # popacity.AddPoint(4000, 0.01)
        # popacity.AddPoint(-100, 0.0)
        popacity.AddPoint(0, 0.0)
        popacity.AddPoint(0.2, 0.01)
        
        popacity.AddPoint(0.3, 0.3)
        # popacity.AddPoint(100, 0.1)

        # popacity.AddPoint(7000, 0.5)
        # volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        # volumeGradientOpacity.AddPoint(0, 0.0)
        # volumeGradientOpacity.AddPoint(-9999, 1.0)
        # volumeGradientOpacity.AddPoint(-10000, 0.0)
        color = vtk.vtkColorTransferFunction()
        color.AddHSVPoint(1000, 0.042, 0.73, 0.55)
        color.AddHSVPoint(2500, 0.042, 0.73, 0.55, 0.5, 0.92)
        color.AddHSVPoint(4000, 0.088, 0.67, 0.88)
        color.AddHSVPoint(5500, 0.088, 0.67, 0.88, 0.33, 0.45)
        color.AddHSVPoint(7000, 0.95, 0.063, 1.0)

        property.SetColor(color)
        property.SetScalarOpacity(popacity)
        # property.SetGradientOpacity(volumeGradientOpacity)
        property.ShadeOn()
        property.SetInterpolationTypeToLinear()
        property.SetShade(0, 1)
        property.SetDiffuse(0.9)
        property.SetAmbient(0.1)
        property.SetSpecular(0.2)
        property.SetSpecularPower(10.0)
        property.SetComponentWeight(0, 1)
        property.SetDisableGradientOpacity(1)
        property.DisableGradientOpacityOn()
        property.SetScalarOpacityUnitDistance(0.891927)

        volume.SetProperty(property)

        # ren = vtk.vtkRenderer()
        self.renImage.AddActor(volume)
        # self.renImage.SetBackground(1,1,1)
        self.renImage.SetBackground(0.5, 0.6, 0.8)

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)
        self.vtkStyle = vtk.vtkInteractorStyleTrackballCamera()
        self.vtkStyle.SetDefaultRenderer(self.renImage)
        self.iren.SetInteractorStyle(self.vtkStyle)
        self.iren.SetRenderWindow(self.qvtkWidget.GetRenderWindow())
        self.qvtkWidget.GetRenderWindow().Render()
        self.iren.Start()

    def renderVtkWindow(self, layerCount = 1):
        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)
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