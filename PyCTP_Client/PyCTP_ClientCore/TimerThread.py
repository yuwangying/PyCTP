import time
from PyQt4 import QtCore, QtGui


class TimerThread(QtCore.QThread):

    timeout_signal = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QThread.__init__(self)

    #重写run方法
    def run(self):
      self.timeout_signal.emit()
      while True:
        time.sleep(0.5)
        #发送timeout信号
        self.timeout_signal.emit()
