from pydicom import *

import numpy as np
import pydicom as pyd
import os
from PIL import Image, ImageOps, ImageEnhance
from PIL.ImageQt import *
from PyQt5.QtCore import *

import cv2

def getDicomWindowCenterAndLevel(fileName):
    dcmFile = dcmread(fileName)
    return (dcmFile.WindowCenter, dcmFile.WindowWidth)

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