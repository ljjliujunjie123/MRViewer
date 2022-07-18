import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QModelIndex,QItemSelectionModel,pyqtSignal
from PyQt5.QtGui import QCursor, QMouseEvent,QStandardItemModel
from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase
from Model.ImagesDataModel import imageDataModel, Kind
from matplotlib.pyplot import connect

class DataBaseDisplayer(QFrame):
    selectFileSignal = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("DataBaseDisplayer")
        self.imageDataModel = imageDataModel
        self.db = None
        self.db_connect()
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.InitializeContent()
        # itemEntered.connect(self.ShowTooltip(self.table1))
    def db_connect(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("./MRViewer.db")
        if not self.db.open():
            QMessageBox.critical(self, 'Database Connection', self.db.lastError().text())

    def InitializeContent(self):
        self.queryModel1 = QSqlQueryModel(self)
        self.queryModel1.setHeaderData(0, Qt.Horizontal, 'Patient name')
        self.queryModel1.setHeaderData(1, Qt.Horizontal, 'Patient ID')
        self.queryModel1.setHeaderData(2, Qt.Horizontal, 'Birth date')
        self.queryModel1.setHeaderData(3, Qt.Horizontal, 'Sex')
        self.queryModel1.setHeaderData(4, Qt.Horizontal, 'Studies number')

        self.table1 = QTableView(self)
        self.table1.setModel(self.queryModel1)
        self.select1 = QItemSelectionModel(self.queryModel1, self)
        self.select1.currentRowChanged.connect(lambda:self.ReloadStudyData())
        self.table1.setSelectionModel(self.select1)
        self.TableSetting(self.table1)
        self.table1.doubleClicked.connect(self.DoubleClick1)

        self.queryModel2 = QSqlQueryModel(self)
        self.queryModel2.setHeaderData(0, Qt.Horizontal, 'Study date')
        self.queryModel2.setHeaderData(1, Qt.Horizontal, 'Study ID')
        self.queryModel2.setHeaderData(2, Qt.Horizontal, 'Study description')
        self.queryModel2.setHeaderData(3, Qt.Horizontal, 'Series')

        self.table2 = QTableView(self)
        self.table2.setModel(self.queryModel2)
        self.select2 = QItemSelectionModel(self.queryModel2, self)
        self.select2.currentRowChanged.connect(lambda:self.ReloadSeriesData())
        self.table2.setSelectionModel(self.select2)
        self.TableSetting(self.table2)
        self.table2.doubleClicked.connect(self.DoubleClick2)


        self.queryModel3 = QSqlQueryModel(self)
        self.queryModel3.setHeaderData(0, Qt.Horizontal, 'Series #')
        self.queryModel3.setHeaderData(1, Qt.Horizontal, 'Series description')
        self.queryModel3.setHeaderData(2, Qt.Horizontal, 'Modality')
        self.queryModel3.setHeaderData(3, Qt.Horizontal, 'Rows')
        self.queryModel3.setHeaderData(4, Qt.Horizontal, 'Columns')
        self.queryModel3.setHeaderData(5, Qt.Horizontal, 'Count')
        self.table3 = QTableView(self)
        self.table3.setModel(self.queryModel3)
        self.select3 = QItemSelectionModel(self.queryModel3, self)
        self.select3.currentRowChanged.connect(lambda:self.parent.ShiftToImage)
        self.table3.setSelectionModel(self.select3)
        self.TableSetting(self.table3)
        self.table3.doubleClicked.connect(self.DoubleClick3)


        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)
        layout.addWidget(self.table1)
        layout.addWidget(self.table2)
        layout.addWidget(self.table3)

    def TableSetting(self,table:QTableView):
        table.verticalHeader().setHidden(True)
        table.setShowGrid(True)
        table.setObjectName("Table")
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    # def ShowTooltip(self, item: QTableWidgetItem):
    #     if item== None:
    #         return
    #     QToolTip.showText(QCursor.pos(), item.text())

    def ReloadData(self):
        self.queryModel1.setQuery(r"""
            SELECT patient_name, patient_id, birth_date, sex, COUNT(*) from 
            (SELECT distinct patient_name, patient_id, birth_date, sex, study_instance_uid from MRViewer_file)
            GROUP BY patient_id
            """
        )
        # QSqlTableModel  select数据完成后，当数据记录数目多于256时，rowCount 返回值最大为256.为了强制获取整个数据集
        # 所以必须实现以下，否则返回256
        while(self.queryModel1.canFetchMore()):
            self.queryModel1.fetchMore()
        if self.queryModel1.rowCount() >= 0:
            self.table1.setCurrentIndex(self.queryModel1.index(0,1))
        self.table1.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
        self.table1.horizontalHeader().setStretchLastSection(True)

    def ReloadStudyData(self):
        index = self.queryModel1.index(self.table1.currentIndex().row(),1)
        data = self.queryModel1.data(index)
        sql =r"""
            SELECT study_date, study_instance_uid, study_description, COUNT(*) from 
            (SELECT distinct study_date, study_instance_uid, study_description, series_instance_uid FROM MRViewer_file
            """ + r"WHERE patient_id = '" + str(data) +r"""')
            GROUP BY study_instance_uid
            ORDER BY study_date desc
            """
        self.queryModel2.setQuery(sql,self.db)
        self.table2.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
        self.table2.horizontalHeader().setStretchLastSection(True)
        while(self.queryModel2.canFetchMore()):
            self.queryModel2.fetchMore()
        if self.queryModel2.rowCount() >= 0:
            self.table2.setCurrentIndex(self.queryModel2.index(0,1))

    def ReloadSeriesData(self):
        index = self.queryModel2.index(self.table2.currentIndex().row(),1)
        data = self.queryModel2.data(index)
        sql = r"""
            SELECT series_instance_uid, series_description, modality, rows, columns, instance_number FROM MRViewer_file t
            WHERE instance_number = (
            select max(`instance_number`) from `MRViewer_file`
            WHERE `study_instance_uid` = t.`study_instance_uid` AND `series_instance_uid` = t.`series_instance_uid` AND
            study_instance_uid = '""" + str(data) +r"""')"""
        self.queryModel3.setQuery(sql,self.db)
        self.table3.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
        self.table3.horizontalHeader().setStretchLastSection(True)
        while(self.queryModel3.canFetchMore()):
            self.queryModel3.fetchMore()

    def DoubleClick1(self):
        # 选中单元格的值传给ImageDisplayer
        index = self.queryModel1.index(self.table1.currentIndex().row(),1)
        data = self.queryModel1.data(index)
        self.imageDataModel.currentKind = Kind.patient
        self.imageDataModel.currentId = []
        self.imageDataModel.currentId.append(data)
        print(self.imageDataModel.currentId)
        self.selectFileSignal.emit()
        self.parent.ShiftToImage()
        

    def DoubleClick2(self):
        # 选中单元格的值传给ImageDisplayer
        index = self.queryModel1.index(self.table1.currentIndex().row(),1)
        data = self.queryModel1.data(index)
        index2 = self.queryModel2.index(self.table2.currentIndex().row(),1)
        data2 = self.queryModel2.data(index2)
        self.imageDataModel.currentKind = Kind.study
        self.imageDataModel.currentId = []
        self.imageDataModel.currentId.append(data)
        self.imageDataModel.currentId.append(data2)
        print(self.imageDataModel.currentId)
        self.selectFileSignal.emit()
        self.parent.ShiftToImage()


    def DoubleClick3(self):
        # 选中单元格的值传给ImageDisplayer
        index = self.queryModel1.index(self.table1.currentIndex().row(),1)
        data = self.queryModel1.data(index)
        index2 = self.queryModel2.index(self.table2.currentIndex().row(),1)
        data2 = self.queryModel2.data(index2)
        index3 = self.queryModel3.index(self.table3.currentIndex().row(),0)
        data3 = self.queryModel3.data(index3)
        self.imageDataModel.currentKind = Kind.series
        self.imageDataModel.currentId = []
        self.imageDataModel.currentId.append(data)
        self.imageDataModel.currentId.append(data2)
        self.imageDataModel.currentId.append(data3)
        print(self.imageDataModel.currentId)
        self.selectFileSignal.emit()
        self.parent.ShiftToImage()
    
    def ReadNewDirectory(self):
        self.imageDataModel.readFromStudyDirectory()
        self.ReloadData()