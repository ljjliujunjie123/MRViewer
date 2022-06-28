from PyQt5.QtCore import *
import copy

class ImageItemMimeData(QMimeData):

    def __init__(self):
        QMimeData.__init__(self)
        self.dict = {}

    def setImageExtraData(self, dict):
        self.dict = copy.deepcopy(dict)

    def addImageExtraDataItem(self, key, value):
        self.dict[key] = value

    def getImageExtraData(self):
        return self.dict