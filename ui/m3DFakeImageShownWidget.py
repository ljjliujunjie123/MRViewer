from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer
)
import vtkmodules.all as vtk
from PyQt5.QtWidgets import QFrame
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from utils.util import MakeAnnotatedCubeActor,numpy2VTK,create_color_from_hexString
from Config import uiConfig
import numpy as np

class m3DFakeImageShownWidget(QFrame, ImageShownWidgetInterface):

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None

        self.qvtkWidget = QVTKRenderWindowInteractor(self)
        self.axes_widget = vtk.vtkOrientationMarkerWidget()

    def initBaseData(self, imageData):
        self.imageData = imageData

    def showAllViews(self):
        self.show3DFakeView()

    def show3DFakeView(self):
        colors = vtkNamedColors()

        ren = vtkRenderer()
        renWin = self.qvtkWidget.GetRenderWindow()
        renWin.AddRenderer(ren)
        self.iren = renWin.GetInteractor()
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.style.SetDefaultRenderer(ren)
        self.iren.SetInteractorStyle(self.style)

        # 添加世界坐标系
        axesActor = MakeAnnotatedCubeActor(colors)
        self.axes_widget.SetViewport(0.8, 0.8, 1.0, 1.0)
        self.axes_widget.SetOrientationMarker(axesActor)
        self.axes_widget.SetInteractor(self.iren)
        self.axes_widget.EnabledOn()
        self.axes_widget.InteractiveOn()  # 坐标系是否可移动

        for actor in self.MakePlanesActors(colors):
            ren.AddActor(actor)

        ren.SetBackground2(create_color_from_hexString(uiConfig.LightColor.Analogous1))
        ren.SetBackground(create_color_from_hexString(uiConfig.LightColor.Complementary))
        ren.GradientBackgroundOn()
        ren.ResetCamera()
        ren.GetActiveCamera().Zoom(1.6)
        ren.GetActiveCamera().SetPosition(-3.4, 5.5, 0.0)
        ren.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
        ren.ResetCameraClippingRange()
        renWin.SetWindowName('AnatomicalOrientation')
        self.qvtkWidget.Initialize()
        renWin.Render()
        self.qvtkWidget.Start()

    def MakePlane(self, resolution, origin, point1, point2, wxyz, translate):
        plane = vtkPlaneSource()
        plane.SetResolution(*resolution)
        plane.SetOrigin(origin)
        plane.SetPoint1(point1)
        plane.SetPoint2(point2)
        trnf = vtkTransform()
        trnf.RotateWXYZ(*wxyz)
        trnf.Translate(translate)
        tpdPlane = vtkTransformPolyDataFilter()
        tpdPlane.SetTransform(trnf)
        tpdPlane.SetInputConnection(plane.GetOutputPort())
        return tpdPlane

    def MakeTexture(self, dcmData):
        vtkImageData = numpy2VTK(np.uint16(dcmData.pixel_array))

        flip = vtk.vtkImageFlip()
        flip.SetInputData(vtkImageData)
        flip.SetFilteredAxes(1)
        flip.Update()

        colorTable = vtk.vtkWindowLevelLookupTable()
        colorTable.SetNumberOfColors(256)
        colorTable.SetTableRange(0,dcmData.LargestImagePixelValue)
        colorTable.SetHueRange(0.0,0.0)
        colorTable.SetSaturationRange(0.0,0.0)
        colorTable.SetValueRange(0.0,1.0)
        colorTable.SetAlphaRange(0.0,1.0)
        colorTable.Build()

        atext = vtk.vtkTexture()
        atext.SetInputConnection(flip.GetOutputPort())
        atext.SetLookupTable(colorTable)
        atext.RepeatOff()
        atext.InterpolateOn()

        return atext

    def MakePlanesActors(self, colors):
        """
        Make the traverse, coronal and saggital planes.
        :param colors: Used to set the color of the planes.
        :return: The planes actors.
        """
        planes = list()
        atexts = list()
        mappers = list()
        actors = list()

        # Parameters for a plane lying in the x-y plane.
        resolution = [10, 10]
        origin = [0.0, 0.0, 0.0]
        point1 = [1, 0, 0]
        point2 = [0, 1, 0]

        atexts = [self.MakeTexture(self.imageData.getDcmDataByIndex(i)) for i in range(self.imageData.seriesImageCount)]

        planes.append(self.MakePlane(resolution, origin, point1, point2, [0, 0, 0, 0], [-0.5, -0.5, 0]))  # x-y plane
        planes.append(self.MakePlane(resolution, origin, point1, point2, [-90, 1, 0, 0], [-0.5, -0.5, 0.0]))  # x-z plane
        planes.append(self.MakePlane(resolution, origin, point1, point2, [-90, 0, 1, 0], [-0.5, -0.5, 0.0]))  # y-z plane

        for i in range(len(planes)):
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(planes[i].GetOutputPort())
            actor = vtkActor()
            actor.SetMapper(mapper)
            actor.SetTexture(atexts[i])
            mappers.append(mapper)
            actors.append(actor)
        return actors

    def resizeEvent(self, *args, **kwargs):
        self.qvtkWidget.setFixedSize(self.size())

    def clearViews(self):
        self.qvtkWidget.Finalize()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.qvtkWidget.Finalize()