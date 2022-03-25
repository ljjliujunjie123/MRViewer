from PyQt5.QtCore import *
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.SingleImageShownContainer import SingleImageShownContainer

class ImageSlideShowController(QObject):
    """
    该类负责处理渲染区的轮播事件
    """

    def __init__(self, imageShownContainerLayout: CustomDecoratedLayout):
        QObject.__init__(self)
        self.imageShownContainerLayout = imageShownContainerLayout

    def imageSlideshowHandler(self, enable):
        self.imageShownContainerLayout.mapWidgetsFunc(self.imageSlideshowSCHandler)

    def imageSlideshowSCHandler(self, handleContainer: SingleImageShownContainer):
        def checkSelectContainerCanSlideShow(container: SingleImageShownContainer):
            if  container is None or\
                not container.isSelected or\
                container.curMode is not SingleImageShownContainer.m2DMode or\
                container.mImageShownWidget is None: return False
            else: return True

        if not checkSelectContainerCanSlideShow(handleContainer): return
        if handleContainer.mImageShownWidget.imageSlideShow is None:
            handleContainer.showSlideShowContainer()
        else:
            handleContainer.closeSlideShowContainer()