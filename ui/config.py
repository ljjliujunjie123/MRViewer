import sys
from PyQt5.QtCore import QSize,QRect,QMargins

class UIConfig():
    #主页面size
    screenWidth = 1000
    screenHeight = 800

    #缩放最小大小
    centralWidgetMinSize = QSize(800,600)

    #菜单高度
    menuHeight = 30

    scrollContainerHintWidth = 300
    toolsContainerHintWidth = 120

    scrollRootItemHeight = 50

    shownContainerMargins = QMargins(0,0,0,0)
    shownContainerContentSpace = 5
    shownContainerTitleHeight = 40
    shownTextInfoX = 20
    shownTextInfoY = 10

    shownSlideShowDialogSize = QSize(240,65)
    shownSlideShowPlayIconSize = QSize(30,30)
    shownSlideShownSpeedIconSize = QSize(30,20)
    shownSlideSpeedDefault = 10
    shownSlideSpeedMax = 100 #时间间隔
    shownSlideSpeedMin = 1

    toolsSelectRegionCol = 5
    toolsSelectRegionRow = 5
    toolsSelectRegionItemSize = QSize(50,50)

    toolsIconSize = QSize(80,80)

    studyTag = 1
    patientTag = 2

    itemHintSize = QSize(280,300)
    itemSpace = 5
    iconSize = QSize(280,280)
    textHeight = 40
    annotationSize = QSize(30,30)
    specialSymbolSize = QSize(40,40)
    iconTextSpace = 10
    listHeight = 1000

    factor_bright = 1
    factor_contrast = 1
    autocontrast_mode = 0
    inversion_mode = 0
    width_of = 450

    class LightColor():
        Primary = "#f3fef2"
        Complementary = "#fbeade"
        Analogous1 = "#f9fef2"
        Black = "#000000"
        White = "#ffffff"

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
          
    # def calcVtkImageContainerSize(self):
    #     """重设单个Vtk大小，防止压缩其他区域"""
    #     return QSize(
    #         (self.calcShownContainerWidth() - self.shownContainerContentSpace * (self.toolsSelectRegionCol - 1) - self.shownContainerMargins.left() - self.shownContainerMargins.right()) // self.toolsSelectRegionCol,
    #         (self.calcCenterWidgetHeight() - self.shownContainerContentSpace * (self.toolsSelectRegionRow - 1) - self.shownContainerMargins.top() - self.shownContainerMargins.bottom()) // self.toolsSelectRegionRow,
    #     )



uiConfig = UIConfig()