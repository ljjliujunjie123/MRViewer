from cacheout import CacheManager,Cache
import os
import pydicom as pyd
from utils.util import checkDirValidity
from utils.status import Status
from copy import deepcopy
from utils.util import checkMultiFrame

class ImagesDataModel():
    """
        该类负责提供医学图像的元数据
        在工程的任意一个地方，只需要按照Patient-Study-Series-Slice的顺序，即可获取该DCM图片的元数据信息
        metaDataSets的Key是StudyName,Value是一个Cache实例
        Cache实例中的Key是SeriesName,Value是一个Dict
        Dict的Key是FileName,Value是dcmFile
    """

    class MultiFrameExceptionError(Exception):
        pass

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
            try:
                self.addSeriesItem(studyName, seriesName)
            except self.MultiFrameExceptionError:
                print("当前series的dcm为多帧格式dcm")
                for dcmFileName in os.listdir(seriesPath):
                    self.addSeriesMultiFrameItem(studyName, seriesName, dcmFileName)

        print("current ImageDataModel:")
        print(self.dataSets.cache_names())

    def findStudyItem(self, studyName):
        return self.dataSets[studyName]

    def findDefaultStudy(self):
        names = self.dataSets.cache_names()
        if len(names) == 1:
            return names[0],self.dataSets[names[0]]

    def removeStudyItem(self, studyName):
        self.dataSets[studyName].clear()

    def addSeriesItem(self, studyName, seriesName):
        seriesPath = os.path.join(self.rootPath, studyName, seriesName)
        seriesDict = {}
        for sliceName in os.listdir(seriesPath):
            slicePath = os.path.join(seriesPath,sliceName)
            dcmFile = pyd.dcmread(slicePath)
            if checkMultiFrame(dcmFile):
                raise self.MultiFrameExceptionError()
            seriesDict[sliceName] = dcmFile
        self.dataSets[studyName].add(seriesName, seriesDict)

    def addSeriesMultiFrameItem(self, studyName, seriesName, dcmFileName):
        """
            兼容多帧DCM的特殊情况，此时的seriesName是单张dcm的文件名
        """
        filePath = os.path.join(self.rootPath, studyName, seriesName, dcmFileName)
        dcmFile = pyd.dcmread(filePath)
        images = dcmFile.pixel_array
        seriesDict = {}
        for i in range(dcmFile.NumberOfFrames):
            _dcmFile = deepcopy(dcmFile)
            _dcmFile.pix_array = deepcopy(images[i])
            seriesDict['{}-{}'.format(dcmFileName,i)] = _dcmFile
        self.dataSets[studyName].add(dcmFileName, seriesDict)

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