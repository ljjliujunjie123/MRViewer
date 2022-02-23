# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import (
    vtkAnnotatedCubeActor,
    vtkAxesActor
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPropAssembly,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.util.vtkConstants import *
from vtkmodules.vtkRenderingFreeType import vtkVectorText
import vtkmodules.all as vtk


def main():
    colors = vtkNamedColors()

    # Create a rendering window, renderer and interactor.
    ren = vtkRenderer()
    renWin = vtkRenderWindow()
    renWin.SetSize(380, 380)
    renWin.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Finally create an annotated cube actor adding it into an orientation marker widget.
    axes3 = MakeAnnotatedCubeActor(colors)
    om3 = vtkOrientationMarkerWidget()
    om3.SetOrientationMarker(axes3)
    # Position upper right in the viewport.
    om3.SetViewport(0.8, 0.8, 1.0, 1.0)
    om3.SetInteractor(iren)
    om3.EnabledOn()
    om3.InteractiveOn()

    for actor in MakePlanesActors(colors):
        ren.AddActor(actor)

    # Interact
    ren.SetBackground2(colors.GetColor3d('OldLace'))
    ren.SetBackground(colors.GetColor3d('MistyRose'))
    ren.GradientBackgroundOn()
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.6)
    ren.GetActiveCamera().SetPosition(-2.3, 4.1, 4.2)
    # ren.GetActiveCamera().SetPosition(-3.4, 5.5, 0.0)
    ren.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
    ren.ResetCameraClippingRange()
    renWin.Render()
    # Call SetWindowName after renWin.Render() is called.
    renWin.SetWindowName('AnatomicalOrientation')

    iren.Initialize()
    iren.Start()

def MakeAnnotatedCubeActor(colors):
    """
    :param colors: Used to determine the cube color.
    :return: The annotated cube actor.
    """
    # A cube with labeled faces.
    cube = vtkAnnotatedCubeActor()
    cube.SetXPlusFaceText('R')  # Right
    cube.SetXMinusFaceText('L')  # Left
    cube.SetYPlusFaceText('A')  # Anterior
    cube.SetYMinusFaceText('P')  # Posterior
    cube.SetZPlusFaceText('S')  # Superior/Cranial
    cube.SetZMinusFaceText('I')  # Inferior/Caudal
    cube.SetFaceTextScale(0.5)
    cube.GetCubeProperty().SetColor(colors.GetColor3d('Gainsboro'))

    cube.GetTextEdgesProperty().SetColor(colors.GetColor3d('LightSlateGray'))

    # Change the vector text colors.
    cube.GetXPlusFaceProperty().SetColor(colors.GetColor3d('Tomato'))
    cube.GetXMinusFaceProperty().SetColor(colors.GetColor3d('Tomato'))
    cube.GetYPlusFaceProperty().SetColor(colors.GetColor3d('DeepSkyBlue'))
    cube.GetYMinusFaceProperty().SetColor(colors.GetColor3d('DeepSkyBlue'))
    cube.GetZPlusFaceProperty().SetColor(colors.GetColor3d('SeaGreen'))
    cube.GetZMinusFaceProperty().SetColor(colors.GetColor3d('SeaGreen'))
    return cube


def MakePlane(resolution, origin, point1, point2, wxyz, translate):
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


def MakePlanesActors(colors):
    """
    Make the traverse, coronal and saggital planes.
    :param colors: Used to set the color of the planes.
    :return: The planes actors.
    """
    planes = list()
    mappers = list()
    actors = list()

    # Parameters for a plane lying in the x-y plane.
    resolution = [10, 10]
    origin = [0.0, 0.0, 0.0]
    point1 = [1, 0, 0]
    point2 = [0, 1, 0]

    # Load in the texture map. A texture is any unsigned char image. If it
    # is not of this type, you will have to map it through a lookup table
    # or by using vtkImageShiftScale.
    from vtkmodules.util.numpy_support import numpy_to_vtk
    import numpy as np

    def numpy2VTK(img):
        shape = img.shape
        if len(shape) < 2:
            raise Exception('numpy array must have dimensionality of at least 2')

        height, width = shape[0], shape[1]
        c = shape[2] if len(shape) == 3 else 1

        linear_array = np.reshape(img, (width * height, c))
        vtk_array = numpy_to_vtk(linear_array)

        imageData = vtk.vtkImageData()
        imageData.SetDimensions(width, height, 1)
        imageData.AllocateScalars(VTK_UNSIGNED_INT, 1)
        imageData.GetPointData().GetScalars().DeepCopy(vtk_array)

        return imageData

    import pydicom as pyd
    dcmFile = pyd.dcmread(r"D:\respository\MRViewer_Scource\PCI\4_LXM_MRI\DICOM\3229208\13557945\717030239")
    vtkImageData = numpy2VTK(np.uint16(dcmFile.pixel_array))

    flip = vtk.vtkImageFlip()
    flip.SetInputData(vtkImageData)
    flip.SetFilteredAxes(1)
    flip.Update()

    colorTable = vtk.vtkWindowLevelLookupTable()
    colorTable.SetNumberOfColors(256)
    colorTable.SetTableRange(0,dcmFile.LargestImagePixelValue)
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

    planes.append(MakePlane(resolution, origin, point1, point2, [0, 0, 0, 0], [-0.5, -0.5, 0]))  # x-y plane
    planes.append(MakePlane(resolution, origin, point1, point2, [-90, 1, 0, 0], [-0.5, -0.5, 0.0]))  # x-z plane
    planes.append(MakePlane(resolution, origin, point1, point2, [-90, 0, 1, 0], [-0.5, -0.5, 0.0]))  # y-z plane

    for plane in planes:
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.SetTexture(atext)
        mappers.append(mapper)
        actors.append(actor)
    return actors


