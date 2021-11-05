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

