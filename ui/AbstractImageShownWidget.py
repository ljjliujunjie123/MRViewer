from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class AbstractImageShownWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setAcceptDrops(True)
        self.qvtkWidget = None

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

    def resizeEvent(self, QResizeEvent):
        print("resizeEvent")
        print('parentWidgetSize:', self.width(), self.height())
        if self.qvtkWidget is not None and self.qvtkWidget.size() != self.size():
            self.qvtkWidget.setFixedSize(self.size())
            print('qvtkSize', self.qvtkWidget.size())

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.qvtkWidget is not None: self.qvtkWidget.Finalize()