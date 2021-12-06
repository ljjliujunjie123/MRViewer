import sys
from PyQt5.QtWidgets import QApplication,QStyle
from ui.LJJMainWindow import LJJMainWindow
from ui.config import uiConfig

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #to do
    #这里有个高度的问题，目前在window没有渲染之前无法拿到正确的标题栏的高度
    #暂时的想法是在window show一次之后进行重绘
    #可能会导致卡顿，暂时的解决思路是加一个小量10 pix作为补充

    curMonitorNum = app.desktop().primaryScreen()
    screenRect = app.desktop().screenGeometry(curMonitorNum)
    uiConfig.setScreenSize(screenRect.width(),
                           screenRect.height() - QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight) - 10)
    mainWindow = LJJMainWindow()
    sys.exit(app.exec_())

