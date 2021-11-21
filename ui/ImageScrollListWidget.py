from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from PIL.ImageQt import *
from ui.config import *
from utils.util import dicom_to_qt

class ImageScrollListWidget(QListWidget):

    def __init__(self):
        QListWidget.__init__(self)

        self.setObjectName("ImageScrollListWidget")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setFixedHeight(listHeight)
        self.setIconSize(iconSize)
        self.setDragEnabled(True)
        self.setUniformItemSizes(True)
        self.setSpacing(itemSpace)

    def showImageList(self, dict):
        for seriesName,imageFileName in dict.items():
            self.addImageItem(imageFileName, seriesName)

    def addImageItem(self, fileName, text):
        qim = dicom_to_qt(fileName, factor_contrast,
                          factor_bright, autocontrast_mode, inversion_mode)
        pix = QPixmap.fromImage(qim)
        pixmap_resized = pix.scaled(iconSize, Qt.KeepAspectRatio)
        imageIcon = QIcon()
        imageIcon.addPixmap(pixmap_resized)
        imageItem = QListWidgetItem()
        imageItem.setIcon(imageIcon)
        imageItem.setText(text)
        self.addItem(imageItem)
        print(fileName)
        print(self.iconSize())