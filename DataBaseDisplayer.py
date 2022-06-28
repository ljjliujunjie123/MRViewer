from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QCursor
from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase
from Model.ImagesDataModel import ImagesDataModel
from matplotlib.pyplot import connect

class DataBaseDisplayer(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.imageDataModel = ImagesDataModel(self)
        self.db = None
        self.db_connect()
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.InitializeContent()
        self.setMouseTracking(True)
        self.table1.itemEntered.connect(self.ShowTooltip(self.table1))
    def db_connect(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("./MRViewer.db")
        if not self.db.open():
            QMessageBox.critical(self, 'Database Connection', self.db.lastError().text())

    def InitializeContent(self):
        self.queryModel1 = QSqlQueryModel(self)
        self.queryModel1.setQuery("SELECT patient_name, patient_id, birth_date, sex, COUNT(*) from MRViewer_file")
        # QSqlTableModel  select数据完成后，当数据记录数目多于256时，rowCount 返回值最大为256.为了强制获取整个数据集
        # 所以必须实现以下，否则返回256
        while(self.queryModel1.canFetchMore()):
            self.queryModel1.fetchMore()
        self.queryModel1.setHeaderData(0, Qt.Horizontal, 'Patient name')
        self.queryModel1.setHeaderData(1, Qt.Horizontal, 'Patient ID')
        self.queryModel1.setHeaderData(2, Qt.Horizontal, 'Birth date')
        self.queryModel1.setHeaderData(3, Qt.Horizontal, 'Sex')
        self.queryModel1.setHeaderData(4, Qt.Horizontal, 'Studies number')
        self.table1 = QTableView(self)
        self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table1.setModel(self.queryModel1)

        self.queryModel2 = QSqlQueryModel(self)
        self.queryModel2.setQuery("SELECT study_date, study_instance_uid, study_description, COUNT(*) FROM MRViewer_file")
        self.queryModel2.setHeaderData(0, Qt.Horizontal, 'Study date')
        self.queryModel2.setHeaderData(1, Qt.Horizontal, 'Study ID')
        self.queryModel2.setHeaderData(2, Qt.Horizontal, 'Study description')
        self.queryModel2.setHeaderData(3, Qt.Horizontal, 'Series')
        self.table2 = QTableView(self)
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table2.setModel(self.queryModel2)

        self.queryModel3 = QSqlQueryModel(self)
        self.queryModel3.setQuery("SELECT series_instance_uid, series_description, modality, rows, columns, COUNT(*) FROM MRViewer_file")
        self.queryModel3.setHeaderData(0, Qt.Horizontal, 'Series #')
        self.queryModel3.setHeaderData(1, Qt.Horizontal, 'Series description')
        self.queryModel3.setHeaderData(2, Qt.Horizontal, 'Modality')
        self.queryModel3.setHeaderData(3, Qt.Horizontal, 'Rows')
        self.queryModel3.setHeaderData(4, Qt.Horizontal, 'Columns')
        self.queryModel3.setHeaderData(5, Qt.Horizontal, 'Count')
        self.table3 = QTableView(self)
        self.table3.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table3.setModel(self.queryModel3)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.table1)
        layout.addWidget(self.table2)
        layout.addWidget(self.table3)

    def ShowTooltip(self, index: QModelIndex):
        QToolTip.showText(QCursor.pos(), index.data().toString())

    def ReloadData(self):
        self.queryModel1.setQuery("SELECT patient_name, patient_id, birth_date, sex, COUNT(*) from MRViewer_file")
        while(self.queryModel1.canFetchMore()):
            self.queryModel1.fetchMore()
        self.queryModel2.setQuery("SELECT study_date, study_instance_uid, study_description, COUNT(*) FROM MRViewer_file")
        while(self.queryModel2.canFetchMore()):
            self.queryModel2.fetchMore()
        self.queryModel3.setQuery("SELECT series_instance_uid, series_description, modality, rows, columns, COUNT(*) FROM MRViewer_file")
        while(self.queryModel3.canFetchMore()):
            self.queryModel3.fetchMore()