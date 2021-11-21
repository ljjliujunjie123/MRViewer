## Introduction

这是一个辅助心血管导航的GUI软件，提供实时的MR图像渲染

## Development records

2021-11-1

- 配置虚拟环境，暂时依赖pyqt5, vtk, pyqt5-tools
- pyqt5提供GUI逻辑层，pyqt5-tools自带designer工具，提供UI层，vtk基于C++核心库，提供3D渲染效果
- 复现教程demo https://blog.csdn.net/weixin_34471817/article/details/89714949

<img src=".\pictures source\星愿浏览器截图20211101183136@2x.png" style="zoom:33%;" />

2021-11-3

- 创建一个实验分支 learnDemo_one

- 在该分支上使用pyinstaller将程序打包成exe免安装程序

  <img src=".\pictures source\星愿浏览器截图20211105174842@2x.png" style="zoom: 50%;" />

2021-11-4

- 尝试vtk的3d渲染，实现平面与半透明球体相交的效果

- 如何实现平面把一个3D物体切开，呈现断面的效果，比较难做

  <img src=".\pictures source\星愿浏览器截图20211105175723@2x.png" style="zoom:33%;" />

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
- 遗留问题
  - UI的美化。包括行高、行间距、字体样式等等
  - series的计数问题，表示当前缩略图在该series中的index
  - 缩略图的resize方法暂用opencv的库函数，会导致最后的软件大小膨胀。所以resize函数后期优化时需要自己实现
- 下一步目标
  - 实现series拖动到文件渲染区，然后加载该series这一功能

加载一个Study

<img src="D:\respository\MRViewer\pictures source\星愿浏览器截图20211121202247@2x.png" style="zoom:33%;" />

加载一个Patient

<img src="D:\respository\MRViewer\pictures source\星愿浏览器截图20211121202319@2x.png" style="zoom:33%;" />

<img src="D:\respository\MRViewer\pictures source\星愿浏览器截图20211121202337@2x.png" style="zoom:33%;" />