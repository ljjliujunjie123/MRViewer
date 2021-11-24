from PyQt5.QtWidgets import *

import os

from ui.config import *
from utils.status import Status

class OpenFileController():

    def __init__(
            self,
            mainWindow,
            imageScrollContainer,
            updateImageListSignal
    ):
        self.mainWindow = mainWindow
        self.imageScrollContainer = imageScrollContainer
        self.updateImageListSignal = updateImageListSignal

    def openFileFolderWindow(self):
        fileNames = QFileDialog.getOpenFileNames(self,'选择文件','','')[0]
        print(fileNames)
        fileCount = len(fileNames)
        if fileCount < 1:
            QMessageBox.information(None,"提示","请至少选择一个文件",QMessageBox.Ok)
            return
        elif fileCount < 2:
            self.updateImageShownSignal.emit(fileNames[0],'')
        else:
            self.updateImageShownSignal.emit(fileNames[0],fileNames[1])

        self.updateImageListSignal.emit(fileNames)
        print("发射 fileFolder 信号")

    def openDirectoryWindow(self):
        filePath = QFileDialog.getExistingDirectory(self, "选择Dicom列表文件夹",'')
        #无效检查
        if not os.path.isdir(filePath):
            QMessageBox.information(None,"提示","请选择有效的文件夹",QMessageBox.Ok)
            return
        subFilePaths = os.listdir(filePath)
        #空检查
        if len(subFilePaths) is 0:
            QMessageBox.information(None,"提示","请选择有效的文件夹",QMessageBox.Ok)
            return
        #子目录检查
        for subFilePath in subFilePaths:
            if os.path.isdir(subFilePath):
                QMessageBox.information(None,"提示","请选择有效的文件夹",QMessageBox.Ok)
                return
        self.updateImage3DShownSignal.emit(filePath)

    def openStudyDirectory(self):
        filePath = QFileDialog.getExistingDirectory(self.mainWindow, "选择一个Study的目录",'')
        # filePath = r'D:/respository/MRViewer_Scource/dicom_for_UItest'
        if self.checkDirValidity(filePath) is Status.bad: return
        seriesPaths = os.listdir(filePath)
        dict = {}
        for _seriesPath in seriesPaths:
            seriesPath = filePath + '/' + _seriesPath
            if self.checkDirValidity(seriesPath) is Status.bad:continue
            fileNames = os.listdir(seriesPath)
            if len(fileNames) > 0:
                dict[_seriesPath] = seriesPath + '/' + fileNames[0]

        self.updateImageListSignal.emit(dict, studyTag)

    def openPatientDirectory(self):
        filePath = QFileDialog.getExistingDirectory(self.mainWindow, "选择一个Patient的目录",'')
        # filePath = r'D:/respository/MRViewer_Scource/Patient_Test_data'
        if self.checkDirValidity(filePath) is Status.bad: return

        resDict = {}

        studyPaths = os.listdir(filePath)
        for _studyPath in studyPaths:
            studyPath = filePath + '/' + _studyPath
            if self.checkDirValidity(studyPath) is Status.bad:continue
            #创建一个studyDict
            studyDict = {}
            seriesPaths = os.listdir(studyPath)
            for _seriesPath in seriesPaths:
                seriesPath = studyPath + '/' + _seriesPath
                if self.checkDirValidity(seriesPath) is Status.bad:continue
                fileNames = os.listdir(seriesPath)
                if len(fileNames) > 0:
                    #从series列表中取一个fileName作为value，key是seriesPath
                    studyDict[_seriesPath] = seriesPath + '/' + fileNames[0]
            #把studyDict加入resDict，key为_studyPath
            resDict[_studyPath] = studyDict

        self.updateImageListSignal.emit(resDict, patientTag)

    def checkDirValidity(self, filePath):
        #非文件夹检查
        if not os.path.isdir(filePath):
            QMessageBox.information(None,"提示","请选择文件夹而非文件",QMessageBox.Ok)
            return Status.bad
        subPaths = os.listdir(filePath)
        #空检查
        if len(subPaths) is 0:
            QMessageBox.information(None,"提示","有空文件夹！",QMessageBox.Ok)
            return Status.bad
        return Status.good