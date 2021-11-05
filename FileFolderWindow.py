from PyQt5 import QtCore, QtGui, QtWidgets

class FileFolderWindow(object):
    def setupUI(self, MainWindow):
        MainWindow.setObjectName("FileFolderWindow")
        MainWindow.resize(1500,1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setGeometry(QtCore.QRect(0,0,1500,1000))

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        model = QtWidgets.QDirModel()
        self.treeView.setModel(model)

        self.treeView.setColumnWidth(0,800)

        self.treeView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.treeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.treeView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)

        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.treeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.treeView.setAutoExpandDelay(-1)
        self.treeView.setItemsExpandable(True)
        self.treeView.setSortingEnabled(True)
        self.treeView.setWordWrap(True)
        self.treeView.setHeaderHidden(True)
        self.treeView.setExpandsOnDoubleClick(True)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setVisible(True)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUI(MainWindow)

    def retranslateUI(self,MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow","FileFolderWindow"))