from Model.ImagesDataModel import imageDataModel
import numpy as np
from enum import Enum
import os
from utils.status import Status

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


class BaseImageData():

    def __init__(self):
        self.filePaths = []
        self.curFilePath = ""
        self.studyName = ""
        self.seriesName = ""
        self.seriesImageCount = 0
        self.currentIndex = 0

    def getSeriesPath(self):
        return os.path.join(imageDataModel.getRootPath(), self.studyName, self.seriesName)

    def getDcmDataByIndex(self, index):
        seriesDict = imageDataModel.findSeriesItem(self.studyName, self.seriesName)
        return seriesDict[list(seriesDict.keys())[index]]

    def getBasePosInfo(self, index):
        dcmData = self.getDcmDataByIndex(index)
        img_array = dcmData.pixel_array# indexes are z,y,x
        ImagePosition =np.array(dcmData.ImagePositionPatient,dtype=float)
        ImageOrientation=np.array(dcmData.ImageOrientationPatient,dtype = float)
        PixelSpacing =dcmData.PixelSpacing
        # SliceThickness=RefDs.SliceThickness
        ImageOrientationX=ImageOrientation[0:3]
        ImageOrientationY=ImageOrientation[3:6]
        Rows = dcmData.Rows
        Cols = dcmData.Columns
        #图像平面法向量(X与Y的叉积)
        normalvector = np.cross(ImageOrientationX,ImageOrientationY)
        return img_array,normalvector,ImagePosition,PixelSpacing,ImageOrientationX,ImageOrientationY,Rows,Cols

    def getImageTileInfo(self, index):
        dcmData = self.getDcmDataByIndex(index)

        try:
            patientName = str(dcmData["PatientName"].value)
        except:
            patientName = "Unknown"

        try:
            seriesDescription = str(dcmData["SeriesDescription"].value)
        except:
            seriesDescription = "Unknown"

        res = ""
        res += (normalKeyDict[Location.UL]["PatientName"] +  patientName)
        res += " - "
        res += (normalKeyDict[Location.UL]["SeriesDescription"] + seriesDescription)
        return res

    def getDicomWindowCenterAndLevel(self, index):
        dcmData = self.getDcmDataByIndex(index)
        try:
            center,width = dcmData.WindowCenter,dcmData.WindowWidth
        except:
            center,width = 500,500
        return center,width

    def getImageOrientationInfoFromDicom(self, index):
        """
            判断方向向量与标准轴的cos值，如果大于阈值，则增加一个标识
        """
        dcmData = self.getDcmDataByIndex(index)
        try:
            ImageOrientation=np.array(dcmData.ImageOrientationPatient,dtype = float)
        except:
            return Status.bad
        xVector,yVector = ImageOrientation[:3],ImageOrientation[3:]
        func = lambda x:round(x,1)
        xVector,yVector = tuple(map(func,xVector)),tuple(map(func,yVector))
        print("orientation vector ", xVector, yVector)
        xInfo = self.calcImageOrientation(xVector)
        yInfo = self.calcImageOrientation(yVector)
        print(xInfo,yInfo)
        return tuple(xInfo) + tuple(yInfo)

    def getImageExtraInfoFromDicom(self, index):
        """输出位置按照Location类的次序"""
        dcmData = self.getDcmDataByIndex(index)
        res = {}
        for location,tagDict in normalKeyDict.items():
            tp = ""
            for tag,text in tagDict.items():
                try:
                    tagValue = str(dcmData[tag].value)
                except:
                    tagValue = "Unknown"
                tp = tp + text + tagValue + "\n"
            res[location] = tp
        print(res)
        return res

    def calcImageOrientation(self,vector):
        info = ["",""]
        for index in reversed(np.array(vector).argsort()):
            if abs(vector[index])<0.3:continue
            value = orientationList[index]
            info[0] += value[0] if vector[index] > 0 else value[1]
            info[1] += value[1] if vector[index] > 0 else value[0]
        return info
