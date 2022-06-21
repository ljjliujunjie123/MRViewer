from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QMouseEvent, QIcon

    
class DisplayArea(QFrame):
    def __init__(self, parent):
        self.parent = parent

