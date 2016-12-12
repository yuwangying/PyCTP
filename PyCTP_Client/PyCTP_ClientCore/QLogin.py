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

from Ui_QLogin import Ui_LoginForm


class QLoginForm(QWidget, Ui_LoginForm):
    """
    Class documentation goes here.
    """

    Signal_SendMsg = QtCore.pyqtSignal(str)  # 自定义信号

    def __init__(self, parent=None):
        """
        Constructor
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QLoginForm, self).__init__(parent)
        self.setupUi(self)

        self.Signal_SendMsg.connect(self.slot_SendMsg)  # 绑定信号、槽函数

        self.__sockfd = None  # socket_file_description
        self.__sm = None  # SocketManager对象

    """
    def set_login_message(self, str_buff):
        print("set_login_message(self, str_buff):json_buff=", type(str_buff), str_buff)
        dict_buff = eval(str_buff)  # str to dict
        if not isinstance(dict_buff, dict):
            print("QLogin.set_login_message() 客户端收到的消息转换成dict出错")
            return
        if 'MsgResult' not in dict_buff:
            print("QLogin.set_login_message() 客户端收到的消息中不包含字段MsgResult")
            return
        if dict_buff['MsgResult'] == 0:  # 服务端返回登录成功消息
            self.label_login_error.setText("登录成功")
            #self.setVisible(False)
        elif dict_buff['MsgResult'] == 1:  # 服务端发挥登录失败消息
            self.label_login_error.setText("登录失败")
            self.label_login_error.setText(dict_buff['MsgErrorReason'])
            self.pushButton_login.setEnabled(True)  # 激活登录按钮，可以重新登录
    """

    def set_sockfd(self, socket_file_description):
        self.__sockfd = socket_file_description

    def set_SocketManager(self, obj_sm):
        self.__sm = obj_sm

    def get_SocketManager(self):
        return self.__sm

    def set_QCTP(self, obj_QCTP):
        self.__QCTP = obj_QCTP

    def get_QCTP(self):
        return self.__QCTP

    def set_QAccountWidget(self, obj_QAccountWidget):
        self.__QAccountWidget = obj_QAccountWidget

    def set_dict_QAccountWidget(self, dict_QAccountWidget):
        self.dict_QAccountWidget = dict_QAccountWidget

    def set_QOrderWidget(self, obj_QOrderWidget):
        self.__QOrderWidget = obj_QOrderWidget

    def set_QClientMain(self, qclientmain):
        self.__QClientMain = qclientmain

    # 自定义槽
    @pyqtSlot(str)
    def slot_SendMsg(self, msg):
        # print("QLogin.slot_SendMsg()", msg)
        # send json to server
        self.__sm.send_msg(msg)
    
    @pyqtSlot()
    def on_pushButton_login_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet

        self.pushButton_login.setEnabled(False)  # 点击后按钮灰显不可用，收到登录失败重新激活

        # 未勾选脱机登录
        if self.checkBox_isoffline.checkState() == PyQt4.QtCore.Qt.Unchecked:
            print("on_pushButton_login_clicked() 未勾选脱机登录")
            # stockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket套接字

            if not self.__sm:
                sm = SocketManager("10.0.0.28", 8888)  # 创建SocketManager实例，公司网络ip"10.0.0.37"，家里网络ip"192.168.5.17"
                sm.connect()
                sm.start()
                self.set_SocketManager(sm)  # SocketManager对象设置为QLoginForm对象的属性
                sm.set_ClientMain(self.__QClientMain)
                # self.__QClientMain.set_SocketManager(sm)  # SocketManager对象设置为QClientMain对象的属性
                self.__QClientMain.set_QLoginForm(self)  # QLoginForm对象设置为QClientMain对象的属性
                self.__QClientMain.set_QCTP(self.get_QCTP())  # QCTP对象设置为QClientMain对象的属性
                self.__QClientMain.set_SocketManager(sm)  # sm(SoketManager)对象设置为QClientMain对象的属性
                # 绑定信号:sm的signal_send_message到ClientMain.slot_output_message
                # sm.signal_send_message.connect(self.__QClientMain.slot_output_message)
                sm.set_QLogin(self)  # QLoginForm对象设置为SocketManager对象的属性

            self.__dict_login = {'MsgRef': self.__sm.msg_ref_add(),
                          'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                          'MsgSrc': 0,  # 消息源，客户端0，服务端1
                          'MsgType': 1,  # 消息类型为trader登录验证
                          'TraderID': self.lineEdit_trader_id.text(),
                          'Password': self.lineEdit_trader_password.text()
                          }

            json_login = json.dumps(self.__dict_login)
            self.Signal_SendMsg.emit(json_login)
        # 勾选脱机登录
        elif self.checkBox_isoffline.checkState() == PyQt4.QtCore.Qt.Checked:
            pass

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

