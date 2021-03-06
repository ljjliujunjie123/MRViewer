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

def checkMultiFrame(seriesDict):
    return seriesDict.isMultiFrame

def createDicomPixmap(dcmFile):
    image_2d = dcmFile.pixel_array.astype(float)
    image_2d_scaled = (np.maximum(image_2d, 0) / max(image_2d.max(),1)) * 255.0
    image_2d_scaled = np.uint8(image_2d_scaled)#!
    image = Image.fromarray(image_2d_scaled)
    dcmImage = ImageQt(image)
    pix = QPixmap.fromImage(dcmImage)
    pixmap_resized = pix.scaled(uiConfig.iconSize, Qt.KeepAspectRatio)
    return pixmap_resized

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

def create_color_from_hexString(color):
    if color[0] == "#":
        # Convert hex string to RGB
        return [int(color[i:i + 2], 16) / 255 for i in range(1, 7, 2)]
    else:
        return [0,0,0]

def isDicom(filePath):
    if filePath.endswith(".dcm"):
        return True
    else:
        with open(filePath,"rb") as f:
            f.seek(128,1)
            strb = f.read(4)
            # return strb == b'DICM'
            return strb == b'DICM'