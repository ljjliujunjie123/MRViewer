## Introduction

这是一个辅助心血管导航的GUI软件，提供实时的MR图像渲染

## Follow Me

##### Windows

Please check your computer if anaconda or miniconda has been installed. It would be easier to manage this project with conda virtual environment. But if not, you can also try the project by installing all packages needed.

Open your Anaconda Prompt console

```
D:  #select a disk
```

```
cd your_directory_path #select a empty directory to store project
```

```
git clone git@github.com:ljjliujunjie123/MRViewer.git
```

```
cd MRViewer 
```

```
conda create -n MRViewer #create a virtual python environment, name is "MRViewer"
```

```
conda activate MRViewer #activate this virtual env
```

```
conda install --yes --file requirements.txt #install all packages needed
```

> in this step, if any wrong occurs, please check requirements.txt. May some packages' version too old
>
> If installing processing is too long, you can manually install these critical packages: 
>
> `python3, vtk, opencv-python, pydicom, pillow, pyqt5, sympy`

Open your Pycharm or other IDE

- open this project
- change the python interpreter. You should replace the path in picture with your own env python path. You can find it by serach in your file explorer. 

![](\pictures source\星愿浏览器截图20211124093000@2x.png)

- run this project

##### Mac or Linux

to do

## Development records

2021-11-1

- 配置虚拟环境，暂时依赖pyqt5, vtk, pyqt5-tools
- pyqt5提供GUI逻辑层，pyqt5-tools自带designer工具，提供UI层，vtk基于C++核心库，提供3D渲染效果
- 复现教程demo https://blog.csdn.net/weixin_34471817/article/details/89714949

<img src="\pictures source\星愿浏览器截图20211101183136@2x.png" style="zoom:33%;" />

2021-11-3

- 创建一个实验分支 learnDemo_one

- 在该分支上使用pyinstaller将程序打包成exe免安装程序

  <img src="\pictures source\星愿浏览器截图20211105174842@2x.png" style="zoom: 50%;" />

2021-11-4

- 尝试vtk的3d渲染，实现平面与半透明球体相交的效果

- 如何实现平面把一个3D物体切开，呈现断面的效果，比较难做

  <img src="\pictures source\星愿浏览器截图20211105175723@2x.png" style="zoom:33%;" />

2021-11-5

- 尝试本地文件的读取window

- 这个功能较为简单，可以抽象成一个独立的widget

  <img src="D:\respository\MRViewer\pictures source\星愿浏览器截图20211105175927@2x.png" style="zoom:33%;" />

2021-11-13

- 实现了窗口页面的基本布局
- 实现了左侧的Dicom列表读取。用到的技术点是
  - QListWidget作为承载的容器，提供了一系列鼠标相关的事件回调
  - QListWidgetItem作为渲染Dicom图像的容器，提供setIcon方法，允许用QIon展示图片
  - QIcon是真正渲染Dicom图像的组件，接收一个Pixmap生成图像
  - Pixmap的生成用到的是pydicom + PIL两个第三方库，能直接从dcm文件生成Pixmap
- 实现了中间的Dicom展示区域中的两个子区域，即三视图中的左视图和俯视图。用到的技术点是
  - vtkDicomImageReader提供读取dcm文件的能力
  - vtkImageViewer2提供渲染图像的窗口

> 在vtk的渲染中遇到很多问题，亟待解决。
>
> 一个是vtk 2d 以及 3d 图像的渲染机制，
>
> 二是为什么窗口加载了数据后默认是不展示图片的，必须要手动调一下visibility，这应该是个bug，
>
> 三是向vtk输入dicom数据，如何不使用vtkDicomImageReader，因为后续工程用的数据格式是h5

<video src="D:\school_files\vedio\录制_2021_11_13_16_33_00_746.mp4" width="800px" height="600px" controls="controls"></video>

2021-11-18

- 实现从2d dicom序列图生成3d vtk图像
  - 基本算法有三种，参考 https://github.com/tgpcai/Dicom_3D_Reconstruction
  - 目前工程使用体绘制算法

<video src="D:\school_files\vedio\录制_2021_11_18_21_19_31_696.mp4" width="800px" height="600px" controls="controls"></video>

