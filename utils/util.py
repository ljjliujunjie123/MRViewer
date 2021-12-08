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