from PyQt5.QtCore import pyqtSignal,QThread
import time

class CycleSyncThread(QThread):

    signal = pyqtSignal(int)
    def __init__(self,interval):
        super(CycleSyncThread,self).__init__()
        self.interval = interval

    def run(self):
        while( not self.isInterruptionRequested()):
            self.signal.emit(1)
            time.sleep(self.interval)