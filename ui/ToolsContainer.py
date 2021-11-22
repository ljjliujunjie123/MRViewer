from PyQt5 import QtWidgets,QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

class ToolsContainer(QtWidgets.QFrame):

    showInfoSig = pyqtSignal()

    def __init__(self, ParentWidget):
        QtWidgets.QFrame.__init__(self, ParentWidget)

        self.setGeometry(QtCore.QRect(2200, 0, 200, 1600))
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setObjectName("toolsContainer")

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 200, 1600))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.toolsVerticalContainer = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.toolsVerticalContainer.setContentsMargins(0, 0, 0, 0)
        self.toolsVerticalContainer.setObjectName("toolsVerticalContainer")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout_2.addItem(spacerItem)

        spacerItem1 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.toolsVerticalContainer.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout_3.addItem(spacerItem3)

        spacerItem4 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.toolsVerticalContainer.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout.addItem(spacerItem6)

        spacerItem7 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout.addItem(spacerItem7)
        self.pushButton_3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20)
        self.horizontalLayout.addItem(spacerItem8)
        self.toolsVerticalContainer.addLayout(self.horizontalLayout)

        self.pushButton.clicked.connect(self.showInfoSig)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.pushButton.setText(_translate("MainWindow", "功能1"))
        self.pushButton_2.setText(_translate("MainWindow", "功能2"))
        self.pushButton_3.setText(_translate("MainWindow", "功能3"))