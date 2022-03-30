import numpy as np
import os
from PIL.ImageQt import *
from utils.status import Status
from ui.config import uiConfig
from PyQt5.QtCore import *
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingAnnotation import vtkAnnotatedCubeActor
from vtkmodules.util.numpy_support import numpy_to_vtk
import vtkmodules.all as vtk
from vtkmodules.util.vtkConstants import *
import string

def createDicomPixmap(dcmFile):
    image_2d = dcmFile.pixel_array.astype(float)
    image_2d_scaled = (np.maximum(image_2d, 0) / max(image_2d.max(),1)) * 255.0
    image_2d_scaled = np.uint8(image_2d_scaled)#!
    image = Image.fromarray(image_2d_scaled)
    dcmImage = ImageQt(image)
    pix = QPixmap.fromImage(dcmImage)
    pixmap_resized = pix.scaled(uiConfig.iconSize, Qt.KeepAspectRatio)
    return pixmap_resized

def getSeriesPathFromFileName(fileName):
    return os.path.split(fileName)[0]

def getSeriesImageCountFromSeriesPath(seriesPath):
    return len(os.listdir(seriesPath))

def checkSameStudy(df1,df2):
    try:
        return (df1["PatientName"] == df2["PatientName"]) and (df1["StudyDescription"] == df2["StudyDescription"])
    except:
        return False

def checkSameSeries(df1,df2):
    try:
        return df1["SeriesDescription"] == df2["SeriesDescription"]
    except:
        True

def MakeAnnotatedCubeActor(colors: vtkNamedColors):
        """
        :param colors: Used to determine the cube color.
        :return: The annotated cube actor.
        """
        # A cube with labeled faces.
        cube = vtkAnnotatedCubeActor()
        cube.SetXPlusFaceText('R')  # Right
        cube.SetXMinusFaceText('L')  # Left
        cube.SetYPlusFaceText('A')  # Anterior
        cube.SetYMinusFaceText('P')  # Posterior
        cube.SetZPlusFaceText('S')  # Superior/Cranial
        cube.SetZMinusFaceText('I')  # Inferior/Caudal
        cube.SetFaceTextScale(0.5)
        cube.GetCubeProperty().SetColor(colors.GetColor3d('Gainsboro'))

        cube.GetTextEdgesProperty().SetColor(colors.GetColor3d('LightSlateGray'))

        # Change the vector text colors.
        cube.GetXPlusFaceProperty().SetColor(colors.GetColor3d('Tomato'))
        cube.GetXMinusFaceProperty().SetColor(colors.GetColor3d('Tomato'))
        cube.GetYPlusFaceProperty().SetColor(colors.GetColor3d('DeepSkyBlue'))
        cube.GetYMinusFaceProperty().SetColor(colors.GetColor3d('DeepSkyBlue'))
        cube.GetZPlusFaceProperty().SetColor(colors.GetColor3d('SeaGreen'))
        cube.GetZMinusFaceProperty().SetColor(colors.GetColor3d('SeaGreen'))
        return cube

def numpy2VTK(img):
    shape = img.shape
    if len(shape) < 2:
        raise Exception('numpy array must have dimensionality of at least 2')

    height, width = shape[0], shape[1]
    c = shape[2] if len(shape) == 3 else 1

    linear_array = np.reshape(img, (width * height, c))
    vtk_array = numpy_to_vtk(linear_array)

    imageData = vtk.vtkImageData()
    imageData.SetDimensions(width, height, 1)
    imageData.AllocateScalars(VTK_UNSIGNED_INT, 1)
    imageData.GetPointData().GetScalars().DeepCopy(vtk_array)

    return imageData

def isDicom(filePath: string):
    if filePath.endswith(".dcm"):
        return True
    else:
        with open(filePath,"rb") as f:
            f.seek(128,1)
            strb = f.read(4)
            # return strb == b'DICM'
            return strb == b'DICM'
                