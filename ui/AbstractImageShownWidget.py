from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class AbstractImageShownWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            print("enter")
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            print("drop")
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()