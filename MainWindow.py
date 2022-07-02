from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QMoveEvent
from Config import uiConfig
from TitleBar import TitleBar
from ControlArea import ControlArea
from DisplayArea import DisplayArea
from Config import uiConfig

class MainWindow(QMainWindow):

    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.InitializeWindow()

        # 信号部分
        self.controlArea.toolsContainer.loadSignal.connect(self.displayArea.dataBaseDisplayer.imageDataModel.readFromStudyDirectory)
        self.controlArea.toolsContainer.loadSignal.connect(self.displayArea.ShiftToDatabase)

    def InitializeWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(uiConfig.screenWidth, uiConfig.screenHeight)
        
        self.InitializeTitleBar()
        self.InitializeMouse()
        self.InitializeContent()

    def InitializeTitleBar(self):
        # dock
        self.title_menu_dock = QDockWidget()
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
        centralWidget = QWidget(self)
        layout = QHBoxLayout()
        self.controlArea = ControlArea(centralWidget)
        self.displayArea = DisplayArea(centralWidget)
        layout.addWidget(self.controlArea)
        layout.addWidget(self.displayArea)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStretchFactor(self.controlArea,1)
        layout.setStretchFactor(self.displayArea,3)
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(layout)
        centralWidget.setStyleSheet('border:1px solid black')
        centralWidget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        

    def InitializeMouse(self):
        self.setMouseTracking(True) # 跟踪鼠标开启
        self._move_drag = False

    def resizeEvent(self, *args, **kwargs):
        print("mainWindow geometry", self.geometry())

    # def moveEvent(self, *args, **kwargs):
        # print("moving MainWindow")

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton):# and self.titleBar.geometry().contains(event.pos()):# 鼠标左键点击标题栏区
            
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        self.setCursor(Qt.ArrowCursor)
        if QMouseEvent.buttons() == Qt.LeftButton:
            # 拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            moveEvent = QMoveEvent(QMouseEvent.globalPos(), self.move_DragPosition)
            # print(moveEvent.pos(), moveEvent.oldPos())
            QMouseEvent.accept()