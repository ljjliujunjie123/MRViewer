from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from utils.util import getDicomWindowCenterAndLevel

class ImageShownContainer(QFrame):

    filePath = r'D:\respository\MRViewer_Scource\dicom_for_UItest\3D_vessel_phantom_transversal'

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(QRect(600, 0, 1000, 1000))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageShownContainer")

        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1000, 1000))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.imageGridShownContainer = QGridLayout(self.gridLayoutWidget)
        self.imageGridShownContainer.setContentsMargins(0,0,0,0)
        self.imageGridShownContainer.setSpacing(10)
        self.imageGridShownContainer.setObjectName("imageGridShownContainer")

        self.RealTimeContainer = QWidget(self.gridLayoutWidget)
        self.RealTimeContainer.setGeometry(0,0,500,500)
        self.RealTimeContainer.setFixedSize(500,500)
        self.RealTimeContainer.setObjectName("RealTimeContainer")
        self.imageGridShownContainer.addWidget(self.RealTimeContainer, 0, 0, 1, 1)

        self.vtk3DContainer = QWidget(self.gridLayoutWidget)
        self.vtk3DContainer.setGeometry(250,0,500,500)
        self.vtk3DContainer.setFixedSize(500,500)
        self.vtk3DContainer.setObjectName("vtk3DContainer")
        self.imageGridShownContainer.addWidget(self.vtk3DContainer, 0, 1, 1, 1)

        self.crossXZContainer = QWidget(self.gridLayoutWidget)
        self.crossXZContainer.setGeometry(0,250,500,500)
        self.crossXZContainer.setFixedSize(500,500)
        self.crossXZContainer.setObjectName("crossXZContainer")
        self.imageGridShownContainer.addWidget(self.crossXZContainer, 1, 0, 1, 1)

        self.crossYZContainer = QWidget(self.gridLayoutWidget)
        self.crossYZContainer.setGeometry(250,250,500,500)
        self.crossYZContainer.setFixedSize(500,500)
        self.crossYZContainer.setObjectName("crossYZContainer")
        self.imageGridShownContainer.addWidget(self.crossYZContainer, 1, 1, 1, 1)

        self.initDicomWindows()

    def initDicomWindows(self):
        self.readerXZ = None
        self.imageViewerXZ = None
        self.renXZ = None
        self.qvtkWidgetXZ = None

        self.readerYZ = None
        self.imageViewerYZ = None
        self.renYZ = None
        self.qvtkWidgetYZ = None

        self.vtk3DLayout = None
        self.vtk3DWidget = None
        self.ren3D = None

    def showXZDicom(self, fileName):
        print("showXZDicom begin")
        if self.readerXZ is None:self.readerXZ = vtk.vtkDICOMImageReader()
        self.readerXZ.SetDataByteOrderToLittleEndian()
        self.readerXZ.SetFileName(fileName)
        self.readerXZ.Update()

        if self.imageViewerXZ is None:self.imageViewerXZ =  vtk.vtkImageViewer2()
        self.imageViewerXZ.SetInputConnection(self.readerXZ.GetOutputPort())
        level,width = getDicomWindowCenterAndLevel(fileName)
        self.imageViewerXZ.SetColorLevel(level)
        self.imageViewerXZ.SetColorWindow(width)

        if self.renXZ is None:self.renXZ = vtk.vtkRenderer()

        if self.qvtkWidgetXZ is None:self.qvtkWidgetXZ = QVTKRenderWindowInteractor(self.crossXZContainer)
        self.qvtkWidgetXZ.setFixedSize(self.crossXZContainer.size())
        self.qvtkWidgetXZ.GetRenderWindow().AddRenderer(self.renXZ)

        self.imageViewerXZ.SetRenderer(self.renXZ)
        self.imageViewerXZ.SetRenderWindow(self.qvtkWidgetXZ.GetRenderWindow())
        self.imageViewerXZ.UpdateDisplayExtent()
        self.imageViewerXZ.SetupInteractor(self.qvtkWidgetXZ.GetRenderWindow().GetInteractor())

        self.renXZ.ResetCamera()
        self.qvtkWidgetXZ.GetRenderWindow().Render()

        if not self.qvtkWidgetXZ.isVisible(): self.qvtkWidgetXZ.setVisible(True)
        print("showXZDicom end")

    def showYZDicom(self, fileName):
        print("showYZDicom begin")
        if self.readerYZ is None: self.readerYZ = vtk.vtkDICOMImageReader()
        self.readerYZ.SetDataByteOrderToLittleEndian()
        self.readerYZ.SetFileName(fileName)
        self.readerYZ.Update()

        if self.imageViewerYZ is None: self.imageViewerYZ =  vtk.vtkImageViewer2()
        self.imageViewerYZ.SetInputConnection(self.readerYZ.GetOutputPort())
        level,width = getDicomWindowCenterAndLevel(fileName)
        self.imageViewerYZ.SetColorLevel(level)
        self.imageViewerYZ.SetColorWindow(width)

        if self.renYZ is None: self.renYZ = vtk.vtkRenderer()

        if self.qvtkWidgetYZ is None: self.qvtkWidgetYZ = QVTKRenderWindowInteractor(self.crossYZContainer)
        self.qvtkWidgetYZ.setFixedSize(self.crossYZContainer.size())
        self.qvtkWidgetYZ.GetRenderWindow().AddRenderer(self.renYZ)

        self.imageViewerYZ.SetRenderer(self.renYZ)
        self.imageViewerYZ.SetRenderWindow(self.qvtkWidgetYZ.GetRenderWindow())
        self.imageViewerYZ.UpdateDisplayExtent()
        self.imageViewerYZ.SetupInteractor(self.qvtkWidgetYZ.GetRenderWindow().GetInteractor())

        self.renYZ.ResetCamera()
        self.qvtkWidgetYZ.GetRenderWindow().Render()

        if not self.qvtkWidgetYZ.isVisible(): self.qvtkWidgetYZ.setVisible(True)
        print("showYZDicom end")

    def show3DDicom(self):
        print("show 3D Dicom Window Begin")
        if self.vtk3DWidget is None: self.vtk3DWidget = QVTKRenderWindowInteractor(self.vtk3DContainer)
        self.vtk3DWidget.setFixedSize(self.vtk3DContainer.size())

        if self.ren3D is None: self.ren3D = vtk.vtkRenderer()
        renWin = self.vtk3DWidget.GetRenderWindow()
        renWin.AddRenderer(self.ren3D)

        # v16 = vtk.vtkVolume16Reader()
        # v16.SetDataDimensions(64, 64)
        # v16.SetImageRange(1, 93)
        # v16.SetDataByteOrderToLittleEndian()
        # v16.SetFilePrefix("D:/dicom_image/headsq/quarter")
        # v16.SetDataSpacing(3.2, 3.2, 1.5)
        v16 = vtk.vtkDICOMImageReader()
        v16.SetDirectoryName(self.filePath)

        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(v16.GetOutputPort())
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

        self.ren3D.AddViewProp(volume)

        camera = self.ren3D.GetActiveCamera()
        c = volume.GetCenter()
        camera.SetFocalPoint(c[0], c[1], c[2])
        camera.SetPosition(c[0] + 400, c[1], c[2])
        camera.SetViewUp(0, 0, -1)
        # Interact with the data.
        self.vtk3DWidget.Initialize()
        renWin.Render()
        self.vtk3DWidget.Start()

        if not self.vtk3DWidget.isVisible(): self.vtk3DWidget.setVisible(True)
        print("show 3D Dicom Window End")

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.qvtkWidgetXZ is not None: self.qvtkWidgetXZ.Finalize()
        if self.qvtkWidgetYZ is not None: self.qvtkWidgetYZ.Finalize()
        if self.vtk3DWidget is not None: self.vtk3DWidget.Finalize()

    def hideXZandYZDicom(self):
        if self.qvtkWidgetXZ is not None:self.qvtkWidgetXZ.setVisible(False)
        if self.qvtkWidgetYZ is not None:self.qvtkWidgetYZ.setVisible(False)
