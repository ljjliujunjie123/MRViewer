from cacheout import CacheManager,Cache
import os
import pydicom as pyd
from utils.util import checkDirValidity
from utils.status import Status

class ImagesDataModel():
    """
        该类负责提供医学图像的元数据
        在工程的任意一个地方，只需要按照Patient-Study-Series-Slice的顺序，即可获取该DCM图片的元数据信息
        metaDataSets的Key是StudyName,Value是一个Cache实例
        Cache实例中的Key是SeriesName,Value是一个Dict
        Dict的Key是FileName,Value是dcmFile
    """
    def __init__(self):
        print("ImagesDataModel Init.")
        self.dataSets = CacheManager()
        self.rootPath = ""

    def setRootPath(self, rootPath):
        self.rootPath = rootPath

    def getRootPath(self):
        return self.rootPath

    def addStudyItem(self, studyName):
        self.dataSets.register(studyName, Cache())
        studyPath = os.path.join(self.rootPath,studyName)
        for seriesName in os.listdir(studyPath):
            seriesPath = os.path.join(studyPath, seriesName)
            if checkDirValidity(seriesPath) is Status.bad:continue
            self.addSeriesItem(studyName, seriesName)

        print("current ImageDataModel:")
        print(self.dataSets.cache_names())

    def findStudyItem(self, studyName):
        return self.dataSets[studyName]

    def removeStudyItem(self, studyName):
        self.dataSets[studyName].clear()

    def addSeriesItem(self, studyName, seriesName):
        seriesPath = os.path.join(self.rootPath, studyName, seriesName)
        seriesDict = {}
        for sliceName in os.listdir(seriesPath):
            slicePath = os.path.join(seriesPath,sliceName)
            dcmFile = pyd.dcmread(slicePath)
            seriesDict[sliceName] = dcmFile
        self.dataSets[studyName].add(seriesName, seriesDict)

    def findSeriesItem(self, studyName, seriesName):
        return self.dataSets[studyName].get(seriesName)

    def removeSeriesItem(self, studyName, seriesName):
        self.dataSets[studyName].delete(seriesName)

    def findSliceItem(self, studyName, seriesName, sliceName):
        return self.findSeriesItem(studyName,seriesName)[sliceName]

    def clearAll(self):
        self.dataSets.clear_all()
        del self.dataSets
        self.dataSets = CacheManager()

imageDataModel = ImagesDataModel()