from PyQt5.QtWidgets import *
class DataBaseDisplayer(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.InitializeContent()

    def InitializeContent(self):
        self.tablewidget1 = QTableWidget(self)
        self.tablewidget2 = QTableWidget(self)
        self.tablewidget3 = QTableWidget(self)
        
    
