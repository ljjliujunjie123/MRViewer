from PyQt5.QtWidgets import *

import os

from ui.config import uiConfig
from Model.ImagesDataModel import imageDataModel
from utils.status import Status

class OpenFileController():

    def __init__(
            self,
            mainWindow,
            imageScrollContainer,
            updateImageListSignal,
            tryClearImageShownSignal
    ):
        self.mainWindow = mainWindow
        self.imageScrollContainer = imageScrollContainer
        self.updateImageListSignal = updateImageListSignal
        self.tryClearImageShownSignal = tryClearImageShownSignal

    def openStudyDirectory(self):
        """
            读取study中的所有dicom文件
        """
        # filePath = QFileDialog.getExistingDirectory(self.mainWindow, "选择一个Study的目录",'')
        # filePath = r"D:\respository\MRViewer_Scource\study_Test_data"
        # filePath = r"E:\research\MRViewer_test\try"
        filePath = r'E:\research\MRViewer_test\study_Test_data'
        rootPath,studyName = os.path.split(filePath)[0], os.path.split(filePath)[-1]
        imageDataModel.clearDataBase()
        self.tryClearImageShownSignal.emit()
        imageDataModel.setRootPath(rootPath)
        imageDataModel.addStudyItem(studyName)

        self.updateImageListSignal.emit(uiConfig.studyTag)

    def openPatientDirectory(self):
        filePath = QFileDialog.getExistingDirectory(self.mainWindow, "选择一个Patient的目录",'')
        # filePath = r"D:\respository\MRViewer_Scource\Patient_Test_data"
        imageDataModel.clearDataBase()
        self.tryClearImageShownSignal.emit()
        imageDataModel.setRootPath(filePath)
        studyNames = os.listdir(filePath)
        for studyName in studyNames:
            studyPath = os.path.join(filePath, studyName)
            imageDataModel.addStudyItem(studyName)

        self.updateImageListSignal.emit(uiConfig.patientTag)