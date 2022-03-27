from cacheout import CacheManager,Cache
import os
import pydicom as pyd
from utils.util import checkDirValidity, isDicom
from utils.status import Status
from utils.isDicom import *
from copy import deepcopy
import sqlite3
from enum import Enum


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
        self.dataBase = sqlite3.connect('MRViewer.db')
        print("数据库已打开")
        
        sql = """
            DROP TABLE if exists `MRViewer_file`;
        """
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        print("文件表格已删除")

        sql = '''
            CREATE TABLE `MRViewer_file` (
                `id`                  INTEGER     PRIMARY KEY,
                `path`                TEXT        NOT NULL,
                `study_instance_uid`  TEXT        NOT NULL,
                `series_instance_uid` TEXT        NOT NULL,
                `study_description`   TEXT        NOT NULL,
                `series_description`  TEXT        ,
                `patient_name`        TEXT        ,
                `is_multiframe`       INTEGER     NOT NULL,
                `instance_number`     INTEGER     NOT NULL,
                `size`                INTEGER     NOT NULL
            );
        '''
        cursor.execute(sql)
        self.dataBase.commit()
        print("文件表格已打开")
        cursor.close()

    def __del__(self):
        print("end")
        self.clearAll()

    def clearDataBase(self):
        sql = '''
        DELETE from `MRViewer_file`;
        '''
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        self.dataBase.commit()
        print("数据库已清空")
        cursor.close()

    def setRootPath(self, rootPath):
        self.rootPath = rootPath

    def getRootPath(self):
        return self.rootPath

    def addStudyItem(self, studyName):
        studyPath = os.path.join(self.rootPath,studyName)
        print(studyPath)
        cursor = self.dataBase.cursor()
        # 遍历文件夹下所有dcm文件夹与多帧格式dcm
        dcmFiles = []
        for root,dirs,files in os.walk(studyPath):

            for f in files:
                file = os.path.join(root, f)
                if isDicom(file):
                    dcmFile = pyd.dcmread(file)
                    # dcmFiles.append((file, dcmFile.PatientID, ))

                    try:
                        _ = dcmFile.NumberOfFrames
                    except:
                        dcmFiles.append((file, dcmFile.StudyInstanceUID, dcmFile.SeriesInstanceUID, dcmFile.StudyDescription, dcmFile.SeriesDescription, str(dcmFile.PatientName), 0, dcmFile.InstanceNumber, os.path.getsize(file)))
                        continue
                    else:
                        if _ > 1:
                            return #!
                            
                        else:
                            dcmFiles.append((file, dcmFile.StudyInstanceUID, dcmFile.SeriesInstanceUID, dcmFile.StudyDescription, dcmFile.SeriesDescription, str(dcmFile.SeriesDescription), 0, int(dcmFile.InstanceNumber), os.path.getsize(file)))
        
        sql = r"""
            INSERT INTO `MRViewer_file` 
            (`path`, 
            `study_instance_uid`,
            `series_instance_uid`,
            `study_description`,
            `series_description`,
            `patient_name`,
            `is_multiframe`,
            `instance_number`,
            `size`) 
            VALUES (?,?,?,?,?,?,?,?,?);
        """
        # print(dcmFiles)
        cursor.executemany(sql, dcmFiles)
        self.dataBase.commit()
        cursor.close()

    def findStudyItem(self, studyName):#!
        sql = r"""
            SELECT * FROM `MRViewer_file`
            WHERE `path` = ?
        """ %(studyName)
        cursor = self.dataBase.cursor()
        cursor.execute(sql)

        return self.dataSets[studyName]

    def findDefaultStudy(self):#!
        # names = self.dataSets.cache_names()
        # if len(names) == 1:
        #     return names[0],self.dataSets[names[0]]
        
        sql = r'''
        SELECT 
        `study_description`,
        `series_description`,
        `is_multiframe`,
        `instance_number`,
        `path` FROM `MRViewer_file` t
        where `instance_number` = (
            select max(`instance_number`) from `MRViewer_file`
            WHERE `study_instance_uid` = t.`study_instance_uid` AND `series_description` = t.`series_description`
        )
        '''
        cursor = imageDataModel.dataBase.cursor()
        cursor.execute(sql)
        print("数据库已提取")
        temp = cursor.fetchall()
        cursor.close()
        # print(temp)
        return temp

    def removeStudyItem(self, studyName):
        sql = r"""
            DELETE FROM `MRViewer_file`
            WHERE `path` = ?
        """ %(studyName)
        cursor = self.dataBase.cursor()

    def addSeriesItem(self, studyName, seriesName):
        seriesPath = os.path.join(self.rootPath, studyName, seriesName)
        for sliceName in os.listdir(seriesPath):
            slicePath = os.path.join(seriesPath,sliceName)
            dcmFile = pyd.dcmread(slicePath)
      

    def addSeriesMultiFrameItem(self, studyName, seriesName, dcmFileName):#!
        """
            兼容多帧DCM的特殊情况，此时的seriesName是单张dcm的文件名
        """
        def genearte_single_frame_dicom(dcmFile, index, filename):
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

    def findSeriesTotalPaths(self, studyName, seriesName):
        """
            通过studyName, seriesName, 找到series的完全路径
            输出: series中dcm文件的完全路径, 组成的升序列表
        """
    #  `study_description`,
    #     `series_description`,
    #     `is_multiframe`,
    #     `instance_number`,
    #     `path` FROM `MRViewer_file` t
        sql = """
            SELECT `path` FROM `MRViewer_file` 
            WHERE `study_description` = \"%s\" AND `series_description` = \"%s\"
            ORDER BY `instance_number`;
        """%(studyName, seriesName)
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        paths = cursor.fetchall()
        # print(paths)
        for i in range(len(paths)):
            paths[i] = paths[i][0]
        cursor.close()
        return paths

    def findSeriesTitleInfo(self, studyName, seriesName):
        sql = """
            SELECT `series_description`,`patient_name` FROM `MRViewer_file` 
            WHERE `study_description` = \"%s\" AND `series_description` = \"%s\"
            LIMITS 1;
        """%(studyName, seriesName)
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        info = cursor.fetchall()
        # print(info)
        for i in range(len(info)):
            info[i] = info[i][0]
        cursor.close()
        return info

    def removeSeriesItem(self, studyName, seriesName):#!no use now
        self.dataSets[studyName].delete(seriesName)

    def findSliceItem(self, studyName, seriesName, sliceName):#!no use now
        return self.findSeriesTotalPaths(studyName,seriesName)[sliceName]

    def clearAll(self):
        self.clearDataBase()

        sql = """
            DROP table `MRViewer_file`;
        """
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        self.dataBase.close()
        print("文件表格已删除")

imageDataModel = ImagesDataModel()