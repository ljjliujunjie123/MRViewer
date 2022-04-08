from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QDrag

import pydicom as pyd
from ui.config import uiConfig
from ui.ImageScrollItemDelegate import ImageScrollItemDelegate
from utils.util import createDicomPixmap,checkMultiFrame
from utils.ImageItemMimeData import ImageItemMimeData
from Model.ImagesDataModel import imageDataModel

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

    def showImageList(self):
        rows = imageDataModel.findDefaultStudy()
        for row in rows:
            studyName = row[0]
            seriesName = row[1]
            isMultiFrame = row[2]
            seriesImageCount = row[3]
            dcmFile = pyd.dcmread(row[4])

            imageIcon = QIcon()
            imageIcon.addPixmap(createDicomPixmap(dcmFile))

            imageItem = QListWidgetItem()
            imageItem.setIcon(imageIcon)
            imageItem.setText(seriesName)
            imageItem.setSizeHint(uiConfig.itemHintSize)

            itemExtraData = {
                "studyName": studyName,
                "seriesName": seriesName,
                "seriesImageCount": seriesImageCount,
                "isMultiFrame": isMultiFrame
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