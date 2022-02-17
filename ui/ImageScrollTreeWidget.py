from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon,QDrag

from ui.config import uiConfig
from ui.ImageScrollItemDelegate import ImageScrollItemDelegate
from utils.util import createDicomPixmap,checkMultiFrame
from utils.ImageItemMimeData import ImageItemMimeData
from Model.ImagesDataModel import imageDataModel

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
        self.setIndentation(0)
        #这里后续要做一波美化
        # self.setStyleSheet("QTreeWidget::item{height:350px;}")

    def showImageList(self):
        self.roots = []
        for studyName in imageDataModel.dataSets.cache_names():
            studyDict = imageDataModel.findStudyItem(studyName)
            root = QTreeWidgetItem(self)
            root.setText(0,studyName)
            for seriesName, seriesDict in studyDict.items():
                child = QTreeWidgetItem(root)
                child.setText(0, seriesName)

                dcmFile = list(seriesDict.values())[0]
                imageIcon = QIcon()
                imageIcon.addPixmap(createDicomPixmap(dcmFile))

                child.setIcon(0, imageIcon)
                seriesImageCount = len(seriesDict)
                itemExtraData = {
                    "studyName": studyName,
                    "seriesName": seriesName,
                    "seriesImageCount": seriesImageCount,
                    "isMultiFrame": checkMultiFrame(seriesDict)
                }
                child.setData(0,3,itemExtraData)
            self.roots.append(root)
        self.addTopLevelItems(self.roots)
        self.expandItem(self.roots[0])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPoint = event.pos()
            item = self.itemAt(self.dragPoint)
            if item == None: return
            item.setSelected(True)
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
