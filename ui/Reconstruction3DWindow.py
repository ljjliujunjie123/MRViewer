from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

'''
    用来测试3种不同的3D绘制算法
'''
class Reconstruction3DWindow(QMainWindow):

    # filePath = r'D:\respository\MRViewer_Scource\CT_source'
    # filePath = r'D:\respository\MRViewer_Scource\dicom_for_UItest\3D_transversal'
    filePath = r'D:\respository\MRViewer_Scource\dicom_for_UItest\3D_vessel_phantom_transversal'

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setObjectName("Reconstruction3DWindow")
        self.setWindowTitle("Reconstruction3DWindow")
        self.resize(1500,1000)

        self.frame = QFrame()
        self.frame.setFixedSize(QSize(1000,1000))
        self.setCentralWidget(self.frame)

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.show()

        # self.surfaceReconstructionMC()
        # self.surfaceReconstruction()
        self.volumeReconstruction()

    def surfaceReconstructionMC(self):

        # 读取Dicom数据，对应source
        v16 = vtk.vtkDICOMImageReader()
        # v16.SetDirectoryName('D:/dicom_image/V')
        v16.SetDirectoryName(self.filePath)

        # 利用封装好的MC算法抽取等值面，对应filter
        marchingCubes = vtk.vtkMarchingCubes()
        marchingCubes.SetInputConnection(v16.GetOutputPort())
        marchingCubes.SetValue(0, -10)

        # 剔除旧的或废除的数据单元，提高绘制速度，对应filter
        Stripper = vtk.vtkStripper()
        Stripper.SetInputConnection(marchingCubes.GetOutputPort())

        # 建立映射，对应mapper
        mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(marchingCubes.GetOutputPort())
        mapper.SetInputConnection(Stripper.GetOutputPort())

        # 建立角色以及属性的设置，对应actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # 角色的颜色设置
        actor.GetProperty().SetDiffuseColor(1, .94, .25)
        # 设置高光照明系数
        actor.GetProperty().SetSpecular(.1)
        # 设置高光能量
        actor.GetProperty().SetSpecularPower(100)

        # 定义舞台，也就是渲染器，对应render
        renderer = vtk.vtkRenderer()

        # 定义舞台上的相机，对应render
        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()

        # 定义整个剧院(应用窗口)，对应renderwindow
        rewin = self.vtkWidget.GetRenderWindow()

        # 将相机添加到舞台renderer
        renderer.SetActiveCamera(aCamera)
        aCamera.Dolly(1.5)

        # 设置交互方式
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.vtkWidget.SetInteractorStyle(style)

        # 将舞台添加到剧院中
        rewin.AddRenderer(renderer)

        # 将角色添加到舞台中
        renderer.AddActor(actor)

        # 将相机的焦点移动至中央，The camera will reposition itself to view the center point of the actors,
        # and move along its initial view plane normal
        renderer.ResetCamera()

        self.vtkWidget.Initialize()

        self.vtkWidget.Start()

    def surfaceReconstruction(self):
        aRenderer = vtk.vtkRenderer()  # 渲染器
        renWin = self.vtkWidget.GetRenderWindow()  # 渲染窗口,创建窗口
        renWin.AddRenderer(aRenderer)  # 渲染窗口

        print(1)
        # The following reader is used to read a series of 2D slices(images)
        # that compose the volume.Theslicedimensions are set, and the
        #  pixel spacing.The data Endianness must also be specified.The reader
        #  uses the FilePrefix in combination with the slice number to construct
        # filenames using the format FilePrefix. % d.(In this case the FilePrefix
        # is the root name of the file.

        v16 = vtk.vtkDICOMImageReader()
        # v16.SetDirectoryName('D:/dicom_image/V')
        v16.SetDirectoryName(self.filePath)

        # An isosurface, or contour value of 500 is known to correspond to the
        # skin of the patient.Once generated, a vtkPolyDataNormals filter is
        # used to create normals for smooth surface shading during rendering.
        skinExtractor = vtk.vtkContourFilter()
        skinExtractor.SetInputConnection(v16.GetOutputPort())
        skinExtractor.SetValue(0, -10)
        # skinExtractor.GenerateValues(2, 100, 110)
        skinNormals = vtk.vtkPolyDataNormals()
        skinNormals.SetInputConnection(skinExtractor.GetOutputPort())
        skinNormals.SetFeatureAngle(60.0)
        skinMapper = vtk.vtkPolyDataMapper()  # 映射器
        skinMapper.SetInputConnection(skinNormals.GetOutputPort())
        skinMapper.ScalarVisibilityOff()

        skin = vtk.vtkActor()
        # 设置颜色RGB颜色系统就是由三个颜色分量：红色(R)、绿色(G)和蓝色(B)的组合表示，
        # 在VTK里这三个分量的取值都是从0到1，(0, 0, 0)表示黑色，(1, 1, 1)表示白色。
        #  vtkProperty::SetColor(r,g, b)采用的就是RGB颜色系统设置颜色属性值。
        #skin.GetProperty().SetColor(0, 0, 1)
        skin.SetMapper(skinMapper)

        skin.GetProperty().SetDiffuseColor(1, .49, .25)

        skin.GetProperty().SetSpecular(.5)

        skin.GetProperty().SetSpecularPower(20)

        # skin.GetProperty().SetRepresentationToSurface()
        # 构建图形的方框
        outlineData = vtk.vtkOutlineFilter()
        outlineData.SetInputConnection(v16.GetOutputPort())
        mapOutline = vtk.vtkPolyDataMapper()
        mapOutline.SetInputConnection(outlineData.GetOutputPort())
        outline = vtk.vtkActor()
        outline.SetMapper(mapOutline)
        outline.GetProperty().SetColor(0, 0, 0)

        # 构建舞台的相机
        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()

        # Actors are added to the renderer.An initial camera view is created.
        # The Dolly() method moves the camera towards the Focal　Point,
        # thereby enlarging the image.
        aRenderer.AddActor(outline)
        aRenderer.AddActor(skin)
        aRenderer.SetActiveCamera(aCamera)
        # 将相机的焦点移动至中央，The camera will reposition itself to view the center point of the actors,
        # and move along its initial view plane normal
        aRenderer.ResetCamera()
        # aCamera.Dolly(1.5)
        # aCamera.Roll(180)
        # aCamera.Yaw(60)

        aRenderer.SetBackground(250, 250, 250)
        # renWin.SetSize(640, 480)
        # 该方法是从vtkRenderWindow的父类vtkWindow继承过来的，用于设置窗口的大小，以像素为单位。
        renWin.SetSize(1000, 1000)
        aRenderer.ResetCameraClippingRange()

        print(2)
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.vtkWidget.SetInteractorStyle(style)

        self.vtkWidget.Initialize()
        self.vtkWidget.Start()

    def volumeReconstruction(self):
        ren = vtk.vtkRenderer()
        renWin = self.vtkWidget.GetRenderWindow()
        renWin.AddRenderer(ren)

        # The following reader is used to read a series of 2D slices (images)
        # that compose the volume. The slice dimensions are set, and the
        # pixel spacing. The data Endianness must also be specified. The reader
        # usese the FilePrefix in combination with the slice number to construct
        # filenames using the format FilePrefix.%d. (In this case the FilePrefix
        # is the root name of the file: quarter.)

        # v16 = vtk.vtkVolume16Reader()
        # v16.SetDataDimensions(64, 64)
        # v16.SetImageRange(1, 93)
        # v16.SetDataByteOrderToLittleEndian()
        # v16.SetFilePrefix("D:/dicom_image/headsq/quarter")
        # v16.SetDataSpacing(3.2, 3.2, 1.5)
        v16 = vtk.vtkDICOMImageReader()
        # v16.SetDirectoryName('D:/dicom_image/vtkDicomRender-master/sample')
        v16.SetDirectoryName(self.filePath)

        # The volume will be displayed by ray-cast alpha compositing.
        # A ray-cast mapper is needed to do the ray-casting, and a
        # compositing function is needed to do the compositing along the ray.
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(v16.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()

        # The color transfer function maps voxel intensities to colors.
        # It is modality-specific, and often anatomy-specific as well.
        # The goal is to one color for flesh (between 500 and 1000)
        # and another color for bone (1150 and over).
        volumeColor = vtk.vtkColorTransferFunction()
        volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
        volumeColor.AddRGBPoint(500,  1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)

        # The opacity transfer function is used to control the opacity
        # of different tissue types.
        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(0,    0.00)
        volumeScalarOpacity.AddPoint(500,  0.15)
        volumeScalarOpacity.AddPoint(1000, 0.15)
        volumeScalarOpacity.AddPoint(1150, 0.85)

        # The gradient opacity function is used to decrease the opacity
        # in the "flat" regions of the volume while maintaining the opacity
        # at the boundaries between tissue types.  The gradient is measured
        # as the amount by which the intensity changes over unit distance.
        # For most medical data, the unit distance is 1mm.
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0,   0.0)
        volumeGradientOpacity.AddPoint(90,  0.5)
        volumeGradientOpacity.AddPoint(100, 1.0)

        # The VolumeProperty attaches the color and opacity functions to the
        # volume, and sets other volume properties.  The interpolation should
        # be set to linear to do a high-quality rendering.  The ShadeOn option
        # turns on directional lighting, which will usually enhance the
        # appearance of the volume and make it look more "3D".  However,
        # the quality of the shading depends on how accurately the gradient
        # of the volume can be calculated, and for noisy data the gradient
        # estimation will be very poor.  The impact of the shading can be
        # decreased by increasing the Ambient coefficient while decreasing
        # the Diffuse and Specular coefficient.  To increase the impact
        # of shading, decrease the Ambient and increase the Diffuse and Specular.
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        # volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.9)
        volumeProperty.SetDiffuse(0.9)
        volumeProperty.SetSpecular(0.9)

        # The vtkVolume is a vtkProp3D (like a vtkActor) and controls the position
        # and orientation of the volume in world coordinates.
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)

        # Finally, add the volume to the renderer
        ren.AddViewProp(volume)

        # Set up an initial view of the volume.  The focal point will be the
        # center of the volume, and the camera position will be 400mm to the
        # patient's left (which is our right).
        camera = ren.GetActiveCamera()
        c = volume.GetCenter()
        camera.SetFocalPoint(c[0], c[1], c[2])
        camera.SetPosition(c[0] + 400, c[1], c[2])
        camera.SetViewUp(0, 0, -1)

        # Increase the size of the render window
        renWin.SetSize(1000, 1000)

        # Interact with the data.
        self.vtkWidget.Initialize()
        renWin.Render()
        self.vtkWidget.Start()