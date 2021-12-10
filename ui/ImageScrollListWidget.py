from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QDrag

from PIL.ImageQt import *
from ui.config import uiConfig
from ui.ImageScrollItemDelegate import ImageScrollItemDelegate
from utils.util import dicom_to_qt,getSeriesPathFromFileName,getSeriesImageCountFromSeriesPath
from utils.ImageItemMimeData import ImageItemMimeData

class ImageScrollListWidget(QListWidget):

    def __init__(self):
        QListWidget.__init__(self)

        self.setObjectName("ImageScrollListWidget")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setFixedHeight(uiConfig.listHeight)
        self.setDragEnabled(True)
        self.setUniformItemSizes(True)
        self.setSpacing(uiConfig.itemSpace)
        self.setResizeMode(QListWidget.Adjust)
        self.setItemDelegate(ImageScrollItemDelegate(self))

    def showImageList(self, dict):
        for seriesName,imageFileName in dict.items():
            self.addImageItem(imageFileName, seriesName)

    def addImageItem(self, fileName, text):
        qim = dicom_to_qt(fileName,uiConfig.factor_contrast,
                          uiConfig.factor_bright, uiConfig.autocontrast_mode,uiConfig.inversion_mode)
        pix = QPixmap.fromImage(qim)
        pixmap_resized = pix.scaled(uiConfig.iconSize, Qt.KeepAspectRatio)
        imageIcon = QIcon()
        imageIcon.addPixmap(pixmap_resized)
        imageItem = QListWidgetItem()
        imageItem.setIcon(imageIcon)
        imageItem.setText(text)
        imageItem.setSizeHint(uiConfig.itemHintSize)
        seriesPath = getSeriesPathFromFileName(fileName)
        seriesImageCount = getSeriesImageCountFromSeriesPath(seriesPath)
        itemExtraData = {
            "seriesPath": seriesPath,
            "seriesImageCount": seriesImageCount
        }
        imageItem.setData(3,itemExtraData)
        self.addItem(imageItem)

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