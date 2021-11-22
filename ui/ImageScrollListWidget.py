from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QDrag

from PIL.ImageQt import *
from ui.config import *
from utils.util import dicom_to_qt,getSeriesPathFromFileName
from utils.ImageItemMimeData import ImageItemMimeData

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
        itemExtraData = {
            "seriesPath":getSeriesPathFromFileName(fileName)
        }
        imageItem.setData(3,itemExtraData)
        self.addItem(imageItem)
        print(fileName)
        print(self.iconSize())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPoint = event.pos()
            self.dragItem = self.itemAt(self.dragPoint)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragItem is not None:
            dragDistance = event.pos() - self.dragPoint
            if dragDistance.manhattanLength() > QApplication.startDragDistance():
                drag = QDrag(self)
                mimeData = ImageItemMimeData()
                mimeData.setImageExtraData(self.dragItem.data(3))
                mimeData.setText(self.dragItem.text())
                drag.setMimeData(mimeData)
                action = drag.exec(Qt.CopyAction)
                if action == Qt.CopyAction:
                    self.dragPoint = None
                    self.dragItem = None
        super().mouseMoveEvent(event)