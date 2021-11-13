from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


# 模式对话窗口和非模式对话窗口 https://www.jb51.net/article/208142.htm

class FileFolderWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.setObjectName("FileFolderWindow")
        self.setWindowTitle("FileFolderWindow")
        self.resize(1500,1000)

        self.treeView = QTreeView(self)
        self.treeView.setGeometry(QRect(0,0,1500,1000))

        QMetaObject.connectSlotsByName(self)
        model = QDirModel()
        self.treeView.setModel(model)
        self.treeView.setColumnWidth(0,800)
        self.treeView.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.treeView.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.treeView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.treeView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treeView.setAutoExpandDelay(-1)
        self.treeView.setItemsExpandable(True)
        self.treeView.setSortingEnabled(True)
        self.treeView.setWordWrap(True)
        self.treeView.setHeaderHidden(True)
        self.treeView.setExpandsOnDoubleClick(True)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setVisible(True)

        self.retranslateUI()

    def retranslateUI(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("FileFolderWindow","FileFolderWindow"))