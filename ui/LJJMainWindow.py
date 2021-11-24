from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from controller.OpenFileController import OpenFileController
from ui.config import *
from ui.ImagesScrollContainer import ImageScrollContainer
from ui.ToolsContainer import ToolsContainer
from ui.ImageShownContainer import ImageShownContainer
from utils.status import Status

import os

class LJJMainWindow(QMainWindow):

    updateImageShownSignal = pyqtSignal(str,str)
    updateImageListSignal = pyqtSignal(dict,int)
    updateImage3DShownSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setObjectName("MainWindow")
        self.resize(2400, 1600)
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
        self.menubar.setGeometry(QRect(0, 0, 2400, 22))
        self.menubar.setObjectName("menubar")
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.actionopen_study = QAction(self)
        self.actionopen_study.setObjectName("actionopen_study")
        self.actionopen_patient = QAction(self)
        self.actionopen_patient.setObjectName("actionopen_patient")

        self.menu.addAction(self.actionopen_study)
        self.menu.addAction(self.actionopen_patient)
        self.menubar.addAction(self.menu.menuAction())

        #初始化controllers
        self.openFileController = OpenFileController(
            self,
            self.imageScrollContainer,
            self.updateImageListSignal
        )

        #信号绑定部分
        self.updateImageListSignal.connect(self.updateImageListArea)
        self.actionopen_study.triggered.connect(self.openFileController.openStudyDirectory)
        self.actionopen_patient.triggered.connect(self.openFileController.openPatientDirectory)
        self.toolsContainer.showInfoSig.connect(self.showLevelAndWindowInfo)

        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

        self.show()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.actionopen_study.setText(_translate("MainWindow", "打开Study"))
        self.actionopen_patient.setText(_translate("MainWindow", "打开Patient"))

        self.toolsContainer.retranslateUi()

    def updateImageListArea(self, dict, tag):
        self.imageScrollContainer.initImageListView(tag)
        if tag is studyTag:
            status = self.imageScrollContainer.updateListHeight(len(dict.keys()))
            if status is Status.bad: return

        if tag is patientTag:
            count = sum([len(study.keys()) for study in list(dict.values())])
            status = self.imageScrollContainer.updateListHeight(count)
            if status is Status.bad: return

        self.imageScrollContainer.clearImageList()
        self.imageScrollContainer.showImageList(dict, tag)

    def showLevelAndWindowInfo(self):
        levelXZ = self.imageShownContainer.imageViewerXZ.GetColorLevel()
        windowXZ = self.imageShownContainer.imageViewerXZ.GetColorWindow()

        levelYZ = self.imageShownContainer.imageViewerYZ.GetColorLevel()
        windowYZ = self.imageShownContainer.imageViewerYZ.GetColorWindow()

        info = "XZ:" + str(levelXZ) + " " + str(windowXZ) + " YZ:" + str(levelYZ) + " " + str(windowYZ)

        QMessageBox.information(None,"展示信息",info, QMessageBox.Ok)

    def closeEvent(self,QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageScrollContainer.closeEvent(QCloseEvent)
        self.imageShownContainer.closeEvent(QCloseEvent)


