from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from controller.OpenFileController import OpenFileController
from ui.config import uiConfig
from ui.ImagesScrollContainer import ImageScrollContainer
from ui.ToolsContainer import ToolsContainer
from ui.ImageShownContainer import ImageShownContainer
from utils.status import Status

class LJJMainWindow(QMainWindow):

    updateImageShownSignal = pyqtSignal(str,str)
    updateImageListSignal = pyqtSignal(dict,int)
    updateImage3DShownSignal = pyqtSignal(str)
    enableImageSlideshow = pyqtSignal(bool) #图像走马灯开关

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setObjectName("MainWindow")
        self.resize(uiConfig.screenWidth, uiConfig.screenHeight)
        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(uiConfig.calcCenterWidgetGeometry())
        self.centralwidget.setObjectName("centralwidget")

        self.mainWindowWidget = QWidget(self.centralwidget)
        self.mainWindowWidget.setGeometry(self.centralwidget.geometry())
        self.mainWindowWidget.setObjectName("mainWindowWidget")

        self.mainWindowLayout = QHBoxLayout(self.mainWindowWidget)
        self.mainWindowLayout.setContentsMargins(0,0,0,0)
        self.mainWindowLayout.setSpacing(0)
        self.mainWindowLayout.setObjectName("mainWindowLayout")

        print("MainWindow CentralWidget Geometry：")
        print(self.centralwidget.geometry())

        #抽象出左侧的image列表
        self.imageScrollContainer = ImageScrollContainer(self.mainWindowWidget)
        #抽象出中间的image展示区域
        self.imageShownContainer = ImageShownContainer(self.mainWindowWidget)
        #抽象出右侧的工具栏
        self.toolsContainer = ToolsContainer(self.mainWindowWidget)

        #添加splitter
        self.splitter =  QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.imageScrollContainer)
        self.splitter.addWidget(self.imageShownContainer)
        self.splitter.addWidget(self.toolsContainer)

        #收敛子组件
        self.mainWindowLayout.addWidget(self.splitter)

        # print(self.geometry())
        # print(self.mainWindowWidget.geometry())
        # print(self.imageScrollContainer.geometry())
        # print(self.imageShownContainer.geometry())
        # print(self.toolsContainer.geometry())

        #菜单栏部分
        self.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(QRect(0, 0, uiConfig.screenWidth, uiConfig.menuHeight))
        self.menuBar.setObjectName("menubar")
        self.menu = QMenu(self.menuBar)
        self.menu.setObjectName("menu")
        self.setMenuBar(self.menuBar)

        #标题栏部分
        # self.titleBar = QStyleOptionTitleBar()
        # self.titleBar.initFrom()

        self.actionopen_study = QAction(self)
        self.actionopen_study.setObjectName("actionopen_study")
        self.actionopen_patient = QAction(self)
        self.actionopen_patient.setObjectName("actionopen_patient")

        self.menu.addAction(self.actionopen_study)
        self.menu.addAction(self.actionopen_patient)
        self.menuBar.addAction(self.menu.menuAction())

        #跟踪鼠标
        self.setMouseTracking(True)
        self.centralwidget.setMouseTracking(True)
        self.imageShownContainer.setMouseTracking(True)
        self.toolsContainer.setMouseTracking(True)

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
        # self.toolsContainer.showInfoSig.connect(self.showImageShownLayoutInfo)
        self.toolsContainer.updateImageShownLayoutSignal.connect(
            self.imageShownContainer.imageShownLayoutController.updateLayout
        )
        self.toolsContainer.enableImageSlideshowSignal.connect(
            self.imageShownContainer.imageShownLayoutController.imageSlideshowControl
        ) #evermg42
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
        if tag is uiConfig.studyTag:
            status = self.imageScrollContainer.updateListHeight(len(dict.keys()))
            if status is Status.bad: return

        if tag is uiConfig.patientTag:
            count = sum([len(study.keys()) for study in list(dict.values())])
            status = self.imageScrollContainer.updateListHeight(count)
            if status is Status.bad: return

        self.imageScrollContainer.clearImageList()
        self.imageScrollContainer.showImageList(dict, tag)

    def closeEvent(self,QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageScrollContainer.closeEvent(QCloseEvent)
        self.imageShownContainer.closeEvent(QCloseEvent)


