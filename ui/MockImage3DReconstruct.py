import vtk
import numpy as np
from numpy import random
import SimpleITK as sitk
from vtk.util.vtkImageImportFromArray import *
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
from Config import uiConfig
from ui.dynamic_track_2d import *
import os


class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
     
    def __init__(self,parent=None):
        self.parent = vtk.vtkRenderWindowInteractor()
        if(parent is not None):
            self.parent = parent
 
        self.AddObserver("KeyPressEvent",self.keyPress)
 
    def keyPress(self,obj,event):
        key = self.parent.GetKeySym()
        if key == 'Up':
            
            gradtfun.AddPoint(-100, 1.0)
            gradtfun.AddPoint(10, 1.0)
            gradtfun.AddPoint(20, 1.0)
            
            volumeProperty.SetGradientOpacity(gradtfun)
            #下面这一行是关键，实现了actor的更新
            renderWindow.Render()
        if key == 'Down':
            
            
            tfun.AddPoint(1129, 0)
            tfun.AddPoint(1300.0, 0.1)
            tfun.AddPoint(1600.0, 0.2)
            tfun.AddPoint(2000.0, 0.1)
            tfun.AddPoint(2200.0, 0.1)
            tfun.AddPoint(2500.0, 0.1)
            tfun.AddPoint(2800.0, 0.1)
            tfun.AddPoint(3000.0, 0.1)
            #下面这一行是关键，实现了actor的更新
            renderWindow.Render()

def StartInteraction():
    renWin.SetDesiredUpdateRate(10)

def EndInteraction():
    renWin.SetDesiredUpdateRate(0.001)

def ClipVolumeRender(obj):
    obj.GetPlanes(planes)
    volumeMapper.SetClippingPlanes(planes)

def MakeAnnotatedCubeActor(colors):
    """
    :param colors: Used to determine the cube color.
    :return: The annotated cube actor.
    """
    # A cube with labeled faces.
    cube = vtkAnnotatedCubeActor()
    cube.SetXPlusFaceText('S')  # Right
    cube.SetXMinusFaceText('')  # Left
    cube.SetYPlusFaceText('C')  # Anterior
    cube.SetYMinusFaceText('')  # Posterior
    cube.SetZPlusFaceText('T')  # Superior/Cranial
    cube.SetZMinusFaceText('')  # Inferior/Caudal
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

def MakeAxesActor(scale, xyzLabels):
    """
    :param scale: Sets the scale and direction of the axes.
    :param xyzLabels: Labels for the axes.
    :return: The axes actor.
    """
    axes = vtkAxesActor()
    axes.SetScale(scale)
    axes.SetShaftTypeToCylinder()
    axes.SetXAxisLabelText(xyzLabels[0])
    axes.SetYAxisLabelText(xyzLabels[1])
    axes.SetZAxisLabelText(xyzLabels[2])
    axes.SetCylinderRadius(0.5 * axes.GetCylinderRadius())
    axes.SetConeRadius(1.025 * axes.GetConeRadius())
    axes.SetSphereRadius(1.5 * axes.GetSphereRadius())
    tprop = axes.GetXAxisCaptionActor2D().GetCaptionTextProperty()
    tprop.ItalicOn()
    tprop.ShadowOn()
    tprop.SetFontFamilyToTimes()
    # Use the same text properties on the other two axes.
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().ShallowCopy(tprop)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().ShallowCopy(tprop)
    return axes

def MakeCubeActor(scale, xyzLabels, colors):
    """
    :param scale: Sets the scale and direction of the axes.
    :param xyzLabels: Labels for the axes.
    :param colors: Used to set the colors of the cube faces.
    :return: The combined axes and annotated cube prop.
    """
    # We are combining a vtkAxesActor and a vtkAnnotatedCubeActor
    # into a vtkPropAssembly
    cube = MakeAnnotatedCubeActor(colors)
    axes = MakeAxesActor(scale, xyzLabels)

    # Combine orientation markers into one with an assembly.
    assembly = vtkPropAssembly()
    assembly.AddPart(axes)
    assembly.AddPart(cube)
    return assembly    


class VtkPointCloud:

    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e6):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(zMin, zMax)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)

    def addPoint(self, point):
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
        else:
            r = random.randint(0, self.maxNumPoints)
            self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')


