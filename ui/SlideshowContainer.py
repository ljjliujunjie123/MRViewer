from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from ui.CustomDecoratedLayout import CustomDecoratedLayout

from ui.config import uiConfig

# Thanks to https://blog.csdn.net/gumenghua_com1/article/details/111318926
# https://www.cnblogs.com/ygzhaof/p/10064851.html

class SlideshowContainer(QDialog):

    playPauseSignal = pyqtSignal(bool)
    prevSignal = pyqtSignal(int)
    nextSignal = pyqtSignal(int)
    fastSignal = pyqtSignal(int)
    slowSignal = pyqtSignal(int)

    def __init__(self,
    ):
        QDialog.__init__(self)

        print("SlideshowContainer Geometry:")
        print(self.geometry())
        self.setObjectName("slideshowContainer")
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)#隐藏标题栏|在主窗口前
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("SlideShow")
        self.setFixedSize(uiConfig.shownSlideShowDialogSize)
        self.setGeometry(500, 500, self.width(), self.height())

        self.isPlayOrPause = False #False -> pause, True -> play
        self.mainLayout = CustomDecoratedLayout(QGridLayout())
        self.playLayout = CustomDecoratedLayout(QHBoxLayout())
        self.speedMainLayout = CustomDecoratedLayout(QGridLayout())
        self.speedFPSLayout = CustomDecoratedLayout(QVBoxLayout())
        self.speedLayout = CustomDecoratedLayout(QVBoxLayout())

        self.prevSliceButton = QPushButton()
        self.playButton = QPushButton()
        self.nextSliceButton = QPushButton()

        self.speedFastButton = QPushButton()
        self.speedSlowButton = QPushButton()
        self.fpsLogoLabel = QLabel()
        self.fpsValueLable = QLabel()

        self.initUISources()
        self.initUILayouts()
        self.initSignals()

        self.setLayout(self.mainLayout.getLayout())
        self.show()

    def initUISources(self):
        self.prevSliceButton.setIcon(QIcon("ui_source/previousFrame.png"))
        self.nextSliceButton.setIcon(QIcon("ui_source/nextFrame.png"))
        self.setPlayButtonIcon()
        self.speedFastButton.setIcon(QIcon("ui_source/Up.png"))
        self.speedSlowButton.setIcon(QIcon("ui_source/Down.png"))

        playButtonList = [self.prevSliceButton, self.nextSliceButton, self.playButton]
        fpsButtonList = [self.speedFastButton, self.speedSlowButton]

        for button in playButtonList:
            button.setIconSize(uiConfig.shownSlideShowPlayIconSize)

        for button in fpsButtonList:
            button.setIconSize(uiConfig.shownSlideShownSpeedIconSize)

        for button in playButtonList + fpsButtonList:
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setFlat(True)
            button.setStyleSheet("QPushButton{background-color:transparent;border-radius: none;}\
                                QPushButton:hover{background-color:white; color: rgb(255,0,0);}")

        self.fpsLogoLabel.setText("FPS")
        self.fpsValueLable.setText(str(uiConfig.shownSlideSpeedDefault))
        for label in [self.fpsLogoLabel, self.fpsValueLable]:
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def initUILayouts(self):
        self.mainLayout.initParamsForPlain()
        self.mainLayout.setAlignment(Qt.AlignCenter)

        self.playLayout.initParamsForPlain()
        self.playLayout.setMargins(5)
        self.playLayout.setSpacing(5)
        self.playLayout.setAlignment(Qt.AlignVCenter)

        self.speedFPSLayout.initParamsForPlain()
        self.speedFPSLayout.setSpacing(2)
        self.speedFPSLayout.setAlignment(Qt.AlignHCenter)

        self.speedLayout.initParamsForPlain()
        self.speedLayout.setSpacing(2)
        self.speedLayout.setAlignment(Qt.AlignHCenter)

        self.speedMainLayout.initParamsForPlain()
        self.speedMainLayout.setMargins(2)
        self.speedMainLayout.setSpacing(2)
        self.speedMainLayout.setAlignment(Qt.AlignCenter)

        self.playLayout.addItems([
            self.prevSliceButton, self.playButton, self.nextSliceButton
        ])
        self.speedFPSLayout.addItems([
            self.fpsLogoLabel, self.fpsValueLable
        ])
        self.speedLayout.addItems([
            self.speedFastButton, self.speedSlowButton
        ])
        self.speedMainLayout.addItems([self.speedFPSLayout], (0,0,1,1))
        self.speedMainLayout.addItems([self.speedLayout], (0,1,1,1))
        self.mainLayout.addItems([self.playLayout], (0,0,1,1))
        self.mainLayout.addItems([self.speedMainLayout], (0,1,1,1))

    def initSignals(self):
        self.playButton.clicked.connect(self.changePlayPauseState)
        self.prevSliceButton.clicked.connect(lambda :self.prevSignal.emit(-1))
        self.nextSliceButton.clicked.connect(lambda :self.nextSignal.emit(1))
        self.speedFastButton.clicked.connect(lambda :self.fastSignal.emit(1))
        self.speedSlowButton.clicked.connect(lambda :self.slowSignal.emit(-1))

    def changePlayPauseState(self):
        self.isPlayOrPause = not self.isPlayOrPause
        self.setPlayButtonIcon()
        self.playPauseSignal.emit(self.isPlayOrPause)

    def setPlayButtonIcon(self):
         if self.isPlayOrPause:
             self.playButton.setIcon(QIcon("ui_source/play.png"))
         else:
             self.playButton.setIcon(QIcon("ui_source/pause.png"))

    def setFPSLabelValue(self, text):
        self.fpsValueLable.setText(text)

    def getFPSLabelValue(self):
        return int(self.fpsValueLable.text())
    