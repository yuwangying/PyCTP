# -*- coding: utf-8 -*-

"""
Module implementing QLoginForm.
"""
import time
import Utils
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget
from PyQt4 import QtGui, QtCore
import PyQt4
from SocketManager import SocketManager
import socket
import json
import QCTP
import ClientMain
import threading

from Ui_QLogin import Ui_LoginForm


class QLoginForm(QWidget, Ui_LoginForm):
    """
    Class documentation goes here.
    """

    signal_send_msg = QtCore.pyqtSignal(dict)  # 信号：绑定到SocketManager的send_msg函数

    def __init__(self, parent=None):
        """
        Constructor
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QLoginForm, self).__init__(parent)
        self.setupUi(self)

        self.__sockfd = None  # socket_file_description
        self.__socket_manager = None  # SocketManager对象

        self.lineEdit_trader_password.setEchoMode(QtGui.QLineEdit.Password)  # 密码框暗文

    def set_sockfd(self, socket_file_description):
        self.__sockfd = socket_file_description

    def set_SocketManager(self, obj_sm):
        self.__socket_manager = obj_sm

    def get_SocketManager(self):
        return self.__socket_manager

    def set_QCTP(self, obj_QCTP):
        self.__q_ctp = obj_QCTP

    def get_QCTP(self):
        return self.__q_ctp
    
    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager
    
    def get_CTPManager(self):
        return self.__ctp_manager

    def set_QAccountWidget(self, obj_QAccountWidget):
        self.__QAccountWidget = obj_QAccountWidget

    def set_dict_QAccountWidget(self, dict_QAccountWidget):
        self.dict_QAccountWidget = dict_QAccountWidget

    def set_QOrderWidget(self, obj_QOrderWidget):
        self.__QOrderWidget = obj_QOrderWidget

    def set_ClientMain(self, obj_ClientMain):
        self.__client_main = obj_ClientMain

    def get_ClientMain(self):
        return self.__client_main

    def closeEvent(self, QCloseEvent):
        print(">>> QLogin.closeEvent() ")
        # self.widget_QAccountWidget.get_SocketManager().set_recive_msg_flag(False)
        QtCore.QCoreApplication.instance().quit()

    # 自定义槽
    @pyqtSlot(str)
    def slot_SendMsg(self, msg):
        # print("QLogin.slot_SendMsg()", msg)
        # send json to server
        self.__socket_manager.send_msg(msg)
    
    @pyqtSlot()
    def on_pushButton_login_clicked(self):
        thread = threading.current_thread()
        print("QLogin.on_pushButton_login_clicked() thread.getName()=", thread.getName())
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.pushButton_login.setEnabled(False)  # 点击后按钮灰显不可用，收到登录失败重新激活
        self.__dict_login = {'MsgRef': self.__socket_manager.msg_ref_add(),
                             'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                             'MsgSrc': 0,  # 消息源，客户端0，服务端1
                             'MsgType': 1,  # 消息类型为trader登录验证
                             'TraderID': self.lineEdit_trader_id.text(),
                             'Password': self.lineEdit_trader_password.text()
                             }
        # json_login = json.dumps(self.__dict_login)
        self.signal_send_msg.emit(self.__dict_login)

    # 获得交易员登录信息
    def get_dict_login(self):
        return self.__dict_login
    
    @pyqtSlot()
    def on_pushButton_cancel_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        self.close()
    

    @pyqtSlot(bool)
    def on_checkBox_isoffline_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        print("on_checkBox_isoffline_clicked()", checked)
    
    @pyqtSlot(int)
    def on_checkBox_isoffline_stateChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    Form = QLoginForm()
    Form.show()

    sys.exit(app.exec_())