2021-11-19

- Double check feature details
- 页面设计
  - 基本菜单栏
  - 左栏文件缩略图列表
  - 中栏文件渲染区
  - 右栏工具区
- 文件缩略图列表
  - Patient-Study-Series 结构
  - Patient层次固定，也就是所有数据只是一个病人的数据
  - Study层次可以是1个，也可以若干个。做成类似文件夹式的折叠效果
  - Series层次一般都是若干个，每一个对应一个特定序列，也对应一个子文件夹。是缩略图列表的最小展示单位
    - 文件夹名称
    - 包含图像数目
    - 选取其中一张作为缩略图
    - Series层次对应的item需要支持拖动效果，拖动到文件渲染区再做监听
- 文件渲染区
  - 基本的四个区域不变，分别是 实时2d图，3d图，独立2d图A，独立2d图B
  - 实时2d图目前搁置，预期效果为
    - 映射到3d图中，渲染一个平面，指示在3d图中的位置
    - 映射到独立2d图A中，渲染一个矩形框，指示在2d图A中的位置
    - 映射到独立2d图B中，效果同A
  - 3d图
    - 可能存在的问题是与实时2d图的图像参数归一化，暂时搁置
    - 渲染的指示平面不可移动，仅作为指示作用
    - 鼠标效果待定，暂时用默认效果
  - 独立2d图A/B
    - 当只使用其中一个时，能作为渲染一个series的窗口。细节是
      - 用户从文件缩略图列表中拖动一个series缩略图到该窗口，松开鼠标
      - 该窗口加载该series中的某一张，选择策略暂定为首张
      - 鼠标与该窗口的交互效果是
        - 左键上下滑动、左右滑动调整窗位窗宽，vtk默认效果即可
        - 右键45度滑动，放缩
        - 滚轮滚动，在该series中切换index
      - 此时窗口默认不渲染右侧的slider
      - 窗口本身除图片外，还需要如FOV的附加信息，默认渲染在右下角，参考radint
    - 当使用两个时，默认布局是左A右B，能各自渲染一个series。细节是
      - 拖动与加载效果同上
      - 此时窗口需要在右侧渲染上slider，slider的滑动对应切换series的index
      - 鼠标与窗口的交互效果也同上
      - 根据两个series的oriention差异大小的程度，有两种情况
        - 差距不大，进行同步处理，在其中一个窗口的切换index事件，会触发另一个窗口相同的切换index事件。两个series之间需要进行序列的配准
        - 差距很大，渲染一个辅助虚线。比如A中的虚线指示B的当前帧在A中的位置，B中的虚线指示A的当前帧在B中的位置。切换index事件触发虚线的更新
  - 实时2d图与独立AB窗口的交互
    - 核心在于将实时2d图映射成一个矩形框
    - 该矩形框需要进行平移、旋转、缩放三种鼠标监听。对应更改Fov，Position，Oriention三个参数
    - 该矩形框的鼠标监听还需要同时触发另一个窗口的随动效果，这一点暂时搁置

- 右栏工具区
  - 可能的功能，如鼠标监听效果的切换，窗口数目的布局，Reset功能，Clear功能...

2021-11-21

- 实现了文件缩略图列表的渲染部分
  - 在菜单栏新增了两个action，openStudy打开一次实验的结果，openPatient打开一个病人的多次实验的结果
  - 两种情况用不同布局实现。study用QListWidget实现，patient用QTreeWidget实现
  - 缩略图选择默认为每个series的第一张图，空series不展示
- 引入问题
  - 缩略图的resize方法暂用opencv的库函数，会导致最后的软件大小膨胀。所以resize函数后期优化时需要自己实现
- 下一步目标
  - UI的美化。包括行高、行间距、字体样式等等
  - series的计数问题，表示当前缩略图在该series中的index
  - 实现series拖动到文件渲染区，然后加载该series这一功能

加载一个Study

<img src="\pictures source\星愿浏览器截图20211121202247@2x.png" style="zoom:33%;" />

加载一个Patient

<img src="\pictures source\星愿浏览器截图20211121202319@2x.png" style="zoom:33%;" />

