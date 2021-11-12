from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.ImagesScrollContainer import ImageScrollContainer
from ui.ToolsContainer import ToolsContainer
from ui.ImageShownContainer import ImageShownContainer


class LJJMainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setObjectName("MainWindow")
        self.resize(2000, 1200)
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        #抽象出右侧的工具栏
        self.toolsContainer = ToolsContainer(self.centralwidget)

        #抽象出中间的image展示区域
        self.imageShownContainer = ImageShownContainer(self.centralwidget)

        #抽象出左侧的image列表
        self.imageScrollContainer = ImageScrollContainer(self.centralwidget)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 2000, 22))
        self.menubar.setObjectName("menubar")
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.actionopen_file = QAction(self)
        self.actionopen_file.setObjectName("actionopen_file")
        self.menu.addAction(self.actionopen_file)
        self.menubar.addAction(self.menu.menuAction())

        self.actionopen_file.triggered.connect(self.openFileFolderWindow)

        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

        self.show()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.actionopen_file.setText(_translate("MainWindow", "打开文件"))

        self.toolsContainer.retranslateUi()

    def openFileFolderWindow(self):
        print("触发openFile")
        fileExploreDialog = QFileDialog()
        fileExploreDialog.setFileMode(QFileDialog.ExistingFiles)
        fileExploreDialog.setFixedWidth(1800)
        fileExploreDialog.setFixedHeight(1000)
        fileExploreDialog.show()
        if fileExploreDialog.exec_():
            self.imageScrollContainer.initImages(fileExploreDialog.selectedFiles())

    def closeEvent(self,QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageScrollContainer.closeEvent(QCloseEvent)
        self.imageShownContainer.closeEvent(QCloseEvent)


