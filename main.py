import sys
from PyQt5.QtWidgets import QApplication
from ui.LJJMainWindow import LJJMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = LJJMainWindow()
    sys.exit(app.exec_())

