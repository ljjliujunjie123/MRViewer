from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame
from ui.config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
import vtkmodules.all as vtk
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom,getImageOrientationInfoFromDicom,Location
from utils.cycleSyncThread import CycleSyncThread
from ui.MockImage3DReconstruct import *
from vtkmodules.vtkRenderingCore import vtkImageActor, vtkPropAssembly
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes,
    vtkStripper
)
from vtkmodules.vtkRenderingAnnotation import (
    vtkAnnotatedCubeActor,
    vtkAxesActor
)



class mMock3DImageShownWidget(QFrame, ImageShownWidgetInterface):
    
    update2DImageShownSignal = pyqtSignal()
    updateCrossViewSubSignal = pyqtSignal()

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None
        #初始化逻辑
        self.imageShownData = None

        self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)

       
        self.path = '/home/zhongsijie/MRViewer/MRViewer/static_3d_axial.nii.gz'
        self.path_mask = '/home/zhongsijie/MRViewer/MRViewer/tips.nii.gz'
        # Renderer
        self.renderer = vtk.vtkRenderer()
        # renderer.SetBackground(.2, .3, .4)
        self.renderer.ResetCamera()

        # Render Window
        self.renderWindow = self.qvtkWidget.GetRenderWindow()

        self.renderWindow.AddRenderer(self.renderer)

        # Interactor
        self.renderWindowInteractor = self.qvtkWidget.GetRenderWindow().GetInteractor()
        self.renderWindowInteractor.SetRenderWindow(self.renderWindow)
        self.renderWindowInteractor.SetInteractorStyle(KeyPressInteractorStyle(parent = self.renderWindowInteractor))
        self.renderWindowInteractor.Initialize()

        # Initialize a timer for MR animation
        self.addPointCloudTimerCallback = AddMRSliceTimerCallback(self.renderer, self.renderWindowInteractor, 100000, self.path, self.path_mask)
        self.renderWindowInteractor.AddObserver('TimerEvent', self.addPointCloudTimerCallback.execute)
        self.timerId = self.renderWindowInteractor.CreateRepeatingTimer(500)
        
        self.addPointCloudTimerCallback.timerId = self.timerId

        # colors = vtkNamedColors()
        # xyzLabels = ['X', 'Y', 'Z']
        # scale = [1.5, 1.5, 1.5]
        # axes = MakeCubeActor(scale, xyzLabels, colors)
        # self.renderer.AddActor(axes)
        # self.renderer.ResetCamera()
        # om = vtkOrientationMarkerWidget()
        # om.SetOrientationMarker(axes)
        # # Position upper left in the viewport.
        # om.SetViewport(0.0, 0.8, 0.2, 1.0)
        # om.SetInteractor(self.renderWindowInteractor)
        # om.EnabledOn()
        # om.InteractiveOn()

        # Set Camera
        self.camera = vtk.vtkCamera()
        self.camera.SetPosition((500, 500, 500))
        self.camera.SetViewUp((0, 0, 1))
        self.camera.SetFocalPoint((0, 0, 1))
        self.renderer.SetActiveCamera(self.camera)

        self.renderer.ResetCamera()


        # Begin Interaction
        self.renderer.SetBackground(0.5, 0.6, 0.8)
        self.renderWindow.SetSize(self.qvtkWidget.width(), self.qvtkWidget.height())
    
        self.renderWindow.Render()
        self.renderWindowInteractor.Start()

    def initBaseData(self, imageData):
        pass

    def showAllViews(self):
        pass

    def renderVtkWindow(self, layerCount = 1):
        self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(layerCount)
        self.qvtkWidget.Initialize()
        self.qvtkWidget.Start()
        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)

    def clearViews(self):
        self.qvtkWidget.Finalize()
    
    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.qvtkWidget.setFixedSize(self.size())
