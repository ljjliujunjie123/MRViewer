from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from ui.config import uiConfig

class CustomDicomTagsWindow(QDialog):

    updataSearchSignal= pyqtSignal(str)
    tableHeaderDict = {
        'Tag ID': 0,
        'VR': 1,
        'VM': 2,
        'Description': 3,
        'Value': 4
    }  # 为表头名称设置默认值
    tableHeaderWidthDict = {
        'Tag ID': 3,
        'VR': 1,
        'VM': 1,
        'Description': 5,
        'Value': 7
    }  # 为表头宽度设置默认值
    tableHeaderHeight=50

    def __init__(self,closeCallBack, parent=None):
        QDialog.__init__(self,parent)
        flags = self.windowFlags()
        flags |= Qt.WindowMinMaxButtonsHint
        self.setStyleSheet("background-color:{0};border:2px".format(uiConfig.LightColor.White))
        self.setWindowFlags(flags)
        self.table = None
        self.updataSearchSignal.connect(self.updataSearch)
        self.RectWidth= uiConfig.screenWidth
        self.RectHeight= uiConfig.screenHeight
        self.filePath=''
        self.closeCallBack = closeCallBack
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(10,10,10,0)
        mainLayout.setSpacing(0)
        self.setGeometry(self.RectWidth/4,self.RectHeight/4, self.RectWidth/2, self.RectHeight/2)
        self.table = self.createTable()
        mainLayout.addWidget(self.table)  # 在主页面插入表格
        mainLayout.addLayout(self.createHboxGroupBoxLayout())  # 再整体插入下方的水平布局
        self.setLayout(mainLayout)
        self.setWindowIcon(QIcon("ui_source/win_title_icon_color.png"))
        self.setWindowTitle('Dicom Tags')

    def injectDicomData(self, dcmData):
        self.updateTable(dcmData)

    def createHboxGroupBoxLayout(self):
        layout=QHBoxLayout()
        layout.setContentsMargins(0,10,0,10)
        layout.setAlignment(Qt.AlignVCenter)

        #搜索框
        searchLineEdit=QLineEdit()
        searchLineEdit.setPlaceholderText("Find text...")
        searchLineEdit.setStyleSheet('background-color:white')
        searchLineEdit.textChanged.connect(self.textsearch)#输入文本后自动搜索

        #关闭窗口
        CloseBtn=QPushButton("Close")
        CloseBtn.setStyleSheet('''QPushButton{background:grey}''')

        CloseBtn.clicked.connect(self.close)#点击“close”关闭窗口

        layout.addWidget(searchLineEdit,2)
        layout.addStretch(6)
        layout.addWidget(CloseBtn,1)

        return layout

    def updateTable(self, dcmData):
        self.table.clearContents()
        self.table.setRowCount(0)

        ds = dcmData

        def createItem(key, header):
            item = QTableWidgetItem()
            text = ''
            if header == 'Tag ID':
                text = str(ds[key].tag)
            elif header == 'VR':
                text = ds[key].VR
            elif header == 'VM':
                text = str(ds[key].VM)
            elif header == 'Description':
                text = ds[key].keyword
            elif header == 'Value':
                text = str(ds[key].value)
            item.setText(text)
            return item

        for i,key in enumerate(ds._dict.keys()):
            self.table.insertRow(i)  # 最下面加一行
            for header in self.tableHeaderDict.keys():
                newItem = createItem(key, header)
                self.table.setItem(i, self.tableHeaderDict[header], newItem)

        self.table.sortItems(0, Qt.AscendingOrder)

    def createTable(self):#创建表格
        table = QTableWidget(0, len(self.tableHeaderDict.keys()))  # 创建表格,这里后续要改为行数与文件数相同
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setFrameShape(QFrame.NoFrame)  # 无边框的表格
        for key in self.tableHeaderDict.keys():
            table.horizontalHeader().resizeSection(self.tableHeaderDict[key],self.width()*self.tableHeaderWidthDict[key]/sum(self.tableHeaderWidthDict.values()))
        table.horizontalHeader().setFixedHeight(self.tableHeaderHeight)  # 表头高度
        table.horizontalHeader().setSectionResizeMode(len(self.tableHeaderDict.keys())-1, QHeaderView.Stretch)  # 设置第最后一列宽度自动调整，充满屏幕
        table.horizontalHeader().setStretchLastSection(True)  # 设置最后一列拉伸至最大列无限延伸
        table.setStyleSheet("background-color:white;")
        table.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:white;}")


        for key in self.tableHeaderDict.keys():
            item=QTableWidgetItem()
            item.setText(key)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setHorizontalHeaderItem(self.tableHeaderDict[key], item)

        table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格不可更改
        table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置不可选择单个单元格，只可选择一行。
        table.verticalHeader().setVisible(False) #列表头不可见
        table.setShowGrid(False) #格线不可见
        return table

    def textsearch(self,text):#在搜索框里打字
        self.updataSearchSignal.emit(text)

    def updataSearch(self,text):
        rowsSet = set([item.row() for item in self.table.findItems(text, Qt.MatchContains)])

        for i in range(self.table.rowCount()):
            self.table.setRowHidden(i,True)

        for row in rowsSet:
            self.table.setRowHidden(row,False)

    def closeEvent(self, QCloseEvent) -> None:
        super().closeEvent(QCloseEvent)
        self.closeCallBack(self)
