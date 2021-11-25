from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ImageShownLayoutController():

    def __init__(
            self,
            imageShownContainerWidget,
            imageShownContainerLayout
    ):
        self.imageShownContainerWidget = imageShownContainerWidget
        self.imageShownContainerLayout = imageShownContainerLayout

    def initLayoutParams(self, uiConfig):
        self.imageShownContainerLayout.setContentsMargins(uiConfig.shownContainerMargins)
        self.imageShownContainerLayout.setSpacing(uiConfig.shownContainerContentSpace)
        self.imageShownContainerLayout.setObjectName("imageGridShownContainer")

    def addWidget(self, childWidget, row, col):
        self.imageShownContainerLayout.addWidget(childWidget, row, col, 1, 1)