<img src="\pictures source\星愿浏览器截图20211121202337@2x.png" style="zoom:33%;" />

2021-11-22

- 实现了文件缩略图列表向文件渲染区的基本拖拽功能
  - 用户左键选中一个series item，移动到文件渲染区
  - 文件渲染区目前只保留一个2d渲染窗口和一个3d窗口，默认加载该series的第一张图
- 实现难点
  - 重写鼠标监听事件，重写dropevent相关事件
  - 自定义QMimeData传递数据
- 下一步目标
  - 2d渲染窗口的附加信息，如TR等
  - 文件渲染区的布局管理，目标是1x1，1x2，2x1，2x2四种选择

<video src="D:\school_files\vedio\录制_2021_11_22_20_00_54_405.mp4" width="800px" height="600px" controls="controls"></video>

- 重新优化了下文件缩略图的效果，实现了3d文件渲染区的基本拖拽功能

<video src="D:\school_files\vedio\录制_2021_11_22_21_48_23_424.mp4" width="800px" height="600px" controls="controls"></video>

2021-11-23

- 将目前的工程打包成exe，遇到了一些问题，解决方式记录一下

  - 问题一：导入pydicom后，运行报错，找不到pydicom.encoders.gcdm。解决方法是手动改写pyinstaller生成的spec扩展名文件，修改为hiddenimports=['pydicom.encoders.gdcm']。出现该问题的可能原因是，pyinstaller进行依赖查询时只能查到工程的直接依赖，第三包代码里的间接依赖无法查询，这种被称为隐式依赖，所以需要手动指定

  - 问题二：导入opencv-python后，运行报错，ImportError: OpenCV loader: missing configuration file: [‘config.py‘]。解决方法是手动改写spec文件，修改为pathex=['D:\python\envs\MRViewer\Lib\site-packages\cv2']，其中该路径是python虚拟环境中的cv2的绝对路径。出现该问题原因未知

  - 问题三：打包得到的exe程序启动十分缓慢，短则十余秒，长则一分钟，且文件包体积超过100M。可能的解决方法如下：

    - 配置一个纯净的python环境，不使用anaconda提供的虚拟环境。因为它会额外附加很多东西

    - 工程减少第三包的依赖。目前工程中主要依赖vtk, PyQt5, cv2, PIL, numpy这5个第三方库，其中

      - vtk PyQt5 numpy 必不可少

      - PIL提供把一个Pixmap转为QtIcon的能力，暂未找到替代实现方式，且PIL本身只有3.6M，可以接受

      - **cv2只用到了一个resize功能，且大小高达100M，必须砍掉**

        <img src="\pictures source\星愿浏览器截图20211123160231@2x.png" style="zoom:33%;" />

    - pyinstaller提供了两种打包模式，一是开箱即用，即产物只有一个exe，所有内容全部封装进去，二是提供一个文件夹，里面包含一个exe文件和一堆依赖文件。两种对比

      |          | 开箱即用                                                     | 文件夹封装                                                   |
      | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
      | 样式     | <img src="\pictures source\星愿浏览器截图20211123155535@2x.png" style="zoom:33%;" /> | <img src="\pictures source\星愿浏览器截图20211123155621@2x.png" style="zoom:33%;" /> |
      | 大小     | 116M                                                         | 331M                                                         |
      | 启动速度 | 30s-60s之间                                                  | 10s以内                                                      |
      | 便携程度 | 非常好                                                       | 较差                                                         |

  - 问题四：自定义的包在运行时import error。解决方法是自定义包下的`__init__`文件配置一下`__all__`属性，从而使from module import *能被正常解释

- 提交git遇到个小问题，打包后的文件超过100M被github禁掉了，如果想传大文件，参考https://git-lfs.github.com./。如果只是误传大文件，会导致后续git push一直过不了，因为大文件被github给缓存了，参考https://blog.csdn.net/u014110320/article/details/82841561清缓存，重新push

2021-11-25

