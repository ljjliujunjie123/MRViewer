from PyQt5.QtCore import pyqtSignal,QThread,QTimer
import time

class CycleSyncThread(QThread):

    signal = pyqtSignal()
    def __init__(self,interval):
        super(CycleSyncThread,self).__init__()
        self.interval = interval

    def run(self):
        while( not self.isInterruptionRequested()):
            self.signal.emit()
            time.sleep(self.interval)
        print("线程退出成功")