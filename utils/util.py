import numpy as np
import pydicom as pyd
import os
from PIL.ImageQt import *
from utils.status import Status
from ui.config import uiConfig
from PyQt5.QtCore import *

def createDicomPixmap(dcmFile):
    image_2d = dcmFile.pixel_array.astype(float)
    image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
    image_2d_scaled = np.uint8(image_2d_scaled)
    image = Image.fromarray(image_2d_scaled)
    dcmImage = ImageQt(image)
    pix = QPixmap.fromImage(dcmImage)
    pixmap_resized = pix.scaled(uiConfig.iconSize, Qt.KeepAspectRatio)
    return pixmap_resized

def getSeriesPathFromFileName(fileName):
    return os.path.split(fileName)[0]

def getSeriesImageCountFromSeriesPath(seriesPath):
    return len(os.listdir(seriesPath))

def checkSameStudy(f1,f2):
    df1 = pyd.dcmread(f1)
    df2 = pyd.dcmread(f2)
    return (df1["PatientName"] == df2["PatientName"]) and (df1["StudyDescription"] == df2["StudyDescription"])

def checkSameSeries(f1,f2):
    df1 = pyd.dcmread(f1)
    df2 = pyd.dcmread(f2)
    return df1["SeriesDescription"] == df2["SeriesDescription"]

def checkDirValidity(filePath):
    #非文件夹检查
    if not os.path.isdir(filePath):
        # QMessageBox.information(None,"提示","请选择文件夹而非文件",QMessageBox.Ok)
        print("Warning:", filePath, "should be a directory not a file!")
        return Status.bad
    subPaths = os.listdir(filePath)
    #空检查
    if len(subPaths) is 0:
        # QMessageBox.information(None,"提示","有空文件夹！",QMessageBox.Ok)
        print("Warning:", filePath, "is a empty directory!")
        return Status.bad
    return Status.good