- 重构整体的布局，能够自适应屏幕的大小
- 重构文件展示区的布局结构，抽离出其中的layout方法，新增imageShownLayoutController，便于后续能实现文件展示区窗口数量的自定义。
- 遇到一个问题：Windows下程序自带一个标题栏，以及包裹标题栏的边框。在自适应屏幕大小时，需要用整个屏幕的高度减去标题栏的高度，但是在窗口没有渲染出来之前，是无法拿到准确的标题栏高度的，所以导致最后程序的底部会有一小块内容无法展示。
  - 暂时的实现：手动加一个小量 10 pix作为补充
  - 未来的可能实现：在第一次渲染窗口后，重绘一次

<img src="\pictures source\星愿浏览器截图20211125212723@2x.png" style="zoom:33%;" />

2021-11-26

- 实现了文件渲染区的布局管理，支持1x1，1x2，2x1，2x2四种选择
  - 基本实现思路继承imageShownLayoutController，逻辑放在这个辅助类里
- 遇到的问题：
  - 问题一：如何实现仿Excel的表格选择效果。查阅一番资料后选择用QT中tableWidget实现，去掉它的表格头，调整表格item大小。因为tableWidget自带selectedRange回调，能直接拿到用户选择了哪些item这个信息。
  - 问题二：如何实现文件渲染区中，widget自适应layout大小这一功能。正常的实现思路是，嵌套两个布局，把子布局的sizePolicy设置成expanding，这样父布局变化时子布局随之变化。但经一番调试后发现vtk的渲染Widget无论如何也无法自动调整大小，无奈之下，只好使用“危险“的实现方式，重写图像渲染Widget的resizeEvent回调方法，用setFixedSize方法手动调整vtk的渲染窗口大小
- 下一步目标
  - vtk窗口附加信息的丰富，以及其中图片大小和角度等参数的自动化调整
  - 多个窗口之间的信息交互，首先是指示线的渲染

<video src="D:\school_files\vedio\录制_2021_11_26_17_49_57_685.mp4" width="800px" height="600px" controls="controls"></video>

2021-11-27

- 实现了文件渲染区中，2d图像基本的附加信息
  - 以标注的形式，在原图上添加一些文本，标记该张dcm文件的一些重要信息
  - 目前只添加了MR的关键参数 TR 和 TE
- 实现思路：
  - 标注性的文本应该依附于图像所在的Widget，同时又要保持背景透明效果。依次尝试以下思路
  - 思路一：用QLabel承载文本，设置背景透明。失败。因为QLabel透明后，背景色继承其父Widget，也就是QFrame的背景色，而不是继承其下一个layer：QVtkWidget的颜色。所以QLabel会遮挡图像
  - 思路二：用QPainter直接绘制文本，设置背景透明。失败。因为本质上QLabel其实调用的就是QPainter，没有太大区别，同样会遮挡图像
  - 思路三：用QGraphicView重新绘制整个图像，添加一个text图元来展示文本。失败。其实这个思路实现普通的qt程序应该是可以的，而且这个机制可以绘制大量图元而不卡顿，性能很好。但遗憾的是本程序的图像用QVtkWidget绘制，不太方便嵌入到QGraphicView中（应该也可以，只是我不会）
  - 思路四：直接调用VTK的VTKTextActor，直接在qvtkWidget中生成一个文本。这个是VTK的原生功能，查阅一圈才发现。成功！
- 下一步目标：
  - 支持多行文本
  - 封装更完善更易用的附加信息类
  - 优化文本的Position控制

<img src="\pictures source\星愿浏览器截图20211127204902@2x.png" style="zoom:33%;" />

2021-11-29

- 实现文件渲染区的多行文本，附加信息暂时用Dict去描述，文本的Position控制暂定左下角
- 遇到的问题：
  - 原计划重构文件渲染区中的m2DImageShownWidget结构，反复调试后始终被一个Bug卡住。即当QVTKRenderWindowInteractor被m2DImageShownWidget固定持有时，会发现在调整渲染区布局时，一个widget的内容会被渲染到其余的widget中，猜测是vtk进行渲染时做了什么优化引起的。暂无修复思路

<img src="\pictures source\星愿浏览器截图20211129151353@2x.png" style="zoom:33%;" />

