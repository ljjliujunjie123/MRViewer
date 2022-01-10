import os
import numpy as np
import pydicom
from PyQt5.QtWidgets import QFrame
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from utils.util import getDicomWindowCenterAndLevel,getImageTileInfoFromDicom

class m3DImageShownWidget(QFrame, ImageShownWidgetInterface):

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None
        #初始化逻辑
        self.qvtkWidget = QVTKRenderWindowInteractor(self)
        self.axes_widget = vtk.vtkOrientationMarkerWidget()

    def resizeEvent(self, *args, **kwargs):
        self.qvtkWidget.setFixedSize(self.size())

    def showAllViews(self):
        self.show3DImage(self.imageData.seriesPath)

    def show3DImage(self, seriesPath):
        print("show 3D Dicom Window Begin")
        ren3D = vtk.vtkRenderer()
        renWin = self.qvtkWidget.GetRenderWindow()
        renWin.AddRenderer(ren3D)

        # 设置交互方式
        self.iren = renWin.GetInteractor()  # 获取交互器
        self.style = vtk.vtkInteractorStyleTrackballCamera()  # 交互器样式的一种，该样式下，用户是通过控制相机对物体作旋转、放大、缩小等操作
        self.style.SetDefaultRenderer(ren3D)
        self.iren.SetInteractorStyle(self.style)
        # 添加世界坐标系
        axesActor = vtk.vtkAnnotatedCubeActor()
        # ren3D.AddActor(axesActor)
        # 注意这里设置的值是屏幕坐标系下的方位值，并不是解剖学上的方位
        axesActor.SetXPlusFaceText("L")
        axesActor.SetXMinusFaceText("R")
        axesActor.SetYMinusFaceText("I")
        axesActor.SetYPlusFaceText("S")
        axesActor.SetZMinusFaceText("P")
        axesActor.SetZPlusFaceText("A")
        axesActor.SetXFaceTextRotation(-90)
        axesActor.SetYFaceTextRotation(180)
        axesActor.SetZFaceTextRotation(90)
        axesActor.GetTextEdgesProperty().SetColor(1,0,0)
        axesActor.GetTextEdgesProperty().SetLineWidth(2)
        axesActor.GetCubeProperty().SetColor(0,0,1)
        self.axes_widget.SetOrientationMarker(axesActor)
        self.axes_widget.SetInteractor(self.iren)
        self.axes_widget.EnabledOn()
        self.axes_widget.InteractiveOn()  # 坐标系是否可移动
        v16 = vtk.vtkDICOMImageReader()
        v16.SetDirectoryName(seriesPath)
        v16.Update()

        shrink = vtk.vtkImageShrink3D()
        shrink.SetShrinkFactors(1,1,4)
        shrink.AveragingOn()
        shrink.SetInputConnection(v16.GetOutputPort())
        shrink.Update()

        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(shrink.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()

        volumeColor = vtk.vtkColorTransferFunction()
        volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
        volumeColor.AddRGBPoint(500,  1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)

        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(0,    0.00)
        volumeScalarOpacity.AddPoint(500,  0.15)
        volumeScalarOpacity.AddPoint(1000, 0.15)
        volumeScalarOpacity.AddPoint(1150, 0.85)

        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0,   0.0)
        volumeGradientOpacity.AddPoint(90,  0.5)
        volumeGradientOpacity.AddPoint(100, 1.0)

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        # volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.9)
        volumeProperty.SetDiffuse(0.9)
        volumeProperty.SetSpecular(0.9)

        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)

        ren3D.AddViewProp(volume)
        ren3D.ResetCamera()
        # camera = ren3D.GetActiveCamera()
        # c = volume.GetCenter()
        # camera.SetFocalPoint(c[0], c[1], c[2])
        # camera.SetPosition(c[0] + 400, c[1], c[2])
        # camera.SetViewUp(0, 0, -1)
        # Interact with the data.
        self.qvtkWidget.Initialize()
        renWin.Render()
        self.qvtkWidget.Start()

        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)
        print("show 3D Dicom Window End")

    def initBaseData(self, imageData):
        self.imageData = imageData

    def clearViews(self):
        self.qvtkWidget.Finalize()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.qvtkWidget.Finalize()