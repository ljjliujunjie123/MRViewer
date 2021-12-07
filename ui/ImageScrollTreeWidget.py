from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QDrag

from PIL.ImageQt import *
from ui.config import uiConfig
from ui.ImageScrollItemDelegate import ImageScrollItemDelegate
from utils.util import dicom_to_qt,getSeriesPathFromFileName,getSeriesImageCountFromSeriesPath
from utils.ImageItemMimeData import ImageItemMimeData

class ImageScrollTreeWidget(QTreeWidget):

    def __init__(self):
        QTreeWidget.__init__(self)

        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(True)
        self.setAutoExpandDelay(-1)
        self.setItemsExpandable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setIconSize(uiConfig.iconSize)
        self.setDragEnabled(True)
        self.setItemDelegateForColumn(0, ImageScrollItemDelegate(self))

    def showImageList(self, dict):

        self.roots = []

        for studyName,studyValue in dict.items():
            root = QTreeWidgetItem(self)
            root.setText(0,studyName)
            for seriesName,seriesValue in studyValue.items():
                child = QTreeWidgetItem(root)
                child.setText(0,seriesName)
                child.setIcon(0,self.getImageIcon(seriesValue))
                seriesPath = getSeriesPathFromFileName(seriesValue)
                seriesImageCount = getSeriesImageCountFromSeriesPath(seriesPath)
                itemExtraData = {
                    "seriesPath": seriesPath,
                    "seriesImageCount": seriesImageCount
                }
                child.setData(0,3,itemExtraData)
            self.roots.append(root)

        self.addTopLevelItems(self.roots)
        self.expandItem(self.roots[0])

    def getImageIcon(self, fileName):
        qim = dicom_to_qt(fileName,uiConfig.factor_contrast,
                            uiConfig.factor_bright, uiConfig.autocontrast_mode, uiConfig.inversion_mode)
        pix = QPixmap.fromImage(qim)
        pixmap_resized = pix.scaled(uiConfig.iconSize, Qt.KeepAspectRatio)
        imageIcon = QIcon()
        imageIcon.addPixmap(pixmap_resized)
        return imageIcon

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
                mimeData.setImageExtraData(self.dragItem.data(0,3))
                mimeData.setText(self.dragItem.text(0))
                drag.setMimeData(mimeData)
                action = drag.exec(Qt.CopyAction)
                if action == Qt.CopyAction:
                    self.dragPoint = None
                    self.dragItem = None
        super().mouseMoveEvent(event)