- **[陶然]** 实现了文件渲染区的滚动切换slice功能
  - 基本思路是重写相关widget的wheelEvent方法

<video src="D:\school_files\vedio\录制_2021_11_29_16_30_53_323.mp4" width="800px" height="600px" controls="controls"></video>

2021-11-30

- 实现了基本的CrossView功能，能支持CrossXZ和CrossYZ之间的同步
- 遇到的问题
  - 问题一：VTK的四个坐标系统的概念，没搞明白
  - 问题二：VTK的四个坐标系之间如何变换，也没搞明白
- 暂时的实现方式：
  - 交线的求取：复现别人的代码，思路还没搞明白
  - 交线坐标映射到Display坐标系：用的一些列骚操作，有很多隐患
  - 线框View的渲染：用的是vtkBorderWidget，这个非常好用，还支持拖拽等事件监听
- 剩余问题：
  - 第一次初始化时，由于目前的映射操作依赖于Render，而目前的初始化时机不佳，执行映射操作时Render还未初始化结束，所以CrossYZ的初始化位置不正确
  - 同样是因为映射操作的不完善，如果用户拖动了图像的缩放中心，映射结果就会有问题
  - Study Test数据存在Crash，原因未知
- 下一步实现
  - 加上安全保护，使得如果两个Series没有交线，则隐藏vtkBorderWidget
  - 重构映射操作
  - 可能要支持vtkBorderWidget的拖放事件

```python
 def getX(self,f1,f2):
        #get info
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= self.getinfo(f1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = self.getinfo(f2)

        #建立方程组
        sp.init_printing(use_unicode=True)
        x, y, z = sp.symbols('x, y, z')
        eq=[normalvector1[0] * (x - ImagePosition1[0]) + normalvector1[1] * (y - ImagePosition1[1]) + normalvector1[2] * (z - ImagePosition1[2]),\
            normalvector2[0] * (x - ImagePosition2[0]) + normalvector2[1] * (y - ImagePosition2[1]) + normalvector2[2] * (z - ImagePosition2[2])]

         #解方程
        s = list(sp.linsolve(eq, [x, y]))
        if len(s) < 1: return Status.bad

        #求2d交线
        x, y, z = sp.symbols('x, y, z')
        x1_3d = s[0][0]
        y1_3d = s[0][1]

        pos=[x1_3d,y1_3d,z]
		
        #x1,x2即为交线投影在两个Image中的col坐标
        differ1=pos-ImagePosition1
        differ1_x=np.dot(differ1,ImageOrientationX1)
        x1 = differ1_x/PixelSpacing1[0]

        differ2=pos-ImagePosition2
        differ2_x=np.dot(differ2,ImageOrientationX2)
        x2 = differ2_x/PixelSpacing2[0]

        #计算Display坐标系下，Image的中心位置和右下角边界位置
        #然后得到Image的ColWidth
        imageCenterPoint1,imageBoundPoint1 = self.getImageCenterAndBoundPos(self.crossXZContainer)
        imageWidth1 = 2 * (imageBoundPoint1[0] - imageCenterPoint1[0])
        imageCenterPoint2,imageBoundPoint2 = self.getImageCenterAndBoundPos(self.crossYZContainer)
        imageWidth2 = 2 * (imageBoundPoint2[0] - imageCenterPoint2[0])
		
        #计算交线的col坐标在Display坐标系下的对应位置
        x1 = int((x1 / Cols1)*imageWidth1 + imageCenterPoint1[0] - imageWidth1/2)
        x2 = int((x2 / Cols2)*imageWidth2 + imageCenterPoint2[0] - imageWidth2/2)
        
        #除以总的窗口宽度得到比例值
        x1 = x1 / self.crossXZContainer.width()
        x2 = x2 / self.crossYZContainer.width()
        return (x1,x2)

def getImageCenterAndBoundPos(self, m2DWidget):
        focal = m2DWidget.renImage.GetActiveCamera().GetFocalPoint()
        m2DWidget.renImage.SetWorldPoint(focal[0],focal[1],focal[2],0)
        m2DWidget.renImage.WorldToDisplay()
        imageCenterPoint = m2DWidget.renImage.GetDisplayPoint()

        bounds = m2DWidget.imageViewer.GetImageActor().GetBounds()
        colBound,rowBound = bounds[1],bounds[3]
        m2DWidget.renImage.SetWorldPoint(colBound,rowBound,focal[2],0)
        m2DWidget.renImage.WorldToDisplay()
        imageBoundPoint = m2DWidget.renImage.GetDisplayPoint()

        return (imageCenterPoint,imageBoundPoint)

def showCrossView(self):
        self.crossView = vtk.vtkBorderWidget()
        self.crossView.SetInteractor(self.qvtkWidget.GetRenderWindow().GetInteractor())
        self.crossView.CreateDefaultRepresentation()
        #这里的position是左下角的比例位置, position2是宽和高
        self.crossView.GetRepresentation().SetPosition(self.crossViewColRatio,0.05)
        self.crossView.GetRepresentation().SetPosition2(0.01,0.9)
        self.crossView.GetRepresentation().GetBorderProperty().SetColor(1,0,0)
        self.crossView.GetRepresentation().GetBorderProperty().SetLineWidth(3)
        self.crossView.ResizableOff()
        # self.crossView.SelectableOff() 设置是否可拖动
        self.crossView.On()
        #
        # self.renCrossView = vtk.vtkRenderer()
        # self.renCrossView.SetLayer(1)
        # self.crossView.SetCurrentRenderer(self.renCrossView)
        # self.qvtkWidget.GetRenderWindow().AddRenderer(self.renCrossView)
        self.renderVtkWindow()
```

