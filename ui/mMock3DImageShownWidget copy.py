from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame
from Config import UIConfig, uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
import vtkmodules.all as vtk
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

        self.path = UIConfig.mainPath
        self.path_mask = UIConfig.mainPathMask

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


        # mapper = vtk.vtkGPUVolumeRayCastMapper()
        # mapper.SetInputData(self.reader.GetOutput())

        # volume = vtk.vtkVolume()
        # volume.SetMapper(mapper)

        # property = vtk.vtkVolumeProperty()

        # popacity = vtk.vtkPiecewiseFunction()
        # popacity.AddPoint(-10000, 0.0)
        # popacity.AddPoint(4000, 0.68)
        # popacity.AddPoint(10000, 0.83)

        # color = vtk.vtkColorTransferFunction()
        # color.AddHSVPoint(1000, 0.042, 0.73, 0.55)
        # color.AddHSVPoint(2500, 0.042, 0.73, 0.55, 0.5, 0.92)
        # color.AddHSVPoint(4000, 0.088, 0.67, 0.88)
        # color.AddHSVPoint(5500, 0.088, 0.67, 0.88, 0.33, 0.45)
        # color.AddHSVPoint(7000, 0.95, 0.063, 1.0)

        # property.SetColor(color)
        # # property.SetScalarOpacity(popacity)
        # property.ShadeOn()
        # property.SetInterpolationTypeToLinear()
        # property.SetShade(0, 1)
        # property.SetDiffuse(0.9)
        # property.SetAmbient(0.1)
        # property.SetSpecular(0.2)
        # property.SetSpecularPower(10.0)
        # property.SetComponentWeight(0, 1)
        # property.SetDisableGradientOpacity(1)
        # property.DisableGradientOpacityOn()
        # property.SetScalarOpacityUnitDistance(0.891927)

        # volume.SetProperty(property)

        # # ren = vtk.vtkRenderer()
        # self.renImage.AddActor(volume)
        # # self.renImage.SetBackground(1,1,1)
        # self.renImage.SetBackground(0.1, 0.2, 0.4)

        # self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)

        # self.iren.SetRenderWindow(self.qvtkWidget.GetRenderWindow())
        # self.qvtkWidget.GetRenderWindow().Render()
        # self.iren.Start()


'''
VTK Pipeline:   reader ->
                extractor -> 
                decimate -> 
                smoother -> 
                normalizer -> 
                mapper
'''
reader = vtk.vtkNIFTIImageReader()
reader.SetFileNameSliceOffset(1)
reader.SetDataByteOrderToBigEndian()
reader.SetFileName(file_name)
reader.Update()

# brain.labels[0].extractor = create_brain_extractor(brain)
brain_extractor = vtk.vtkFlyingEdges3D()
brain_extractor.SetInputConnection(brain.reader.GetOutputPort())

# reducer = create_polygon_reducer(nii_object.labels[label_idx].extractor)
reducer = vtk.vtkDecimatePro()
reducer.AddObserver('ErrorEvent', error_observer)  # throws an error event if there is no data to decimate
reducer.SetInputConnection(extractor.GetOutputPort())
reducer.SetTargetReduction(0.5)  # magic number
reducer.PreserveTopologyOn()
# smoother = create_smoother(reducer, nii_object.labels[label_idx].smoothness)
smoother = vtk.vtkSmoothPolyDataFilter()
smoother.SetInputConnection(reducer.GetOutputPort())
smoother.SetNumberOfIterations(smoothness)

# normals = create_normals(smoother)
brain_normals = vtk.vtkPolyDataNormals()
brain_normals.SetInputConnection(smoother.GetOutputPort())
brain_normals.SetFeatureAngle(60.0)  #
# actor_mapper = create_mapper(normals)
brain_mapper = vtk.vtkPolyDataMapper()
brain_mapper.SetInputConnection(stripper.GetOutputPort())
brain_mapper.ScalarVisibilityOff()
brain_mapper.Update()
# actor_property = create_property(nii_object.labels[label_idx].opacity, nii_object.labels[label_idx].color)
prop = vtk.vtkProperty()
prop.SetColor(color[0], color[1], color[2])
prop.SetOpacity(opacity)
# actor = create_actor(actor_mapper, actor_property)
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.SetProperty(prop)


def read_volume(file_name):
    """
    :param file_name: The filename of type 'nii.gz'
    :return: vtkNIFTIImageReader (https://www.vtk.org/doc/nightly/html/classvtkNIFTIImageReader.html)
    """
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileNameSliceOffset(1)
    reader.SetDataByteOrderToBigEndian()
    reader.SetFileName(file_name)
    reader.Update()
    return reader


def create_brain_extractor(brain):
    """
    Given the output from brain (vtkNIFTIImageReader) extract it into 3D using
    vtkFlyingEdges3D algorithm (https://www.vtk.org/doc/nightly/html/classvtkFlyingEdges3D.html)
    :param brain: a vtkNIFTIImageReader volume containing the brain
    :return: the extracted volume from vtkFlyingEdges3D
    """
    brain_extractor = vtk.vtkFlyingEdges3D()
    brain_extractor.SetInputConnection(brain.reader.GetOutputPort())
    # brain_extractor.SetValue(0, sum(brain.scalar_range)/2)
    return brain_extractor


