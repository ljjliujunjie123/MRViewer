import os
from PyQt5.QtWidgets import QFrame
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from utils.util import getDicomWindowCenterAndLevel,getImageTileInfoFromDicom

class m3DFakeImageShownWidget(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置
        self.label.setText("This is a 3D image based on series.")
        #初始化数据
        self.seriesPath = ""
        #初始化逻辑
        self.update3DImageShownSignal = None
        self.qvtkWidget = None

    def dropEvent(self, event):
        super().dropEvent(event)
        self.seriesPath = event.mimeData().getImageExtraData()["seriesPath"]
        fileNames = os.listdir(self.seriesPath)
        if len(fileNames) > 0: self.setTileText(getImageTileInfoFromDicom(self.seriesPath + '/' + fileNames[0]))
        event.mimeData().setText("")
        self.show3DImage(self.seriesPath)

    def show3DImage(self, seriesPath):
        print("show 3D Dicom Window Begin")
        if self.qvtkWidget is None: self.qvtkWidget = QVTKRenderWindowInteractor(self.imageContainer)
        self.qvtkWidget.setFixedSize(self.imageContainer.size())

        ren3D = vtk.vtkRenderer()
        renWin = self.qvtkWidget.GetRenderWindow()
        renWin.AddRenderer(ren3D)

        # v16 = vtk.vtkVolume16Reader()
        # v16.SetDataDimensions(64, 64)
        # v16.SetImageRange(1, 93)
        # v16.SetDataByteOrderToLittleEndian()
        # v16.SetFilePrefix("D:/dicom_image/headsq/quarter")
        # v16.SetDataSpacing(3.2, 3.2, 1.5)
        v16 = vtk.vtkDICOMImageReader()
        v16.SetDirectoryName(seriesPath)

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

        ren3D.AddViewProp(volume)

        camera = ren3D.GetActiveCamera()
        c = volume.GetCenter()
        camera.SetFocalPoint(c[0], c[1], c[2])
        camera.SetPosition(c[0] + 400, c[1], c[2])
        camera.SetViewUp(0, 0, -1)
        # Interact with the data.
        self.qvtkWidget.Initialize()
        renWin.Render()
        self.qvtkWidget.Start()

        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)
        print("show 3D Dicom Window End")