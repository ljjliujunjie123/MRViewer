import sys
from PyQt5.QtCore import QSize,QRect,QMargins

class UIConfig():
    #主页面size
    screenWidth = 1000
    screenHeight = 800

    #缩放最小大小
    centralWidgetMinSize = QSize(800,600)

    #菜单高度
    menuHeight = 22

    
    scrollContainerHintWidth = 300
    toolsContainerHintWidth = 100

    shownContainerMargins = QMargins(0,0,0,0)
    shownContainerContentSpace = 4
    shownTextInfoX = 20
    shownTextInfoY = 10

    shownSlideShowDialogSize = QSize(300,100)
    shownSlideSpeedDefault = 0.2
    shownSlideSpeedMax = 0.05 #时间间隔
    shownSlideSpeedMin = 1

    toolsSelectRegionCol = 2
    toolsSelectRegionRow = 2
    toolsSelectRegionItemSize = QSize(50,50)

    imageModeIconSize = QSize(80,80)

    studyTag = 1
    patientTag = 2

    itemHintSize = QSize(280,300)
    itemSpace = 2
    iconSize = QSize(280,280)
    textHeight = 40
    annotationSize = QSize(40,20)
    iconTextSpace = 10
    listHeight = 1000

    factor_bright = 1
    factor_contrast = 1
    autocontrast_mode = 0
    inversion_mode = 0
    width_of = 450

    def __init__(self):
        print("UI Config Init.")

    def setScreenSize(self, width, height):
        self.screenWidth, self.screenHeight =  width, height

    def calcCenterWidgetHeight(self):
        return self.screenHeight - self.menuHeight

    def calcCenterWidgetGeometry(self):
        return QRect(0, 0,
            self.screenWidth, self.calcCenterWidgetHeight()
        )

    def calcShownContainerWidth(self):
        return (self.screenWidth - self.scrollContainerHintWidth - self.toolsContainerHintWidth)
          




uiConfig = UIConfig()