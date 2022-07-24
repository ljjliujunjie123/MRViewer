## 2022-6-21
1. 初步完成标题栏和侧边栏一
   
## 2022-6-28 am
1. 完成标题栏并简化部分代码
2. 导入展示图片相关py文件进入ui文件夹

## 2022-6-28 pm
1. m2DImageShownWidget去除slideshow功能
2. 修改了DisplayArea中database部分和image部分，初步完成布局

## 2022-6-29

## 2022-6-30
1. 修改database部分
2. 新增按钮以及滑块

## 2022-7-2
1. qss美化

## 2022-7-18
1. 加入选择图像的滚动窗口，准备解决pixelarray传输问题
2. 未解决pixelarray传输问题，改为传输path，暂无2D/3D选项

## 2022-7-22
1. PreImageDisplayer 与 IntraImageDisplayer 分离。前者沿用LJJ的ImageShownContainer结构。后者运用3-by-1布局。

## 2022-7-24
1. 完善布局，RT(RealTime)起步阶段。
2. Config.py中存储RT的三个文件夹
3. 存在无法读取的情况如
        ERROR: In ..\IO\Image\vtkDICOMImageReader.cxx, line 264
        vtkDICOMImageReader (000001AB1B3F45E0): There was a problem retrieving data from: E:/research/MRViewer_test/MRNewUI/mock_dicoms2//TEST0722.MR.IMR-SJTU_ZSJ.0059.0003.2022.07.23.16.56.39.512788.55368191.IMA

        ERROR: In ..\Common\ExecutionModel\vtkExecutive.cxx, line 753
        vtkCompositeDataPipeline (000001AB1B505FF0): Algorithm vtkDICOMImageReader(000001AB1B3F45E0) returned failure for request: vtkInformation (000001AB1B51A250)
        Debug: Off
        Modified Time: 7611
        Reference Count: 1
        Registered Events: (none)
        Request: REQUEST_DATA
        FORWARD_DIRECTION: 0
        ALGORITHM_AFTER_FORWARD: 1
        FROM_OUTPUT_PORT: 0