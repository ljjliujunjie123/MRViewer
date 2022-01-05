import numpy as np
import pydicom as pyd
import os
from PIL import ImageOps, ImageEnhance
from PIL.ImageQt import *
from enum import Enum


class Location(Enum):
    """顺序为左上、右上、左下、右下"""
    UL = 0 # up right
    UR = 1
    DL = 2 #down left
    DR = 3

normalKeyDict = {
    Location.UL:{
        "PatientName": "",
        "StudyDescription": "Study: ",
        "SeriesDescription": "Series: ",
    },
    Location.UR:{
        "InstanceNumber": "Index: "
    },
    Location.DL:{
        "RepetitionTime": "TR: ",
        "EchoTime": "TE: ",
    },
    Location.DR:{
        "SliceThickness": "Slice Thickness: "
    }
}

orientationList = [
    ("R","L"),
    ("A","P"),
    ("I","S")
]

def getDicomWindowCenterAndLevel(fileName):
    dcmFile = pyd.dcmread(fileName)
    return (dcmFile.WindowCenter, dcmFile.WindowWidth)

def getImageTileInfoFromDicom(fileName):
    dcmFile = pyd.dcmread(fileName)
    res = ""
    res += (normalKeyDict[Location.UL]["PatientName"] +  str(dcmFile["PatientName"].value))
    res += " - "
    res += (normalKeyDict[Location.UL]["SeriesDescription"] +  str(dcmFile["SeriesDescription"].value))
    return res

def getImageOrientationInfoFromDicom(fileName):
    """
        判断方向向量与标准轴的cos值，如果大于阈值，则增加一个标识
    """
    dcmFile = pyd.dcmread(fileName)
    ImageOrientation=np.array(dcmFile.ImageOrientationPatient,dtype = float)
    xVector,yVector = ImageOrientation[:3],ImageOrientation[3:]
    func = lambda x:round(x,1)
    xVector,yVector = tuple(map(func,xVector)),tuple(map(func,yVector))
    print("orientation vector ", xVector, yVector)
    xInfo = calcImageOrientation(xVector)
    yInfo = calcImageOrientation(yVector)

    print(xInfo,yInfo)
    return tuple(xInfo) + tuple(yInfo)

def calcImageOrientation(vector):
    info = ["",""]
    for index in reversed(np.array(vector).argsort()):
        if abs(vector[index])<0.3:continue
        value = orientationList[index]
        info[0] += value[0] if vector[index] > 0 else value[1]
        info[1] += value[1] if vector[index] > 0 else value[0]
    return info

def getImageExtraInfoFromDicom(fileName):
    """从Dicom文件中读取信息，输出位置按照Location类的次序"""
    dcmFile = pyd.dcmread(fileName)
    res = {}
    for location,tagDict in normalKeyDict.items():
        tp = ""
        for tag,text in tagDict.items():
            tp = tp + text + str(dcmFile[tag].value) + "\n"
        res[location] = tp
    print(res)
    return res

def extract_grayscale_image(mri_file):
    plan = pyd.read_file(mri_file)
    image_2d = plan.pixel_array.astype(float)
    image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
    image_2d_scaled = np.uint8(image_2d_scaled)
    return image_2d_scaled

def dicom_to_qt(dcm_file, factor_contrast, factor_bright, auto_mode, inversion_mode, custom_size = (200,200)):
    image = np.array(extract_grayscale_image(dcm_file))
    image = Image.fromarray(image)
    if auto_mode == 1:
        image = ImageOps.equalize(image, mask=None)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(factor_contrast)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(factor_bright)
    if inversion_mode == 1:
        image = ImageOps.invert(image.convert('L'))
    qim = ImageQt(image)
    return (qim)

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