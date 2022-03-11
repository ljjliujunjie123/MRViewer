from cacheout import CacheManager,Cache
import os
import pydicom as pyd
from utils.util import checkDirValidity, isDicom
from utils.status import Status
from utils.isDicom import *
from copy import deepcopy
import pymysql
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
        self.rootPath = ""
        self.dataBase = pymysql.connect(host='localhost',
            user='user',
            password='passwd',
            database='MRViewer',
            charset='utf8mb4')
        
    def initDataBase(self):
        # 创建表
        sql = '''CREATE TABLE `MRViewer_file` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `path` text ,
        `patient` INT NOT NULL ,
        `is_multiframe` INT NOT NULL ,
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        '''
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        self.dataBase.commit()
        cursor.close()

    def clearDataBase(self):
        sql = '''
        truncate TABLE `MRViewer_file`;
        DROP TABLE `MRViewer_file`;
        '''
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        self.dataBase.commit()
        cursor.close()

    def setRootPath(self, rootPath):
        self.rootPath = rootPath

    def getRootPath(self):
        return self.rootPath

    def addStudyItem(self, studyName):
        studyPath = os.path.join(self.rootPath,studyName)

        # 
        # with self.dataBase:
        #     with self.dataBase.cursor() as cursor:
        #         # Create a new record
        #         sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
        #         # cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

        #     # dataBase is not autocommit by default. So you must commit to save
        #     # your changes.
        #     self.dataBase.commit()
        for root,dirs,files in os.walk(studyPath):
            for file in files:
                print(os.path.join(root,file))
                if isDicom(file):
                    try:
                        self.addSeriesItem(studyName, seriesName)
                    except self.MultiFrameExceptionError:
                        print("当前series的dcm为多帧格式dcm")
                        for dcmFileName in os.listdir(seriesPath):
                            print(dcmFileName)
                            self.addSeriesMultiFrameItem(studyName, seriesName, dcmFileName)

        # for seriesName in os.listdir(studyPath):
        #     seriesPath = os.path.join(studyPath, seriesName)
        #     if checkDirValidity(seriesPath) is Status.bad:continue
        #     try:
        #         self.addSeriesItem(studyName, seriesName)
        #     except self.MultiFrameExceptionError:
        #         print("当前series的dcm为多帧格式dcm")
        #         for dcmFileName in os.listdir(seriesPath):
        #             print(dcmFileName)
        #             self.addSeriesMultiFrameItem(studyName, seriesName, dcmFileName)

        # print("current ImageDataModel:")
        # print(self.dataSets.cache_names())#!

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
        self.dataBase.close()

imageDataModel = ImagesDataModel()

"""
#!/usr/bin/python3
 
import pymysql
 
# 打开数据库连接
db = pymysql.connect(host='localhost',
                     user='testuser',
                     password='test123',
                     database='TESTDB')
 
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()
 
# 使用 execute()  方法执行 SQL 查询 
cursor.execute("SELECT VERSION()")
 
# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()
 
print ("Database version : %s " % data) 
# 关闭数据库连接
db.close()




conn = pymysql.connect(host='localhost',user='root',password='123456',charset='utf8mb4')
# 创建游标
cursor = conn.cursor()
 
# 创建数据库的sql(如果数据库存在就不创建，防止异常)
sql = "CREATE DATABASE IF NOT EXISTS db_name" 
# 执行创建数据库的sql
cursor.execute(sql)
 
 
# 创建表
sql_2 = '''CREATE TABLE `employee` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `topic` INT ,
  `ptid` INT NOT NULL,
  `level` INT NOT NULL,
  `time` TIME,
  `consume` INT NOT NULL,
  `err` INT NOT NULL,
  `points` INT NOT NULL,
  `gid` INT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''

"""