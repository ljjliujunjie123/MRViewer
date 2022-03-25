from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from ui.Tools.ToolsInterface import ToolsInterface
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.SingleImageShownContainer import SingleImageShownContainer


class ImageModeContainer(QFrame, ToolsInterface):

    iconPaths = {
        SingleImageShownContainer.m2DMode:"ui_source/2d_mode.png",
        SingleImageShownContainer.m3DMode:"ui_source/3d_mode.png",
        SingleImageShownContainer.m3DFakeMode:"ui_source/3d_fake_mode.png",
        SingleImageShownContainer.mRTMode:"ui_source/RT_mode.png"
    }

    def __init__(self, parent, signal):
        super().__init__(parent=parent)
        imageVBoxLayout =  CustomDecoratedLayout(QVBoxLayout())
        imageVBoxLayout.initParamsForPlain()
        bt2D = self.createImageModeButton(SingleImageShownContainer.m2DMode, signal)
        bt3D = self.createImageModeButton(SingleImageShownContainer.m3DMode, signal)
        bt3DFake = self.createImageModeButton(SingleImageShownContainer.m3DFakeMode, signal)
        btRT = self.createImageModeButton(SingleImageShownContainer.mRTMode, signal)
        imageVBoxLayout.addItems([bt2D,bt3D,bt3DFake,btRT])

        self.setLayout(imageVBoxLayout.getLayout())
        self.setEnabled(False)
    
    def initImageMode(self):
        self.setEnabled(True)
        
    def updateImageMode(self):
        self.setEnabled(False)

    def createImageModeButton(self, mode, signal):
        button = QPushButton()
        button.setIcon(QIcon(self.iconPaths[mode]))
        button.setIconSize(uiConfig.toolsIconSize)
        button.clicked.connect(lambda : signal.emit(mode))
        return button

    def init(self):
        self.setEnabled(True)

    def update(self):
        pass