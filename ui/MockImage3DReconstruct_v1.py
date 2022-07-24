import vtk
import numpy as np
from numpy import random
import SimpleITK as sitk
from vtk.util.vtkImageImportFromArray import *

class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
     
    def __init__(self,parent=None):
        self.parent = vtk.vtkRenderWindowInteractor()
        if(parent is not None):
            self.parent = parent
 
        self.AddObserver("KeyPressEvent",self.keyPress)
 
    def keyPress(self,obj,event):
        key = self.parent.GetKeySym()
            
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

    def __init__(self, path, iren):
        # path = 'D:\\Ref_Code\\ANTsPy-master\\data\\ch2.nii.gz'#segmentation volume
        ds = sitk.ReadImage(path)  #读取nii数据的第一个函数sitk.ReadImage
        self.spacing = ds.GetSpacing()
        self.data = sitk.GetArrayFromImage(ds)     #把itk.image转为array # 
        
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
        tfun.AddPoint(300.0, 0.1)
        tfun.AddPoint(400.0, 0.1)
        tfun.AddPoint(500.0, 0.1)
        tfun.AddPoint(6000.0, 0.1)
        tfun.AddPoint(700.0, 0.1)
        tfun.AddPoint(800.0, 0.1)
        tfun.AddPoint(900.0, 0.1)
        tfun.AddPoint(1000.0, 0.1)
        tfun.AddPoint(1100.0, 0.20)


        # gradtfun
        gradtfun = vtk.vtkPiecewiseFunction()  # 梯度不透明度函数---放在gradtfun
        gradtfun.AddPoint(-1000, 9)
        gradtfun.AddPoint(0.5, 9.9)
        gradtfun.AddPoint(1, 10)

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
        # volumeProperty.SetGradientOpacity(gradtfun) # 加上这句会使渲染出来的结果不透明
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

    
    def addSlice(self, slice):
        if slice <= self.num_slices:
            next_slices = self.data[0:slice]
            # next_slices[-1,target[0], target[1]] = 1300
            self.img_arr.SetArray(next_slices)
            self.img_arr.SetDataSpacing(self.spacing)
            origin = (-120,-120,-120)
            self.img_arr.SetDataOrigin(origin)
            self.img_arr.Update()
        
    
    def clearSlice(self):

        pass


slice_idx = 0
start_point_x = 153
start_point_y = 140

idx = 470

class AddMRSliceTimerCallback():
    def __init__(self, renderer, iren, iterations, path):
        self.iterations = iterations
        self.renderer = renderer
        self.MR_slice = VtkMRSlice(path, iren)
        self.renderer.ResetCamera()

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
        # global idx
        # rawimg = sitk.ReadImage("../dynamic_2d_1.nii.gz")
        # img = sitk.GetArrayFromImage(rawimg)[idx]
        # idx += 1

        # # 2. 使用dectmkr找到导丝顶点坐标（x,y）
        # global start_point_x, start_point_y
        # x_2d, y_2d = detect_probe(img, start_point_x, start_point_y)
        # (start_point_x, start_point_y) = (x_2d, y_2d)

        # print("Trcked 2D point: (%d, %d)"%(x_2d, y_2d))
        

        # # 3. 使用p2dto3d找到2D坐标(x,y)在三维空间的坐标(x',y',z')
        # x_3d, y_3d, z_3d = map2dto3d(np.double(x_2d), np.double(y_2d))

        # print("Mapped 3D point: (%d, %d, %d)"%(x_3d, y_3d, z_3d))

        # # 4. 根据z'来确定我们要渲染到的高度，即决定slice_idx;根据(x,y)来确定画出导丝顶点的位置
        global slice_idx
        # grow = slice_idx < z_3d
        # slice_idx = np.int(z_3d)

        # target = (np.int(x_3d), np.int(y_3d))

        self.renderer.AddActor(self.MR_slice.vtkActor)
        self.renderer.AddVolume(self.MR_slice.newvol)
        self.MR_slice.clearSlice()
        
        # import pdb
        # pdb.set_trace()

        # self.MR_slice.addSlice(grow, slice_idx, target)
        self.MR_slice.addSlice(slice_idx)
        # if slice_idx <= 100:
        slice_idx += 1
        iren.GetRenderWindow().Render()
        # if self.iterations == 36:
        #     self.renderer.ResetCamera()
        
        self.iterations -= 1
        print("NEXT!!!")


if __name__ == "__main__":
    # path = 'D:\\Ref_Code\\ANTsPy-master\\data\\ch2.nii.gz'#segmentation volume
    # path = 'E:\\Data\\pre_3d_vessel\\HEAD_CLINICAL_LIBRARIES_20211229_104656_059000\\3D_VESSEL_11_0033_nii\\3d_vessel_11_0033.nii.gz'
    # path = 'E:\\Data\\mr_3d\\Segmentation_1.seg.nrrd'
    # path = 'E:\\Data\\mr_3d\\4 t1_fl3d_sag_iso_1.nrrd'
    # path = 'E:\\Data\\2022-1-7\\IMR-SJTU_ZSJ_20220107_104710_497000\\static_3d_crossS.nii.gz'
    path = '../static_3d_mask.nii.gz'
    # Renderer
    renderer = vtk.vtkRenderer()
    # renderer.SetBackground(.2, .3, .4)
    renderer.ResetCamera()

    # Render Window
    renderWindow = vtk.vtkRenderWindow()

    renderWindow.AddRenderer(renderer)

    # Interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.SetInteractorStyle(KeyPressInteractorStyle(parent = renderWindowInteractor))
    renderWindowInteractor.Initialize()

    # Initialize a timer for the animation
    # addPointCloudTimerCallback = AddPointCloudTimerCallback(renderer, 30)
    # renderWindowInteractor.AddObserver('TimerEvent', addPointCloudTimerCallback.execute)
    # timerId = renderWindowInteractor.CreateRepeatingTimer(1000)
    # addPointCloudTimerCallback.timerId = timerId

    # Initialize a timer for MR animation
    addPointCloudTimerCallback = AddMRSliceTimerCallback(renderer, renderWindowInteractor, 1000, path)
    renderWindowInteractor.AddObserver('TimerEvent', addPointCloudTimerCallback.execute)
    timerId = renderWindowInteractor.CreateRepeatingTimer(1)
    addPointCloudTimerCallback.timerId = timerId

    # Set Camera
    camera = vtk.vtkCamera()
    camera.SetPosition((500, 500, 500))
    camera.SetViewUp((0, 0, 1))
    camera.SetFocalPoint((0, 0, 1))
    renderer.SetActiveCamera(camera)

    renderer.ResetCamera()


    # Begin Interaction
    renderer.SetBackground(0.5, 0.6, 0.8)
    renderWindow.SetSize(1000, 1000)
    
    renderWindow.Render()
    renderWindowInteractor.Start()
