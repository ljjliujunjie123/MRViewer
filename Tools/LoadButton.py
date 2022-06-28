import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from enum import Enum
from Model.ImagesDataModel import imageDataModel
from Config import uiConfig
class Status(Enum):
    good = 1
    bad = 0 

class LoadButton(QFrame, ToolsInterface):
    def __init__(self, parent):
        super().__init__(parent)
        imgPath = r"./slide_show.png"
        self.loadBtn = QPushButton("Load Scan")
        self.loadBtn.setMinimumSize(100,40)
        self.loadBtn.setEnabled(True)
        self.loadBtn.clicked.connect(lambda x:self.openStudyDirectory())

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.loadBtn)

        self.setLayout(layout)
        self.setEnabled(True)

    def openStudyDirectory(self):
        filePath = QFileDialog.getExistingDirectory(None, "选择一个Study的目录",'')
        if checkDirValidity(filePath) is Status.bad: 
            return
        rootPath,studyName = os.path.split(filePath)[0], os.path.split(filePath)[-1]
        imageDataModel.clearDataBase()
        imageDataModel.setRootPath(rootPath)
        imageDataModel.addStudyItem(studyName)

def checkDirValidity(filePath):
    #非文件夹检查
    if not os.path.isdir(filePath):
        print("Warning:", filePath, "should be a directory not a file!")
        return Status.bad
    subPaths = os.listdir(filePath)
    #空检查
    if len(subPaths) is 0:
        print("Warning:", filePath, "is a empty directory!")
        return Status.bad
    return Status.good
