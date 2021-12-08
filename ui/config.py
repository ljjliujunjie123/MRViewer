import sys
from PyQt5.QtCore import QSize,QRect,QMargins

class UIConfig():

    screenWidth = 1000
    screenHeight = 800

    menuHeight = 22

    scrollContinerColRatio = 1
    shownContainerColRatio = 4
    toolsContainerColRation = 1

    shownContainerMargins = QMargins(0,0,0,0)
    shownContainerContentSpace = 4
    shownTextInfoMarginWidth = 20
    shownTextInfoMarginHeight = 0

    shownSlideShowDialogSize = QSize(300,100)
    shownSlideSpeedMax = 0.1 #时间间隔
    shownSlideSpeedMin = 1

    toolsSelectRegionCol = 2
    toolsSelectRegionRow = 2
    toolsSelectRegionItemSize = QSize(80,80)

    totalColRation = scrollContinerColRatio + shownContainerColRatio + toolsContainerColRation

    studyTag = 1
    patientTag = 2

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
            (self.screenWidth // self.totalColRation) * self.scrollContinerColRatio,
            self.calcCenterWidgetHeight()
        )

    def calcShownContainerGeometry(self):
        return QRect(
            (self.screenWidth // self.totalColRation) * self.scrollContinerColRatio,
            0,
            (self.screenWidth // self.totalColRation) * self.shownContainerColRatio,
            self.calcCenterWidgetHeight()
        )

    def calcToolsContainerGeometry(self):
        return QRect(
            (self.screenWidth // self.totalColRation) * self.scrollContinerColRatio +
            (self.screenWidth // self.totalColRation) * self.shownContainerColRatio,
            0,
            (self.screenWidth // self.totalColRation) * self.toolsContainerColRation,
            self.calcCenterWidgetHeight()
        )


uiConfig = UIConfig()