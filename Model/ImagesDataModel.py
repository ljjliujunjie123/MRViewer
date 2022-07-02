import imp
import os
import pydicom as pyd
from copy import deepcopy
import sqlite3
import queue, threading, time
from enum import Enum
from PyQt5.QtWidgets import *

class Status(Enum):
    good = 1
    bad = 0 

def isDicom(filePath):
    if filePath.endswith(".dcm"):
        return True
    else:
        with open(filePath,"rb") as f:
            f.seek(128,1)
            strb = f.read(4)
            return strb == b'DICM'

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

    def __init__(self, parent):
        self.parent = parent
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
                `patient_name`        TEXT        ,
                `patient_id`          TEXT        ,
                `birth_date`          TEXT        ,
                `sex`                 TEXT        ,
                `study_date`          TEXT        ,
                `study_instance_uid`  TEXT        NOT NULL,
                `study_description`   TEXT        NOT NULL,
                `instance_number`     INTEGER     NOT NULL,
                `series_instance_uid` TEXT        NOT NULL,
                `series_description`  TEXT        ,
                `modality`            TEXT        ,
                `rows`                INTEGER     ,
                `columns`             INTEGER     ,
                `pixel_array`          BLOB        
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
        t1 = time.time()
        # 遍历文件夹下所有dcm文件夹与多帧格式dcm
        list_manager = ListManager(queue.Queue(-1))
        list_manager.add_job(list_dir,studyPath)
        list_manager.complete_all()
        # print(len(list_manager.result_list))
        # print(list_manager.result_list[1:10])
        list_manager.result_list
        t2 = time.time()
        print(t2-t1)
        #存入database
        cursor = self.dataBase.cursor()
        sql = r"""
            INSERT INTO `MRViewer_file` 
            (
            `patient_name`, `patient_id`, `birth_date`, `sex`,
            `study_date`, `study_instance_uid`, `study_description`,
            `instance_number`, `series_instance_uid`, `series_description`, 
            `modality`, `rows`,`columns`,
            `pixel_array`) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);
        """
        # print(dcmFiles)
        # print(len(list_manager.result_list))
        cursor.executemany(sql, list_manager.result_list)
        self.dataBase.commit()
        cursor.close()
        t3 = time.time()
        print(t3-t2)
        self.parent.ReloadData()

    def findStudyItem(self, studyName):#!
        sql = r"""
            SELECT * FROM `MRViewer_file`
            WHERE `path` = ?
        """ %(studyName)
        cursor = self.dataBase.cursor()
        cursor.execute(sql)

        return self.dataSets[studyName]

    def findDefaultStudy(self):
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
        cursor = self.dataBase.cursor()
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

    def clearAll(self):
        self.clearDataBase()

        sql = """
            DROP table `MRViewer_file`;
        """
        cursor = self.dataBase.cursor()
        cursor.execute(sql)
        self.dataBase.close()
        print("文件表格已删除")

    def readFromStudyDirectory(self):
        filePath = QFileDialog.getExistingDirectory(None, "选择一个Study的目录",'')
        if checkDirValidity(filePath) is Status.bad: 
            return
        rootPath,studyName = os.path.split(filePath)[0], os.path.split(filePath)[-1]
        self.clearDataBase()
        self.setRootPath(rootPath)
        self.addStudyItem(studyName)

def checkDirValidity(filePath):
    #非文件夹检查
    if not os.path.isdir(filePath):
        print("Warning:", filePath, "should be a directory not a file!")
        return Status.bad
    subPaths = os.listdir(filePath)
    #空检查
    if len(subPaths) is 0:
        print("Warning:", filePath, "is a empty directory!")
        return Status.bad
    return Status.good

##多线程遍历文件
def list_dir(directory):
    dirlist = []
    dcmFiles = []
    try:
        for item in os.listdir(directory):
            path = os.path.join(directory,item)
            if os.path.isfile(path):
                if isDicom(path):
                    dcmFile = pyd.dcmread(path)
                    try:
                        _ = dcmFile.NumberOfFrames
                    except:
                        dcmFiles.append(
                            (str(dcmFile.PatientName), dcmFile.PatientID, dcmFile.PatientBirthDate, dcmFile.PatientSex,
                            dcmFile.StudyDate, dcmFile.StudyInstanceUID, dcmFile.StudyDescription,
                            int(dcmFile.InstanceNumber), dcmFile.SeriesInstanceUID, dcmFile.SeriesDescription,
                            dcmFile.Modality, int(dcmFile.Rows), int(dcmFile.Columns),dcmFile.pixel_array)
                        )
                        continue
                    else:
                        if _ > 1:
                            return #!

                        else:
                            dcmFiles.append(
                                (str(dcmFile.PatientName), dcmFile.PatientID, dcmFile.PatientBirthDate, dcmFile.PatientSex,
                                dcmFile.StudyDate, dcmFile.StudyInstanceUID, dcmFile.StudyDescription,
                                int(dcmFile.InstanceNumber), dcmFile.SeriesInstanceUID, dcmFile.SeriesDescription,
                                dcmFile.Modality, int(dcmFile.Rows), int(dcmFile.Columns),dcmFile.pixel_array)
                            )
            else:
                dirlist.append(path)
    except:
        pass

    return (dirlist,dcmFiles)

class ListWorker(threading.Thread):
    def __init__(self,requestQueue,resultlist):
        threading.Thread.__init__(self)
        self.request_queue = requestQueue
        self.result_list = resultlist
        self.setDaemon(True) 
        self.start()

    def run(self):
        while True:
            try:
                callback,args = self.request_queue.get(block=True,timeout=0.01)
            except queue.Empty:
                break

            dirlist,filelist = callback(args[0])

            self.request_queue.task_done()#通知系统任务完成

            for item in dirlist:
                self.request_queue.put((callback,(item,)))
            self.result_list += filelist

class ListManager(object):
    def __init__(self,request_queue,threadnum=1):
        self.request_queue = request_queue
        self.result_list = []
        self.threads = []
        self.__init_thread_pool(threadnum)

    def __init_thread_pool(self,threadnum):
        for i in range(threadnum):
            self.threads.append(ListWorker(self.request_queue,self.result_list))

    def add_job(self,callback,*args):
        self.request_queue.put((callback,args))

    def complete_all(self):
        while len(self.threads):
            worker = self.threads.pop()
            worker.join()