class AddPointCloudTimerCallback():
    def __init__(self, renderer, iterations):
        self.iterations = iterations
        self.renderer = renderer

    def execute(self, iren, event):
        if self.iterations == 0:
            iren.DestroyTimer(self.timerId)
        pointCloud = VtkPointCloud()
        self.renderer.AddActor(pointCloud.vtkActor)
        pointCloud.clearPoints()
        for k in range(10000):
            point = 20*(random.rand(3)-0.5)
            pointCloud.addPoint(point)
        pointCloud.addPoint([0,0,0])
        pointCloud.addPoint([0,0,0])
        pointCloud.addPoint([0,0,0])
        pointCloud.addPoint([0,0,0])
        iren.GetRenderWindow().Render()
        if self.iterations == 30:
            self.renderer.ResetCamera()

        self.iterations -= 1

class VtkMRSlice:

    def __init__(self, path, path_tips, iren):
        # path = 'D:\\Ref_Code\\ANTsPy-master\\data\\ch2.nii.gz'#segmentation volume
        ds = sitk.ReadImage(path)  #读取nii数据的第一个函数sitk.ReadImage
        self.spacing = ds.GetSpacing()
        self.data = sitk.GetArrayFromImage(ds)[70:]     #把itk.image转为array # 

        ds_tip = sitk.ReadImage(path_tips)  #读取nii数据的第一个函数sitk.ReadImage
        # self.spacing_tip = ds_tip.GetSpacing()
        self.tips = sitk.GetArrayFromImage(ds_tip)[70:]     #把itk.image转为array #
        
        self.data[self.tips==1] = 1300
        # self.data = self.coronaldata.swapaxes(0,2)
        # import pdb
        # pdb.set_trace()
        # self.data = preprocess_general_procedure(self.rawdata, thresh=140)
        self.num_slices = self.data.shape[0]

        srange = [np.min(self.data),np.max(self.data)]
        min = srange[0]
        max = srange[1]
        diff = max - min             #体数据极差
        inter = 4200 / diff
        shift = -min


        self.img_arr = vtkImageImportFromArray()
        # self.img_arr.SetArray(self.data)
        # self.img_arr.SetDataSpacing(self.spacing)
        # origin = (-120,-120,-120)
        # self.img_arr.SetDataOrigin(origin)
        # self.img_arr.Update()
        
        self.vtkPoints = vtk.vtkPoints()
        # self.tip_arr = vtkImageImportFromArray()
        #下面的img_arr.SetArray是不是应该放到AddSlice里面
        # self.img_arr.SetArray(self.data[0:50])
        # self.img_arr.SetDataSpacing(self.spacing)
        # origin = (0,0,0)
        # self.img_arr.SetDataOrigin(origin)
        # self.img_arr.Update()

        # shifter 用来对图像的数值进行shift变换
        # 例如一副double类型的图像，其数值范围为[-1,1],如果将其转换为unsigned char类型，
        # 需要设置shift=+1,Scale=127.5;那么输入图像的数据-1可以被映射为（-1+1）*127.5=0；
        # +1可以被映射为（1+1）*127.5=255。
        shifter = vtk.vtkImageShiftScale()  # 对偏移和比例参数来对图像数据进行操作 数据转换，之后直接调用shifter
        shifter.SetShift(shift)
        shifter.SetScale(inter)
        shifter.SetOutputScalarTypeToUnsignedShort()
        shifter.SetInputData(self.img_arr.GetOutput())
        # shifter.SetInputData(self.tip_arr.GetOutput())
        shifter.ReleaseDataFlagOff()
        shifter.Update()

        # tfun
        tfun = vtk.vtkPiecewiseFunction()  # 不透明度传输函数---放在tfun
        # tfun.AddPoint(1129, 0)
        # tfun.AddPoint(1300.0, 0.1)
        # tfun.AddPoint(1600.0, 0.12)
        # tfun.AddPoint(2000.0, 0.13)
        # tfun.AddPoint(2200.0, 0.14)
        # tfun.AddPoint(2500.0, 0.16)
        # tfun.AddPoint(2800.0, 0.17)
        # tfun.AddPoint(3000.0, 0.18)
        # modify
        tfun.AddPoint(200, 0)
        # tfun.AddPoint(300.0, 0.901)
        # tfun.AddPoint(400.0, 0.901)
        # tfun.AddPoint(500.0, 0.901)
        tfun.AddPoint(600.0, 0.01)
        tfun.AddPoint(700.0, 0.1)
        tfun.AddPoint(800.0, 0.1)
        tfun.AddPoint(900.0, 0.1)
        tfun.AddPoint(1000.0, 0.1)
        tfun.AddPoint(1100.0, 0.20)
        tfun.AddPoint(1400.0, 0.30)


        # gradtfun
        gradtfun = vtk.vtkPiecewiseFunction()  # 梯度不透明度函数---放在gradtfun
        gradtfun.AddPoint(50, 0)
        gradtfun.AddPoint(500, 0.5)
        gradtfun.AddPoint(1000, 1)

        # ctfun
        ctfun = vtk.vtkColorTransferFunction()  # 颜色传输函数---放在ctfun
        ctfun.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
        ctfun.AddRGBPoint(200.0, 0.6, 0.7, 0.8)
        ctfun.AddRGBPoint(500.0, 0.7, 0.8, 0.9)
        ctfun.AddRGBPoint(1000.0, 0.8, 0.9, 1.0)
        ctfun.AddRGBPoint(2200.0, 0.9, 1.0, 1.0)
        ctfun.AddRGBPoint(2500.0, 1, 1.0, 1.0)
        ctfun.AddRGBPoint(3024.0, 1.0, 0.0, 0.0)

        # volumeMapper and volumeProperty
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()   #映射器volumnMapper使用vtk的管线投影算法
        volumeMapper.SetInputData(shifter.GetOutput())   #向映射器中输入数据：shifter(预处理之后的数据)
        volumeProperty = vtk.vtkVolumeProperty()         #创建vtk属性存放器,向属性存放器中存放颜色和透明度
        volumeProperty.SetColor(ctfun)  
        volumeProperty.SetScalarOpacity(tfun)
        volumeProperty.SetGradientOpacity(gradtfun) # 加上这句会使渲染出来的结果不透明
        volumeProperty.SetInterpolationTypeToLinear()    #???
        volumeProperty.ShadeOn()

        # newvol and outline 
        self.newvol = vtk.vtkVolume()                 #演员       
        self.newvol.SetMapper(volumeMapper)
        self.newvol.SetProperty(volumeProperty)

        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(shifter.GetOutputPort())

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(outlineMapper)

        self.vtkActor.GetProperty().SetOpacity(0.5)

        boxWidget = vtk.vtkBoxWidget()
        boxWidget.SetInteractor(iren)
        boxWidget.SetPlaceFactor(1.0)
        boxWidget.PlaceWidget(0,0,0,0,0,0)
        boxWidget.InsideOutOn()
        boxWidget.AddObserver("StartInteractionEvent", StartInteraction)
        boxWidget.AddObserver("InteractionEvent",  ClipVolumeRender)
        boxWidget.AddObserver("EndInteractionEvent",  EndInteraction)

        outlineProperty = boxWidget.GetOutlineProperty()
        outlineProperty.SetRepresentationToWireframe()
        outlineProperty.SetAmbient(1.0)
        outlineProperty.SetAmbientColor(1, 1, 1)
        outlineProperty.SetLineWidth(9)

        selectedOutlineProperty = boxWidget.GetSelectedOutlineProperty()
        selectedOutlineProperty.SetRepresentationToWireframe()
        selectedOutlineProperty.SetAmbient(1.0)
        selectedOutlineProperty.SetAmbientColor(1, 0, 0)
        selectedOutlineProperty.SetLineWidth(3)


        # Add Axial Plane use vtkImageActor
        self.axial = vtkImageActor()
        self.axial.GetMapper().SetInputConnection(shifter.GetOutputPort())
        # self.axial.SetDisplayExtent(0, 319, 0 , 255, 46, 46)
        self.axial.ForceOpaqueOn()

        # Extract Surface of vessel
        # colors = vtkNamedColors()
        # colors.SetColor('SkinColor', [240, 184, 160, 255])
        # skin_extractor = vtkMarchingCubes()
        # skin_extractor.SetInputConnection(shifter.GetOutputPort())
        # skin_extractor.SetValue(0, 600)
        # skin_extractor.Update()

        # skin_stripper = vtkStripper()
        # skin_stripper.SetInputConnection(skin_extractor.GetOutputPort())
        # skin_stripper.Update()

        # skin_mapper = vtk.vtkPolyDataMapper()
        # skin_mapper.SetInputConnection(skin_stripper.GetOutputPort())
        # skin_mapper.ScalarVisibilityOff()

        # self.skin = vtk.vtkActor()
        # self.skin.SetMapper(skin_mapper)
        # self.skin.GetProperty().SetDiffuseColor(colors.GetColor3d('SkinColor'))
        # self.skin.GetProperty().SetSpecular(0.3)
        # self.skin.GetProperty().SetSpecularPower(20)

        # self.skin.GetProperty().SetOpacity(0.5)


    
    def addSlice(self, slice):
        if slice <= self.num_slices:
            next_slices = self.data[0:slice]
            # next_tips = self.tips[0:slice]
            # next_slices[next_tips==1] = 1300
            # cur_tip = self.tips
            # cur_tip[slice:-1] = 0
            # self.data[cur_tip==1] = 1300
            # next_slices[-1,target[0], target[1]] = 1300
            self.img_arr.SetArray(next_slices)
            self.img_arr.SetDataSpacing(self.spacing)
            origin = (-120,-120,-120)
            self.img_arr.SetDataOrigin(origin)
            self.img_arr.Update()


            # self.axial.SetDisplayExtent(slice, slice, 0, 319, 0, 255)
            self.axial.SetDisplayExtent(0, 319, 0, 255, slice-1, slice)
            # self.axial.Update()
        
    
    def clearSlice(self):

        pass