def create_mask_extractor(mask):
    """
    Given the output from mask (vtkNIFTIImageReader) extract it into 3D using
    vtkDiscreteMarchingCubes algorithm (https://www.vtk.org/doc/release/5.0/html/a01331.html).
    This algorithm is specialized for reading segmented volume labels.
    :param mask: a vtkNIFTIImageReader volume containing the mask
    :return: the extracted volume from vtkDiscreteMarchingCubes
    """
    mask_extractor = vtk.vtkDiscreteMarchingCubes()
    mask_extractor.SetInputConnection(mask.reader.GetOutputPort())
    return mask_extractor


def create_polygon_reducer(extractor):
    """
    Reduces the number of polygons (triangles) in the volume. This is used to speed up rendering.
    (https://www.vtk.org/doc/nightly/html/classvtkDecimatePro.html)
    :param extractor: an extractor (vtkPolyDataAlgorithm), will be either vtkFlyingEdges3D or vtkDiscreteMarchingCubes
    :return: the decimated volume
    """
    reducer = vtk.vtkDecimatePro()
    reducer.AddObserver('ErrorEvent', error_observer)  # throws an error event if there is no data to decimate
    reducer.SetInputConnection(extractor.GetOutputPort())
    reducer.SetTargetReduction(0.5)  # magic number
    reducer.PreserveTopologyOn()
    return reducer


def create_smoother(reducer, smoothness):
    """
    Reorients some points in the volume to smooth the render edges.
    (https://www.vtk.org/doc/nightly/html/classvtkSmoothPolyDataFilter.html)
    :param reducer:
    :param smoothness:
    :return:
    """
    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputConnection(reducer.GetOutputPort())
    smoother.SetNumberOfIterations(smoothness)
    return smoother


def create_normals(smoother):
    """
    The filter can reorder polygons to insure consistent orientation across polygon neighbors. Sharp edges can be split
    and points duplicated with separate normals to give crisp (rendered) surface definition.
    (https://www.vtk.org/doc/nightly/html/classvtkPolyDataNormals.html)
    :param smoother:
    :return:
    """
    brain_normals = vtk.vtkPolyDataNormals()
    brain_normals.SetInputConnection(smoother.GetOutputPort())
    brain_normals.SetFeatureAngle(60.0)  #
    return brain_normals


def create_mapper(stripper):
    brain_mapper = vtk.vtkPolyDataMapper()
    brain_mapper.SetInputConnection(stripper.GetOutputPort())
    brain_mapper.ScalarVisibilityOff()
    brain_mapper.Update()
    return brain_mapper


def create_property(opacity, color):
    prop = vtk.vtkProperty()
    prop.SetColor(color[0], color[1], color[2])
    prop.SetOpacity(opacity)
    return prop


def create_actor(mapper, prop):
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetProperty(prop)
    return actor


def create_mask_table():
    m_mask_opacity = 1
    brain_lut = vtk.vtkLookupTable()
    brain_lut.SetRange(0, 4)
    brain_lut.SetRampToLinear()
    brain_lut.SetValueRange(0, 1)
    brain_lut.SetHueRange(0, 0)
    brain_lut.SetSaturationRange(0, 0)

    brain_lut.SetNumberOfTableValues(10)
    brain_lut.SetTableRange(0, 9)
    brain_lut.SetTableValue(0, 0, 0, 0, 0)
    brain_lut.SetTableValue(1, 1, 0, 0, m_mask_opacity)  # RED
    brain_lut.SetTableValue(2, 0, 1, 0, m_mask_opacity)  # GREEN
    brain_lut.SetTableValue(3, 1, 1, 0, m_mask_opacity)  # YELLOW
    brain_lut.SetTableValue(4, 0, 0, 1, m_mask_opacity)  # BLUE
    brain_lut.SetTableValue(5, 1, 0, 1, m_mask_opacity)  # MAGENTA
    brain_lut.SetTableValue(6, 0, 1, 1, m_mask_opacity)  # CYAN
    brain_lut.SetTableValue(7, 1, 0.5, 0.5, m_mask_opacity)  # RED_2
    brain_lut.SetTableValue(8, 0.5, 1, 0.5, m_mask_opacity)  # GREEN_2
    brain_lut.SetTableValue(9, 0.5, 0.5, 1, m_mask_opacity)  # BLUE_2
    brain_lut.Build()
    return brain_lut


def create_table():
    table = vtk.vtkLookupTable()
    table.SetRange(0.0, 1675.0)  # +1
    table.SetRampToLinear()
    table.SetValueRange(0, 1)
    table.SetHueRange(0, 0)
    table.SetSaturationRange(0, 0)


