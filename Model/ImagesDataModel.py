from cacheout import CacheManager,Cache
import os
import pydicom as pyd
from utils.util import checkDirValidity
from utils.status import Status
from copy import deepcopy

class SeriesDict(dict):

        isMultiFrame = False

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
                    print(dcmFileName)
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
        seriesDict = SeriesDict()
        for sliceName in os.listdir(seriesPath):
            slicePath = os.path.join(seriesPath,sliceName)
            dcmFile = pyd.dcmread(slicePath)
            try:
                _ = dcmFile.NumberOfFrames
            except:
                seriesDict[sliceName] = dcmFile
                continue
            else:
                if _ > 1:
                    raise self.MultiFrameExceptionError()
                else:
                    seriesDict[sliceName] = dcmFile

        self.dataSets[studyName].add(seriesName, seriesDict)

    def addSeriesMultiFrameItem(self, studyName, seriesName, dcmFileName):
        """
            兼容多帧DCM的特殊情况，此时的seriesName是单张dcm的文件名
        """
        def genearte_single_frame_dicom(dcmFile,index, filename):
            #create metadata
            file_meta = pyd.Dataset()
            file_meta.ImplementationClassUID = dcmFile.file_meta.ImplementationClassUID
            file_meta.FileMetaInformationGroupLength = dcmFile.file_meta.FileMetaInformationGroupLength
            file_meta.FileMetaInformationVersion = dcmFile.file_meta.FileMetaInformationVersion
            file_meta.ImplementationVersionName = dcmFile.file_meta.ImplementationVersionName
            file_meta.TransferSyntaxUID = dcmFile.file_meta.TransferSyntaxUID
            ds = pyd.FileDataset(filename, {},file_meta = file_meta,preamble=b"\x00" * 128)

            ds.is_little_endian = dcmFile.is_little_endian
            ds.is_implicit_VR = dcmFile.is_implicit_VR
            ds.Modality = dcmFile.Modality
            ds.ContentDate = dcmFile.ContentDate
            ds.ContentTime = dcmFile.ContentTime
            ds.StudyInstanceUID = dcmFile.StudyInstanceUID
            ds.SeriesInstanceUID = dcmFile.SeriesInstanceUID
            ds.SOPInstanceUID =  dcmFile.SOPInstanceUID
            ds.SOPClassUID = dcmFile.SOPClassUID
            # ds.SecondaryCaptureDeviceManufctur = dcmFile.SecondaryCaptureDeviceManufctur
            # ds.FrameOfReferenceUID = dcmFile.FrameOfReferenceUID
            ds.PatientName = dcmFile.PatientName
            ds.PatientID = dcmFile.PatientID
            ds.SamplesPerPixel = dcmFile.SamplesPerPixel
            ds.PhotometricInterpretation = dcmFile.PhotometricInterpretation
            ds.PixelRepresentation = dcmFile.PixelRepresentation
            ds.HighBit = dcmFile.HighBit
            ds.BitsStored = dcmFile.BitsStored
            ds.BitsAllocated = dcmFile.BitsAllocated
            # core tag
            images = dcmFile.pixel_array
            ds.PixelData = deepcopy(images[index]).tobytes()
            ds.Columns = images[index].shape[1]
            ds.Rows = images[index].shape[0]
            # ds.ImagesInAcquisition = dcmFile.ImagesInAcquisition
            return ds

        filePath = os.path.join(self.rootPath, studyName, seriesName, dcmFileName)
        dcmFile = pyd.dcmread(filePath)
        seriesDict = SeriesDict()
        seriesDict.isMultiFrame = True
        for i in range(dcmFile.NumberOfFrames):
            fileName = '{}-{}'.format(dcmFileName,i)
            _dcmFile = genearte_single_frame_dicom(dcmFile,i, fileName)
            seriesDict[fileName] = _dcmFile
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