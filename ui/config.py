import sys
from PyQt5.QtCore import QSize,QRect,QMargins

class UIConfig():

    screenWidth = 1000
    screenHeight = 800

    centralWidgetMinSize = QSize(800,600)

    menuHeight = 22

    shownContainerColRatio = 4
    toolsContainerColRation = 1

    scrollContainerHintWidth = 400

    shownContainerMargins = QMargins(0,0,0,0)
    shownContainerContentSpace = 4
    shownTextInfoX = 20
    shownTextInfoY = 0

    shownSlideShowDialogSize = QSize(300,100)
    shownSlideSpeedDefault = 0.2
    shownSlideSpeedMax = 0.05 #时间间隔
    shownSlideSpeedMin = 1

    toolsSelectRegionCol = 2
    toolsSelectRegionRow = 2
    toolsSelectRegionItemSize = QSize(80,80)

    imageModeIconSize = QSize(80,80)
    totalColRation = shownContainerColRatio + toolsContainerColRation

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

    def calcScrollContainerGeometry(self):
        return QRect(0, 0,
                     self.scrollContainerHintWidth,
                     self.calcCenterWidgetHeight()
                     )

    def calcShownContainerGeometry(self):
        return QRect(
            self.scrollContainerHintWidth,
            0,
            ((self.screenWidth - self.scrollContainerHintWidth) // self.totalColRation) * self.shownContainerColRatio,
            self.calcCenterWidgetHeight()
        )

    def calcToolsContainerGeometry(self):
        return QRect(
                self.scrollContainerHintWidth +
                ((self.screenWidth - self.scrollContainerHintWidth) // self.totalColRation) * self.shownContainerColRatio,
            0,
                ((self.screenWidth - self.scrollContainerHintWidth) // self.totalColRation) * self.toolsContainerColRation,
            self.calcCenterWidgetHeight()
        )


uiConfig = UIConfig()