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