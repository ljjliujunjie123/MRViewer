from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.ImagesScrollContainer import ImageScrollContainer
from ui.ToolsContainer import ToolsContainer
from ui.ImageShownContainer import ImageShownContainer
from utils.status import Status

class LJJMainWindow(QMainWindow):

    updateImageShownSignal = pyqtSignal(str,str)
    updateImageListSignal = pyqtSignal(list)

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

        #菜单栏部分
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

        #菜单-文件浏览窗口
        self.fileFolderWindow = None

        #信号绑定部分
        self.updateImageShownSignal.connect(self.updateImageShownArea)
        self.updateImageListSignal.connect(self.updateImageListArea)
        self.actionopen_file.triggered.connect(self.openFileFolderWindow)

        self.toolsContainer.showInfoSig.connect(self.showLevelAndWindowInfo)

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
        fileNames = QFileDialog.getOpenFileNames(self,'选择文件','','')[0]
        fileCount = len(fileNames)
        if fileCount < 1:
            QMessageBox.information(None,"提示","请至少选择一个文件",QMessageBox.Ok)
            return
        elif fileCount < 2:
            self.updateImageShownSignal.emit(fileNames[0],'')
        else:
            self.updateImageShownSignal.emit(fileNames[0],fileNames[1])

        self.updateImageListSignal.emit(fileNames)

    def updateImageShownArea(self,fileNameXZ,fileNameYZ):
        self.imageShownContainer.hideXZandYZDicom()
        if fileNameXZ is not '': self.imageShownContainer.showXZDicom(fileNameXZ)
        if fileNameYZ is not '': self.imageShownContainer.showYZDicom(fileNameYZ)

    def updateImageListArea(self,fileNames):
        status = self.imageScrollContainer.updateListHeight(len(fileNames))
        if status is Status.bad:
            return
        self.imageScrollContainer.clearImageList()
        for index,fileName in enumerate(fileNames):
            self.imageScrollContainer.addImageItem(fileName,index)

    def showLevelAndWindowInfo(self):
        levelXZ = self.imageShownContainer.imageViewerXZ.GetColorLevel()
        windowXZ = self.imageShownContainer.imageViewerXZ.GetColorLevel()

        levelYZ = self.imageShownContainer.imageViewerYZ.GetColorLevel()
        windowYZ = self.imageShownContainer.imageViewerYZ.GetColorLevel()

        info = "XZ:" + str(levelXZ) + " " + str(windowXZ) + " YZ:" + str(levelYZ) + " " + str(windowYZ)

        QMessageBox.information(None,"展示信息",info, QMessageBox.Ok)

    def closeEvent(self,QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageScrollContainer.closeEvent(QCloseEvent)
        self.imageShownContainer.closeEvent(QCloseEvent)


