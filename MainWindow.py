from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QMoveEvent
from Config import uiConfig
from TitleBar import TitleBar
from ControlArea import ControlArea
from DisplayArea import DisplayArea
from ui.ImageScrollListWidget import ImageScrollListWidget
# from ui.displayArea.preImageDisplayer import ImageShownContainer
from Config import uiConfig

class MainWindow(QMainWindow):

    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.InitializeWindow()

        # 信号部分
        self.controlArea.toolsContainer.loadSignal.connect(self.displayArea.dataBaseDisplayer.ReadNewDirectory)
        self.controlArea.toolsContainer.loadSignal.connect(self.displayArea.ShiftToDatabase)
        self.displayArea.dataBaseDisplayer.selectFileSignal.connect(self.imageScrollContainer.showImageList)
        self.controlArea.modeSignal.connect(self.displayArea.setCurrentMode)

        
        #旧信号绑定部分
        # self.updateImageListSignal.connect(self.updateImageListArea)
        # self.tryClearImageShownSignal.connect(self.tryClearImageShownHandler)
        # self.actionopen_study.triggered.connect(self.openFileController.openStudyDirectory)
        # self.controlArea.extraToolsContainer.showInfoSig.connect(self.showImageShownLayoutInfo)
        self.displayArea.preImageDisplayer.imageShownBaseController.initToolsContainerStateSignal.connect(
            self.controlArea.extraToolsContainer.initToolsContainerStateHandler
        )
        self.displayArea.preImageDisplayer.imageShownBaseController.updateToolsContainerStateSignal.connect(
            self.controlArea.extraToolsContainer.updateToolsContainerStateHandler
        )
        self.controlArea.extraToolsContainer.updateImageShownLayoutSignal.connect(
            self.displayArea.preImageDisplayer.imageShownLayoutController.updateLayout
        )
        self.controlArea.extraToolsContainer.enableImageSlideshowSignal.connect(
            self.displayArea.preImageDisplayer.imageSlideShowController.imageSlideshowHandler
        ) #evermg42
        self.controlArea.extraToolsContainer.imageModeSelectSignal.connect(
            self.displayArea.preImageDisplayer.imageShownBaseController.imageModeSelectHandler
        )
        self.controlArea.extraToolsContainer.enableImageExtraInfoSignal.connect(
            self.displayArea.preImageDisplayer.imageShownBaseController.imageExtraInfoStateHandler
        )


    def InitializeWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(uiConfig.screenWidth, uiConfig.screenHeight)
        
        self.InitializeTitleBar()
        self.InitializeMouse()
        self.InitializeContent()

    def InitializeTitleBar(self):
        # dock
        self.title_menu_dock = QDockWidget()
        self.title_menu_dock.setContentsMargins(0,0,0,0)
        self.title_menu_dock.setAllowedAreas(Qt.TopDockWidgetArea)
        self.title_menu_dock.setFixedHeight(50)
        self.title_menu_dock.setTitleBarWidget(QWidget()) 
        self.addDockWidget(Qt.TopDockWidgetArea, self.title_menu_dock)
        # Titlebar
        self.titleBar = TitleBar(self)
        self.bars = QWidget()
        layout = QVBoxLayout()
        self.bars.setLayout(layout)
        layout.addWidget(self.titleBar)
        layout.setStretch(1, 1280)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.title_menu_dock.setWidget(self.bars)

    def InitializeContent(self):
        centralWidget = QSplitter(self)
        displayDivider = QSplitter(self)
        displayDivider.setOrientation(Qt.Vertical)
        self.controlArea = ControlArea(centralWidget)
        self.displayArea = DisplayArea(centralWidget)
        self.imageScrollContainer=ImageScrollListWidget(centralWidget)
        # self.setCentralWidget(centralWidget)

        displayDivider.addWidget(self.displayArea)
        displayDivider.addWidget(self.imageScrollContainer)
        centralWidget.setOrientation(Qt.Horizontal)
        centralWidget.addWidget(self.controlArea)
        centralWidget.addWidget(displayDivider)
        # centralWidget.addWidget(self.displayArea)
        # centralWidget.addWidget(self.imageScrollContainer)
        centralWidget.setStretchFactor(0,1)
        centralWidget.setStretchFactor(1,3)
        self.setCentralWidget(centralWidget)

    def InitializeMouse(self):
        self.setMouseTracking(True) # 跟踪鼠标开启
        self._move_drag = False

    def resizeEvent(self, *args, **kwargs):
        print("mainWindow geometry", self.geometry())
