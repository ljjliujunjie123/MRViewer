from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.config import uiConfig

class CustomSelectRegionTableWidget(QTableWidget):

    def __init__(self):
        QTableWidget.__init__(self)

        width = uiConfig.toolsSelectRegionCol * uiConfig.toolsSelectRegionItemSize.width()
        height = uiConfig.toolsSelectRegionRow * uiConfig.toolsSelectRegionItemSize.height()
        self.setFixedSize(width,height)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.setColumnCount(uiConfig.toolsSelectRegionCol)
        self.setRowCount(uiConfig.toolsSelectRegionRow)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setAllColWidth(uiConfig.toolsSelectRegionItemSize.width())
        self.setAllRowHeight(uiConfig.toolsSelectRegionItemSize.height())

    def setAllColWidth(self, width):
        for i in range(self.columnCount()):
            self.setColumnWidth(i, width)

    def setAllRowHeight(self, height):
        for i in range(self.rowCount()):
            self.setRowHeight(i, height)
