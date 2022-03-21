from PyQt5.QtCore import *
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.SingleImageShownContainer import SingleImageShownContainer
from utils.status import Status

class ImageShownBaseController(QObject):
    """
    该类负责处理渲染区的简单的控制逻辑
    """
    selectImageShownContainerSignal = pyqtSignal(SingleImageShownContainer,bool)
    initToolsContainerStateSignal = pyqtSignal()
    updateToolsContainerStateSignal = pyqtSignal(int)

    def __init__(self, imageShownContainerLayout: CustomDecoratedLayout):
        QObject.__init__(self)
        self.imageShownContainerLayout = imageShownContainerLayout
        self.selectedImageShownContainer = None
        self.selectImageShownContainerSignal.connect(self.selectImageShownContainerHandler)

    def setContainerSignals(self, container):
        container.signalCollectionHelper.setSelectImageShownContainerSignal(
                self.selectImageShownContainerSignal
        )

    #选中SC
    def selectImageShownContainerHandler(self, container, isSelected):
        if self.selectedImageShownContainer is not None:
            if self.selectedImageShownContainer is not container:
                self.selectedImageShownContainer.resetSelectState()
                self.selectedImageShownContainer = container
        else:
            self.selectedImageShownContainer = container

        if isSelected:
            self.initToolsContainerStateSignal.emit()
        else:
            self.updateToolsContainerStateSignal.emit(container.curMode)

    #SC模式切换
    def imageModeSelectHandler(self, mode):
        if self.selectedImageShownContainer.curMode ==  mode: return
        self.selectedImageShownContainer.switchImageContainerMode(mode)
        self.updateToolsContainerStateSignal.emit(self.selectedImageShownContainer.curMode)

    #SC的imageExtraInfo开关
    def imageExtraInfoStateHandler(self, isShow):
        self.selectedImageShownContainer.controlImageExtraInfoState(isShow)

    def clearViews(self):
        self.selectedImageShownContainer = None
        self.imageShownContainerLayout.mapWidgetsFunc(lambda container,*args:container.close(),None)
        self.imageShownContainerLayout.clearLayout()
        self.imageShownWidgetPool.clear()
        self.initWidget()