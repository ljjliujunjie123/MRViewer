from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.m2DImageShownWidget import m2DImageShownWidget
from ui.m3DImageShownWidget import m3DImageShownWidget
from ui.config import uiConfig

from copy import deepcopy

class ImageShownLayoutController():

    def __init__(
            self,
            imageShownContainerWidget,
            imageShownContainerLayout
    ):
        self.imageShownContainerWidget = imageShownContainerWidget
        self.imageShownContainerLayout = imageShownContainerLayout

        self.curlayout = (0, 0, 1, 1)
        self.imageShownWidgetPool = { }

    def initLayoutParams(self, uiConfig):
        self.imageShownContainerLayout.setContentsMargins(uiConfig.shownContainerMargins)
        self.imageShownContainerLayout.setSpacing(uiConfig.shownContainerContentSpace)
        self.imageShownContainerLayout.setObjectName("imageGridShownContainer")

    def initWidget(self):
        self.RealTimeContainer = m2DImageShownWidget()
        self.vtk3DContainer = m3DImageShownWidget()
        self.crossXZContainer = m2DImageShownWidget()
        self.crossYZContainer = m2DImageShownWidget()

        self.addWidget(self.RealTimeContainer, 0, 0)
        self.addWidget(self.vtk3DContainer, 0, 1)
        self.addWidget(self.crossXZContainer, 1, 0)
        self.addWidget(self.crossYZContainer, 1, 1)

        self.imageShownWidgetPool[(0, 0)] = self.RealTimeContainer
        self.imageShownWidgetPool[(0, 1)] = self.vtk3DContainer
        self.imageShownWidgetPool[(1, 0)] = self.crossXZContainer
        self.imageShownWidgetPool[(1, 1)] = self.crossYZContainer

    def addWidget(self, childWidget, row, col, rowSpan = 1, colSpan = 1):
        self.imageShownContainerLayout.addWidget(childWidget, row, col, rowSpan, colSpan)

    def updateLayout(self, layoutTuple):
        if layoutTuple == self.curlayout: return
        self.curlayout = deepcopy(layoutTuple)

        topRow, leftCol, bottomRow, rightCol = layoutTuple

        #从Layout移除所有子Widget
        for i in reversed(range(self.imageShownContainerLayout.count())):
            widget = self.imageShownContainerLayout.itemAt(i).widget()
            print(widget.geometry())
            widget.setParent(None)
        print(self.imageShownContainerLayout.count())

        #重新向Layout中添加子Widget
        rowSpan = uiConfig.toolsSelectRegionRow - bottomRow
        colSpan = uiConfig.toolsSelectRegionCol - rightCol
        for row in range(topRow, bottomRow + 1):
            for col in range(leftCol, rightCol + 1):
                childWidget = self.imageShownWidgetPool[(row, col)]
                self.addWidget(childWidget, row, col, rowSpan, colSpan)

