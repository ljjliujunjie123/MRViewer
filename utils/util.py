import numpy as np
import pydicom as pyd
import os
from PIL import ImageOps, ImageEnhance
from PIL.ImageQt import *

import cv2

normalKeyDict = {
        "PatientName": "",
        "StudyDescription": "Study: ",
        "SeriesDescription": "Series: ",
        "InstanceNumber": "Index: ",
        "RepetitionTime": "TR: ",
        "EchoTime": "TE: ",
        "SliceThickness": "Slice Thickness: "
    }

orientationDict = {
    (1,0,0):("R","L"),
    (0,1,0):("A","P"),
    (0,0,1):("I","S"),
    (-1,0,0):("L","R"),
    (0,-1,0):("P","A"),
    (0,0,-1):("S","I")
}

def getDicomWindowCenterAndLevel(fileName):
    dcmFile = pyd.dcmread(fileName)
    return (dcmFile.WindowCenter, dcmFile.WindowWidth)

def getImageTileInfoFromDicom(fileName):
    dcmFile = pyd.dcmread(fileName)
    res = ""
    res += (normalKeyDict["PatientName"] +  str(dcmFile["PatientName"].value))
    res += " - "
    res += (normalKeyDict["SeriesDescription"] +  str(dcmFile["SeriesDescription"].value))
    return res

def getImageOrientationInfoFromDicom(fileName):
    dcmFile = pyd.dcmread(fileName)
    ImageOrientation=np.array(dcmFile.ImageOrientationPatient,dtype = float)
    xVector,yVector = ImageOrientation[:3],ImageOrientation[3:]
    func = lambda x:round(x)
    xVector,yVector = tuple(map(func,xVector)),tuple(map(func,yVector))
    print("orientation vector ", xVector, yVector)
    xInfo,yInfo = orientationDict[xVector],orientationDict[yVector]
    return xInfo + yInfo

def getImageExtraInfoFromDicom(fileName):
    dcmFile = pyd.dcmread(fileName)

    res = ""
    valueDict = {}
    for key,value in normalKeyDict.items():
        valueDict[value] = str(dcmFile[key].value)
    for key,value in valueDict.items():
        res += (key + value + "\n")
    return res

def extract_grayscale_image(mri_file):
    plan = pyd.read_file(mri_file)
    image_2d = plan.pixel_array.astype(float)
    image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
    image_2d_scaled = np.uint8(image_2d_scaled)
    return image_2d_scaled

def dicom_to_qt(dcm_file, factor_contrast, factor_bright, auto_mode, inversion_mode, custom_size = (200,200)):
    image = np.array(extract_grayscale_image(dcm_file))
    image = cv2.resize(image, (200,200), cv2.INTER_AREA)
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