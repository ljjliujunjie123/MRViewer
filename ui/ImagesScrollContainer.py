from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

import numpy as np
import pydicom as pyd
from PIL import Image, ImageOps, ImageEnhance
from PIL.ImageQt import *

from utils.status import Status

class ImageScrollContainer(QFrame):

    factor_bright = 1
    factor_contrast = 1
    autocontrast_mode = 0
    inversion_mode = 0
    width_of = 450

    itemSpace = 10
    iconSize = QSize(400,400)
    listHeight = 1000


    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(QRect(0, 0, 600, 1000))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageScrollContainer")

        self.imageVerticalScrollLayout = QVBoxLayout()
        self.setLayout(self.imageVerticalScrollLayout)

        self.imageVerticalScrollContainer = QScrollArea()
        self.imageVerticalScrollLayout.addWidget(self.imageVerticalScrollContainer)

        self.imageVerticalScrollWidget = QListWidget()
        self.imageVerticalScrollWidget.setMinimumSize(self.width(),self.height())
        self.imageVerticalScrollWidget.setFixedHeight(self.listHeight)
        self.imageVerticalScrollWidget.setIconSize(self.iconSize)
        self.imageVerticalScrollWidget.setDragEnabled(True)
        self.imageVerticalScrollWidget.setUniformItemSizes(True)
        self.imageVerticalScrollWidget.setSpacing(self.itemSpace)
        self.imageVerticalScrollContainer.setWidget(self.imageVerticalScrollWidget)

        # self.addImageItem("E:/DCMTK/test10.dcm", 0)
        # self.addImageItem("E:/DCMTK/CT4.dcm",1)
        # self.addImageItem("E:/DCMTK/CT2.dcm",2)

    def addImageItem(self, fileName, index):
        qim = self.dicom_to_qt(fileName, self.factor_contrast,
                          self.factor_bright, self.autocontrast_mode, self.inversion_mode)
        pix = QPixmap.fromImage(qim)
        pixmap_resized = pix.scaled(self.width_of, 10000, Qt.KeepAspectRatio)

        self.imageIcon = QIcon()
        self.imageIcon.addPixmap(pixmap_resized)
        self.imageItem = QListWidgetItem()
        self.imageItem.setIcon(self.imageIcon)
        self.imageVerticalScrollWidget.addItem(self.imageItem)

        print(fileName)

    def extract_grayscale_image(self,mri_file):
        plan = pyd.read_file(mri_file)
        image_2d = plan.pixel_array.astype(float)
        image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
        image_2d_scaled = np.uint8(image_2d_scaled)
        return image_2d_scaled

    def dicom_to_qt(self,dcm_file, factor_contrast, factor_bright, auto_mode, inversion_mode):
        image = np.array(self.extract_grayscale_image(dcm_file))
        image = Image.fromarray(image)
        if auto_mode == 1:
            image = ImageOps.equalize(image, mask=None)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(factor_contrast)
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(factor_bright)
        if inversion_mode == 1:
            image = ImageOps.invert(image.convert('L'))
        qim = ImageQt(image)
        return (qim)

    def updateListHeight(self, itemCount):
        self.listHeight = (self.iconSize.height() + self.itemSpace * 2) * itemCount
        if self.listHeight > 1e5:
            QMessageBox.information(None,"警告","选择的文件过多！请重新选择",QMessageBox.Ok)
            return Status.bad
        self.imageVerticalScrollWidget.setFixedHeight(self.listHeight)
        return Status.good

    def clearImageList(self):
        # 注意删除item时要先清除其所有的connect信号
        for index in range(self.imageVerticalScrollWidget.count()):
            print("清除", index)
            item = self.imageVerticalScrollWidget.item(index)
            self.imageVerticalScrollWidget.takeItem(index)
            del item