def AddTextToPlanes():
    """
    Generate text to place on the planes.
    Careful placement is needed here.
    :return: The text actors.
    """
    textActors = list()
    scale = [0.04, 0.04, 0.04]

    text1 = vtkVectorText()
    text1.SetText('Transverse\nPlane\n\nSuperior\nCranial')
    trnf1 = vtkTransform()
    trnf1.RotateZ(-90)
    tpdPlane1 = vtkTransformPolyDataFilter()
    tpdPlane1.SetTransform(trnf1)
    tpdPlane1.SetInputConnection(text1.GetOutputPort())
    textMapper1 = vtkPolyDataMapper()
    textMapper1.SetInputConnection(tpdPlane1.GetOutputPort())
    textActor1 = vtkActor()
    textActor1.SetMapper(textMapper1)
    textActor1.SetScale(scale)
    textActor1.AddPosition(0.4, 0.49, 0.01)
    textActors.append(textActor1)

    text2 = vtkVectorText()
    text2.SetText('Transverse\nPlane\n\nInferior\n(Caudal)')
    trnf2 = vtkTransform()
    trnf2.RotateZ(270)
    trnf2.RotateWXYZ(*[180, 0, 1, 0])
    tpdPlane2 = vtkTransformPolyDataFilter()
    tpdPlane2.SetTransform(trnf2)
    tpdPlane2.SetInputConnection(text2.GetOutputPort())
    textMapper2 = vtkPolyDataMapper()
    textMapper2.SetInputConnection(tpdPlane2.GetOutputPort())
    textActor2 = vtkActor()
    textActor2.SetMapper(textMapper2)
    textActor2.SetScale(scale)
    textActor2.AddPosition(0.4, -0.49, -0.01)
    textActors.append(textActor2)

    text3 = vtkVectorText()
    text3.SetText('Sagittal\nPlane\n\nLeft')
    trnf3 = vtkTransform()
    trnf3.RotateX(90)
    trnf3.RotateWXYZ(*[-90, 0, 1, 0])
    tpdPlane3 = vtkTransformPolyDataFilter()
    tpdPlane3.SetTransform(trnf3)
    tpdPlane3.SetInputConnection(text3.GetOutputPort())
    textMapper3 = vtkPolyDataMapper()
    textMapper3.SetInputConnection(tpdPlane3.GetOutputPort())
    textActor3 = vtkActor()
    textActor3.SetMapper(textMapper3)
    textActor3.SetScale(scale)
    textActor3.AddPosition(-0.01, 0.49, 0.4)
    textActors.append(textActor3)

    text4 = vtkVectorText()
    text4.SetText('Sagittal\nPlane\n\nRight')
    trnf4 = vtkTransform()
    trnf4.RotateX(90)
    trnf4.RotateWXYZ(*[-270, 0, 1, 0])
    tpdPlane4 = vtkTransformPolyDataFilter()
    tpdPlane4.SetTransform(trnf4)
    tpdPlane4.SetInputConnection(text4.GetOutputPort())
    textMapper4 = vtkPolyDataMapper()
    textMapper4.SetInputConnection(tpdPlane4.GetOutputPort())
    textActor4 = vtkActor()
    textActor4.SetMapper(textMapper4)
    textActor4.SetScale(scale)
    textActor4.AddPosition(0.01, -0.49, 0.4)
    textActors.append(textActor4)

    text5 = vtkVectorText()
    text5.SetText('Coronal\nPlane\n\nAnterior')
    trnf5 = vtkTransform()
    trnf5.RotateY(-180)
    trnf5.RotateWXYZ(*[-90, 1, 0, 0])
    tpdPlane5 = vtkTransformPolyDataFilter()
    tpdPlane5.SetTransform(trnf5)
    tpdPlane5.SetInputConnection(text5.GetOutputPort())
    textMapper5 = vtkPolyDataMapper()
    textMapper5.SetInputConnection(tpdPlane5.GetOutputPort())
    textActor5 = vtkActor()
    textActor5.SetMapper(textMapper5)
    textActor5.SetScale(scale)
    textActor5.AddPosition(0.49, 0.01, 0.20)
    textActors.append(textActor5)

    text6 = vtkVectorText()
    text6.SetText('Coronal\nPlane\n\nPosterior')
    trnf6 = vtkTransform()
    trnf6.RotateWXYZ(*[90, 1, 0, 0])
    tpdPlane6 = vtkTransformPolyDataFilter()
    tpdPlane6.SetTransform(trnf6)
    tpdPlane6.SetInputConnection(text6.GetOutputPort())
    textMapper6 = vtkPolyDataMapper()
    textMapper6.SetInputConnection(tpdPlane6.GetOutputPort())
    textActor6 = vtkActor()
    textActor6.SetMapper(textMapper6)
    textActor6.SetScale(scale)
    textActor6.AddPosition(-0.49, -0.01, 0.3)
    textActors.append(textActor6)
    return textActors


if __name__ == '__main__':
    main()
