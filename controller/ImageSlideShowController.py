from PyQt5.QtCore import *
from ui.CustomDecoratedLayout import CustomDecoratedLayout

class ImageSlideShowController(QObject):
    """
    该类负责处理渲染区的轮播事件
    """

    def __init__(self, imageShownContainerLayout: CustomDecoratedLayout):
        QObject.__init__(self)
        self.imageShownContainerLayout = imageShownContainerLayout

    def imageSlideshowHandler(self, enable):
        pass