slice_idx = 1
start_point_x = 170
start_point_y = 124

idx = 70
start = True
mean = 0
stop = False
finish = False
begin = False
class AddMRSliceTimerCallback():
    def __init__(self, renderer, iren, iterations, path, path_tips):
        self.iterations = iterations
        self.renderer = renderer
        self.MR_slice = VtkMRSlice(path, path_tips, iren)
        self.renderer.ResetCamera()
        # self.rawimg = sitk.ReadImage("/home/zhongsijie/MRViewer/MRViewer/dynamic_2d_robot.nii.gz")
        self.rawimg = sitk.ReadImage(r'E:\research\MRViewer_test\MRNewUI\dynamic_2d_robot.nii.gz')
        self.imgs = sitk.GetArrayFromImage(self.rawimg)
        #-----------------------------------------------------------------------------
        self.seriespath = '/home/zhongsijie/MRViewer/mock_dicoms/'
        self.seriespath = uiConfig.axialPath

    def execute(self, iren, event):
        # 1. 读取最新扫描得到的一张2D图像
        # 2. 使用dectmkr找到导丝顶点坐标（x,y）
        # 3. 使用p2dto3d找到2D坐标(x,y)在三维空间的坐标(x',y',z')
        # 4. 根据z'来确定我们要渲染到的高度，即决定slice_idx （这里的问题是，不能回退，如果监测到z'变小，则维持当前高度）
        #    根据(x,y)来确定画出导丝顶点的位置
        if self.iterations == 0:
            iren.DestroyTimer(self.timerId)
        # MR_slice = VtkMRSlice()
        
        # # 1. 读取最新扫描得到的一张2D图像
        global idx, stop, start_point_x, start_point_y, start, mean, begin
        try:
            #-----------------------------------------------------------------
            tmpFileNames = sorted(os.listdir(self.seriespath))
            rawimg = sitk.ReadImage(os.path.join(self.seriespath, tmpFileNames[-1]))
            img = sitk.GetArrayFromImage(rawimg)
            stop = False
            begin = True
            #-----------------------------------------------------------------
            # img = self.imgs[idx]
            # idx += 1
            # stop = False
        except:
            #------------------------------------------------------------------
            pass
            stop = True
            #------------------------------------------------------------------
            # img = self.imgs[-1]
            # stop = True

        
        # # 2. 使用dectmkr找到导丝顶点坐标（x,y）
        (pre_x, pre_y) = (start_point_x, start_point_y)
        tracker_size = 3
        if stop == False:
            try:
                start_point_x, start_point_y, mean = pci_tracking(img, start_point_x, start_point_y, mean, tracker_size, start)
                start = False
            except:
                pass
        

        print("Trcked 2D point: (%d, %d)"%(start_point_x, start_point_y))
        

        # # 3. 使用p2dto3d找到2D坐标(x,y)在三维空间的坐标(x',y',z')
        # x_3d, y_3d, z_3d = map2dto3d(np.double(x_2d), np.double(y_2d))

        # print("Mapped 3D point: (%d, %d, %d)"%(x_3d, y_3d, z_3d))

        # # 4. 根据z'来确定我们要渲染到的高度，即决定slice_idx;根据(x,y)来确定画出导丝顶点的位置
        global slice_idx
        # grow = slice_idx < z_3d
        # slice_idx = np.int(z_3d)

        # target = (np.int(x_3d), np.int(y_3d))

        self.renderer.AddActor(self.MR_slice.axial)
        self.renderer.AddActor(self.MR_slice.vtkActor)
        # self.renderer.AddActor(self.MR_slice.skin)
        self.renderer.AddVolume(self.MR_slice.newvol)
        
        self.MR_slice.clearSlice()
        
        # import pdb
        # pdb.set_trace()
        
        # self.MR_slice.addSlice(grow, slice_idx, target)
        self.MR_slice.addSlice(slice_idx)
        # slice_idx += 1
        # if start_point_x < pre_x:
        #     slice_idx += 1
        #     # slice_idx += pre_x - start_point_x
        # if stop == True and start == False:
        #     slice_idx += 1

        if stop == False and begin == True:
            slice_idx += 1
        iren.GetRenderWindow().Render()
        # if self.iterations == 36:
        #     self.renderer.ResetCamera()
        
        self.iterations -= 1
        print("NEXT!!!")