<video src="D:\school_files\vedio\录制_2021_11_30_21_41_43_998.mp4" width="800px" height="600px" controls="controls"></video>

2021-12-1

- 修复了Study Case崩溃的bug
- 实现了横纵两个方向的CrossView
  - 交线求取的代码搞懂了原理，并重新实现了一遍

<img src="\pictures source\星愿浏览器截图20211201093205@2x.png" style="zoom:33%;" />

2021-12-7

- 修复了多个扩展屏幕时，mainWindow读取屏幕尺寸异常的bug
  - 待测试
- 重构了ImageShownContainer的自动layout功能，仿Radint效果
- 重构了文件缩略图列表的item样式，实现上文字，下图片的效果
- 完善了文件渲染区的自动轮播效果
  - 基本功能已实现，后续重构文件渲染区的item时还需要调试
- 实现了三个区域的splitter调节，允许用户调节各区域宽度
  - 文件缩略图列表只重绘了item的背景部分
  - 文件渲染区只重绘了每个item的大小，里面的image没有重绘
  - 工具栏没有对item重绘

- 遇到的难点与解决方案
  - 问题一：扩展屏幕。暂定用Qt的destop对象暴露的方法，效果未知
  - 问题二：自动layout的仿Radint效果。原实现方式是用tableWidget，难以调节，不优雅。现方案是用gridLayout + 自定义Widget，重写mouseMoveEvent和mousePressEvent实现事件监听。扩展性强，交互优雅
  - 问题三：缩略图列表的item自定义。由于缩略图列表用了listWidget和treeWidget作为容器，所以采用它们的item的父类暴露的方法，用委托模式，自定义一个imageItemDelegata渲染器，重写paint事件，手动计算好位置，并绘制图片和相关文字。最后实例化该渲染器并设置给缩略图列表容器即可
  - 问题四：自动轮播时的异步操作。由于自动轮播需要开启一个周期性死循环任务，如果放在主线程，会阻塞UI操作，用户无法与其他组件交互。所以只能开一个子线程执行该任务。踩了一些坑后找到了QT子线程执行周期任务的正确姿势，在子线程中持有一个signal，主线程connet该signal，子线程周期性emit该signal即可。注意qt子线程的退出较为繁琐，不能强退

2021-12-8

- 实现了渲染区的title
- 重构并优化了渲染区的子container
  - 目的是让四个container都持有同一套功能，便于模式切换
- 重构自动轮播功能，兼容新的container
- 实现了模式切换
  - 暂时只实现了2D和3D的切换

<img src="\pictures source\星愿浏览器截图20211208235216@2x.png" style="zoom:33%;" />