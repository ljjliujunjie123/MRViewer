import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from ui.LJJMainWindow import LJJMainWindow
from ui.config import uiConfig
from ui.mGraphicRectItem import mGraphicRectItem

# D:\python\envs\MRViewer\Lib\site-packages\PyQt5\Qt5\plugins
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #to do
    #这里有个高度的问题，目前在window没有渲染之前无法拿到正确的标题栏的高度
    #暂时的想法是在window show一次之后进行重绘
    #可能会导致卡顿，暂时的解决思路是加一个60 pix作为补充

    curMonitorNum = app.desktop().primaryScreen()
    screenRect = app.desktop().screenGeometry(curMonitorNum)
    uiConfig.setScreenSize(screenRect.width(),screenRect.height() - 60)
    mainWindow = LJJMainWindow()
    # 用于演示新版CrossView
    scene = QGraphicsScene()
    scene.setBackgroundBrush(Qt.black)

    scene.addItem(mGraphicRectItem())

    view = QGraphicsView(scene)
    view.resize(1024, 768)
    view.show()
    sys.exit(app.exec_())

