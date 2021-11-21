from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from PIL.ImageQt import *
from ui.config import *
from utils.util import dicom_to_qt

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
        self.setIconSize(iconSize)
        self.setDragEnabled(True)

    def showImageList(self, dict):

        self.roots = []

        for studyName,studyValue in dict.items():
            root = QTreeWidgetItem(self)
            root.setText(0,studyName)
            for seriesName,seriesValue in studyValue.items():
                child = QTreeWidgetItem(root)
                child.setText(0,seriesName)
                child.setIcon(0,self.getImageIcon(seriesValue))
            self.roots.append(root)

        self.addTopLevelItems(self.roots)
        self.expandItem(self.roots[0])

    def getImageIcon(self, fileName):
        qim = dicom_to_qt(fileName, factor_contrast,
                          factor_bright, autocontrast_mode, inversion_mode)
        pix = QPixmap.fromImage(qim)
        pixmap_resized = pix.scaled(iconSize, Qt.KeepAspectRatio)
        imageIcon = QIcon()
        imageIcon.addPixmap(pixmap_resized)
        return imageIcon
