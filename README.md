预期
self.setCentralWidget(self.centralwidget)
tools 中加一个 checkbox signal ->改变container状态
如何把按钮变灰*
加在 controller\ImageShownLayoutController.py 里（位置量）
container -> m2D
m2d->窗口位置设置
window.getImagePlayShow
按钮png方icon里setwenzi 空
layout变换问题*
轮播问题
1.禁止*

2021-12-4
1. 在ui\LJJMainWindow.py中添加“跑马灯”选项
2. 添加注释并优化ui\m2DImageShownWidget.py中的滚轮事件
3. 改正ui\m2DImageShownWidget.py中的wheelEvent在未放入图时崩溃问题
4. 添加ui\SlideshowContainer.py控制播放器窗口，可拖动但没写信号传递, 背景颜色需要调整