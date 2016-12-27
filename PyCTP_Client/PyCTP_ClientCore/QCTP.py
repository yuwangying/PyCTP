# -*- coding: utf-8 -*-

"""
Module implementing QCTP.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QCloseEvent
from PyQt4 import QtCore
from QMessageCenter import MessageCenter


from Ui_QCTP import Ui_MainWindow

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class QCTP(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QCTP, self).__init__(parent)
        self.setupUi(self)

        self.message_center = MessageCenter(self)

        status_bar = QtGui.QStatusBar()  # 创建状态栏
        status_bar.addWidget(self.message_center, stretch=1)  # 设置状态栏格式
        self.setStatusBar(status_bar)

    def set_ClientMain(self, obj_ClientMain):
        self.__client_main = obj_ClientMain

    def get_ClientMain(self):
        return self.__client_main

    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager

    def get_CTPManager(self):
        return self.__ctp_manager

    def set_QLogin(self, obj_QLogin):
        self.__q_login = obj_QLogin

    def get_QLogin(self):
        return self.__q_login

    def set_SocketManager(self, obj_SocketManager):
        self.__socket_manager = obj_SocketManager

    def get_SocketManager(self):
        return self.__socket_manager

    """
    void
    MainWindow::closeEvent(QCloseEvent * event)
    {
        QApplication.quit()
    }
    """

    def closeEvent(self, QCloseEvent):
        print(">>> QCTP closeEvent")
        QtGui.QApplication.quit()
        pass
