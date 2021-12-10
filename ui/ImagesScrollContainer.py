from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.config import uiConfig
from ui.ImageScrollListWidget import ImageScrollListWidget
from ui.ImageScrollTreeWidget import ImageScrollTreeWidget
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from utils.status import Status

class ImageScrollContainer(QFrame):

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(uiConfig.calcScrollContainerGeometry())
        print("ImageScrollContainer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageScrollContainer")
        self.imageVerticalScrollWidget = None
        self.imageVerticalScrollLayout = CustomDecoratedLayout(QVBoxLayout())
        self.imageVerticalScrollLayout.initParamsForPlain()
        self.setLayout(self.imageVerticalScrollLayout.getLayout())

    def updateListHeight(self, itemCount):
        listHeight = (uiConfig.iconSize.height() + uiConfig.itemSpace * 2) * itemCount
        if listHeight > 1e5:
            QMessageBox.information(None,"警告","选择的文件过多！请重新选择",QMessageBox.Ok)
            return Status.bad
        # self.imageVerticalScrollWidget.setFixedHeight(listHeight)
        return Status.good

    def initImageListView(self, tag):
        if tag is uiConfig.studyTag:
            self.imageVerticalScrollWidget = ImageScrollListWidget()
        if tag is uiConfig.patientTag:
            self.imageVerticalScrollWidget = ImageScrollTreeWidget()
        self.imageVerticalScrollLayout.clearLayout()
        self.imageVerticalScrollWidget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.imageVerticalScrollWidget.setFixedHeight(self.height())
        self.imageVerticalScrollLayout.getLayout().addWidget(self.imageVerticalScrollWidget)
        self.imageVerticalScrollWidget.show()

    def clearImageList(self):
        # 注意删除item时要先清除其所有的connect信号
        self.imageVerticalScrollWidget.clear()

    def showImageList(self, dict, tag):
        self.imageVerticalScrollWidget.showImageList(dict)

    def resizeEvent(self, *args, **kwargs):
        if self.imageVerticalScrollWidget is not None:
            self.imageVerticalScrollWidget.setFixedHeight(self.height())
