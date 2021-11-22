import sys
from ui.LJJMainWindow import LJJMainWindow
from ui.FileFolderWindow import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = LJJMainWindow()
    sys.exit(app.exec_())

