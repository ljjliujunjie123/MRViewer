1. 通过修改了ui\SingleImageShownContainer.py、ui\ToolsFactory.py、ui\ToolsContainer.py、controller\ImageShownLayoutController.py 完成了按钮、图片双向调控

2021-12-30
1. 修改了ui\m2DImageShownWidget.py、ui\mRealTimeImageShownWidget.py、utils\util.py中的getImageExtraInfoFromDicom
2. ui\config.py中将变量名改短：shownTextInfoMarginWidth, shownTextInfoMarginHeight  -> shownTextInfoX, shownTextInfoY

2022-1-5
1. 3D Orientation Marker
2. 修改了ui\m2DImageShownWidget.py，修正extra text 无法resize的问题，简化了部分代码
3. 修改了ui\m2DImageShownWidget.py，utils\util.py，美化代码

2022-1-10
1. 美化界面ver1.0.0

2022-2-23
1. 不稳定版5x5网格

2022-4-6
1. 数据库版，可以读取文件夹下所有的dcm文件，按内部序列号区分。