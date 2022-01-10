from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from controller.OpenFileController import OpenFileController
from ui.config import uiConfig
from ui.ImagesScrollContainer import ImageScrollContainer
from ui.ToolsContainer import ToolsContainer
from ui.ImageShownContainer import ImageShownContainer
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from utils.status import Status

class LJJMainWindow(QMainWindow):

    updateImageShownSignal = pyqtSignal(str,str)
    updateImageListSignal = pyqtSignal(dict,int)
    updateImage3DShownSignal = pyqtSignal(str)
    enableImageSlideshow = pyqtSignal(bool) #图像走马灯开关

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        # self.setWindowFlags(Qt.FramelessWindowHint)

        self.setObjectName("MainWindow")
        self.resize(uiConfig.screenWidth, uiConfig.screenHeight)
        # self._move_drag = False
        # layout = QVBoxLayout(self)
        # layout
        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(uiConfig.calcCenterWidgetGeometry())
        self.centralwidget.setMinimumSize(uiConfig.centralWidgetMinSize)
        self.centralwidget.setStyleSheet("background-color:#A9A9A9;")
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        
        print("MainWindow CentralWidget Geometry:")
        print(self.centralwidget.geometry())

        #添加splitter
        self.splitter =  QSplitter(self.centralwidget)
        self.splitter.setGeometry(self.centralwidget.geometry())
        self.splitter.setOrientation(Qt.Horizontal)

        #抽象出左侧的image列表
        self.imageScrollContainer = ImageScrollContainer(self.splitter)
        #抽象出中间的image展示区域
        self.imageShownContainer = ImageShownContainer(self.splitter)
        #抽象出右侧的工具栏
        self.toolsContainer = ToolsContainer(self.splitter)

        self.splitter.addWidget(self.imageScrollContainer)
        self.splitter.addWidget(self.imageShownContainer)
        self.splitter.addWidget(self.toolsContainer)

        # print(self.geometry())
        # print(self.mainWindowWidget.geometry())
        # print(self.imageScrollContainer.geometry())
        # print(self.imageShownContainer.geometry())
        # print(self.toolsContainer.geometry())

        #菜单栏部分
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(QRect(0, 0, uiConfig.screenWidth, uiConfig.menuHeight))
        
        self.menuBar.setObjectName("menubar")
        self.setStyleSheet("background: #A9A9A9")
        self.fileOpener = QMenu(self.menuBar)
        self.fileOpener.setObjectName("fileOpener")
        self.setMenuBar(self.menuBar)

        #标题栏部分
        self.setWindowIcon(QIcon("ui_source/win_title_icon_color.png"))
        self.setWindowTitle("iRTMR V1")

        # #添加centralWidget的layout
        self.mainWinLayout = CustomDecoratedLayout(QVBoxLayout())
        self.mainWinLayout.initParamsForPlain()
        self.splitter.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setMinimumSize(100,0)
        # self.mainWinLayout.getLayout().addWidget(self.titleBar)
        self.mainWinLayout.getLayout().addWidget(self.splitter)
        self.centralwidget.setLayout(self.mainWinLayout.getLayout())

        self.actionopen_study = QAction(self)
        self.actionopen_study.setObjectName("actionopen_study")
        self.actionopen_patient = QAction(self)
        self.actionopen_patient.setObjectName("actionopen_patient")
        self.fileOpener.addAction(self.actionopen_study)
        self.fileOpener.addAction(self.actionopen_patient)
        self.menuBar.addAction(self.fileOpener.menuAction())

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
        self.imageShownContainer.imageShownLayoutController.updateToolsContainerStateSignal.connect(
            self.toolsContainer.updateToolsContainerStateHandler
        )
        self.toolsContainer.updateImageShownLayoutSignal.connect(
            self.imageShownContainer.imageShownLayoutController.updateLayout
        )
        self.toolsContainer.enableImageSlideshowSignal.connect(
            self.imageShownContainer.imageShownLayoutController.imageSlideshowControl
        ) #evermg42
        self.toolsContainer.imageModeSelectSignal.connect(
            self.imageShownContainer.imageShownLayoutController.imageModeSelectHandler
        )
        self.toolsContainer.enableImageExtraInfoSignal.connect(
            self.imageShownContainer.imageShownLayoutController.imageExtraInfoStateHandler
        )
        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

        self.show()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        self.fileOpener.setTitle(_translate("MainWindow", "文件"))
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

    def resizeEvent(self, *args, **kwargs):
        print("mainWindow geometry", self.geometry())
        print("centralWidget geometry", self.centralwidget.geometry())
        self.centralwidget.resize(self.width(),self.height() - self.menuBar.height())

    def moveEvent(self, *args, **kwargs):
        print("moving MainWindow")
        self.imageShownContainer.imageShownLayoutController.controlMoveEvent()

    def closeEvent(self,QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageScrollContainer.closeEvent(QCloseEvent)
        self.imageShownContainer.closeEvent(QCloseEvent)

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton):# and self.titleBar.geometry().contains(event.pos()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        self.setCursor(Qt.ArrowCursor)
        if Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()