def add_surface_rendering(nii_object, label_idx, label_value):
    nii_object.labels[label_idx].extractor.SetValue(0, label_value)
    nii_object.labels[label_idx].extractor.Update()

    # if the cell size is 0 then there is no label_idx data
    if nii_object.labels[label_idx].extractor.GetOutput().GetMaxCellSize():
        reducer = create_polygon_reducer(nii_object.labels[label_idx].extractor)
        smoother = create_smoother(reducer, nii_object.labels[label_idx].smoothness)
        normals = create_normals(smoother)
        actor_mapper = create_mapper(normals)
        actor_property = create_property(nii_object.labels[label_idx].opacity, nii_object.labels[label_idx].color)
        actor = create_actor(actor_mapper, actor_property)
        nii_object.labels[label_idx].actor = actor
        nii_object.labels[label_idx].smoother = smoother
        nii_object.labels[label_idx].property = actor_property


def setup_slicer(renderer, brain):
    x = brain.extent[1]
    y = brain.extent[3]
    z = brain.extent[5]

    axial = vtk.vtkImageActor()
    axial_prop = vtk.vtkImageProperty()
    axial_prop.SetOpacity(0)
    axial.SetProperty(axial_prop)
    axial.GetMapper().SetInputConnection(brain.image_mapper.GetOutputPort())
    axial.SetDisplayExtent(0, x, 0, y, int(z/2), int(z/2))
    axial.InterpolateOn()
    axial.ForceOpaqueOn()

    coronal = vtk.vtkImageActor()
    cor_prop = vtk.vtkImageProperty()
    cor_prop.SetOpacity(0)
    coronal.SetProperty(cor_prop)
    coronal.GetMapper().SetInputConnection(brain.image_mapper.GetOutputPort())
    coronal.SetDisplayExtent(0, x, int(y/2), int(y/2), 0, z)
    coronal.InterpolateOn()
    coronal.ForceOpaqueOn()

    sagittal = vtk.vtkImageActor()
    sag_prop = vtk.vtkImageProperty()
    sag_prop.SetOpacity(0)
    sagittal.SetProperty(sag_prop)
    sagittal.GetMapper().SetInputConnection(brain.image_mapper.GetOutputPort())
    sagittal.SetDisplayExtent(int(x/2), int(x/2), 0, y, 0, z)
    sagittal.InterpolateOn()
    sagittal.ForceOpaqueOn()

    renderer.AddActor(axial)
    renderer.AddActor(coronal)
    renderer.AddActor(sagittal)

    return [axial, coronal, sagittal]


def setup_projection(brain, renderer):
    slice_mapper = vtk.vtkImageResliceMapper()
    slice_mapper.SetInputConnection(brain.reader.GetOutputPort())
    slice_mapper.SliceFacesCameraOn()
    slice_mapper.SliceAtFocalPointOn()
    slice_mapper.BorderOff()

    brain_image_prop = vtk.vtkImageProperty()
    brain_image_prop.SetOpacity(0.0)
    brain_image_prop.SetInterpolationTypeToLinear()
    image_slice = vtk.vtkImageSlice()
    image_slice.SetMapper(slice_mapper)
    image_slice.SetProperty(brain_image_prop)
    image_slice.GetMapper().SetInputConnection(brain.image_mapper.GetOutputPort())
    renderer.AddViewProp(image_slice)
    return brain_image_prop


def setup_brain(renderer, file):
    brain = NiiObject()
    brain.file = file
    brain.reader = read_volume(brain.file)
    brain.labels.append(NiiLabel(BRAIN_COLORS[0], BRAIN_OPACITY, BRAIN_SMOOTHNESS))
    brain.labels[0].extractor = create_brain_extractor(brain)
    brain.extent = brain.reader.GetDataExtent()

    scalar_range = brain.reader.GetOutput().GetScalarRange()
    bw_lut = vtk.vtkLookupTable()
    bw_lut.SetTableRange(scalar_range)
    bw_lut.SetSaturationRange(0, 0)
    bw_lut.SetHueRange(0, 0)
    bw_lut.SetValueRange(0, 2)
    bw_lut.Build()

    view_colors = vtk.vtkImageMapToColors()
    view_colors.SetInputConnection(brain.reader.GetOutputPort())
    view_colors.SetLookupTable(bw_lut)
    view_colors.Update()
    brain.image_mapper = view_colors
    brain.scalar_range = scalar_range

    add_surface_rendering(brain, 0, sum(scalar_range)/2)  # render index, default extractor value
    renderer.AddActor(brain.labels[0].actor)
    return brain


def setup_mask(renderer, file):
    mask = NiiObject()
    mask.file = file
    mask.reader = read_volume(mask.file)
    mask.extent = mask.reader.GetDataExtent()
    n_labels = int(mask.reader.GetOutput().GetScalarRange()[1])
    n_labels = n_labels if n_labels <= 10 else 10

    for label_idx in range(n_labels):
        mask.labels.append(NiiLabel(MASK_COLORS[label_idx], MASK_OPACITY, MASK_SMOOTHNESS))
        mask.labels[label_idx].extractor = create_mask_extractor(mask)
        add_surface_rendering(mask, label_idx, label_idx + 1)
        renderer.AddActor(mask.labels[label_idx].actor)
    return mask