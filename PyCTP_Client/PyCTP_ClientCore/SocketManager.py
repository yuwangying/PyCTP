# -*- coding: utf-8 -*-

from collections import namedtuple
import socket
import sys
import struct
import threading
from QCTP import QCTP
from QAccountWidget import QAccountWidget
import time
from PyQt4 import QtCore

Message = namedtuple("Message", "head checknum buff")


class SocketManager(QtCore.QThread):

    #定义一个发送消息的信号
    signal_send_message = QtCore.pyqtSignal(dict)


    def __init__(self, ip_address, port, parent = None):
        # threading.Thread.__init__(self)
        super(SocketManager, self).__init__(parent)
        self.__ip_address = ip_address
        self.__port = port
        self.__sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__event = threading.Event()  # 初始化协程threading.Event()
        self.__msg_ref = 0  # 发送消息引用
        self.__RecvN = True  # RecvN方法运行状态，True正常，False异常

    def set_ClientMain(self, obj_ClientMain):
        self.__ClientMain = obj_ClientMain

    def set_QCTP(self, obj_QCTP):
        self.__QCTP = obj_QCTP

    def get_QCTP(self):
        return self.__QCTP

    def set_QLogin(self, obj_QLogin):
        self.__QLogin = obj_QLogin

    def get_QLogin(self):
        return self.__QLogin

    def set_QAccountWidget(self, obj_QAccountWidget):
        self.__QAccountWidget = obj_QAccountWidget

    def get_QAccountWidget(self):
        return self.__QAccountWidget

    def set_QOrderWidget(self, obj_QOrderWidget):
        self.__QOrderWidget = obj_QOrderWidget

    def get_QOrderWidget(self):
        return self.__QOrderWidget

    def get_sockfd(self):
        return self.__sockfd

    def get_msg_ref(self):
        return self.__msg_ref

    def msg_ref_add(self):
        self.__msg_ref += 1
        return self.__msg_ref

    # 连接服务器
    def connect(self):
        # 创建socket套接字
        if self.__sockfd:
            # 连接服务器: IP,port
            try:
                # 进行与服务端的连接(ip地址根据实际情况进行更改)
                self.__sockfd.connect((self.__ip_address, self.__port))
            except socket.error as e:
                print("SocketManager.connect() socket error", e)
                sys.exit(1)

    # ------------------------------------------------------
    # RecvN
    #     recv N bytes to target
    # ------------------------------------------------------
    def RecvN(self, socketd, n):
        totalContent = b''
        totalRecved = 0
        while totalRecved < n:
            try:
                onceContent = socketd.recv(n - totalRecved)
                # self.__RecvN = True
            except socket.error as e:
                self.__RecvN = False
                print("SocketManager.RecvN()", e, n, totalRecved)
                return None
            # print("onceContent", onceContent)
            totalContent += onceContent
            totalRecved = len(totalContent)

        return totalContent

    # 计算校验码
    def msg_check(self, message):
        # 将收到的head以及buff分别累加 % 255
        checknum = 0
        for i in message.head:
            # print("i1 = %c \n" % i)
            checknum = ((checknum + ord(i)) % 255)
            # print("i1 checknum = %d \n" % checknum)
        # for i in message.buff:
        #     # print("i2 = %c \n" %i)
        #     checknum = ((checknum + ord(i)) % 255)
        #     # print("i2 checknum = %d \n" % checknum)
        return checknum

    # 发送数据
    @QtCore.pyqtSlot(str)
    def send_msg(self, buff):  # sockfd为socket套接字，buff为消息体json数据
        # 构造Message
        m = Message("gmqh_sh_2016", 0, buff)

        # 数据发送前,将校验数据填入Message结构体
        checknum = self.msg_check(m)
        m = Message("gmqh_sh_2016", checknum, buff)

        # print("send m.buff = ", m.buff.encode())
        # print("send m.checknum = ", m.checknum)
        # 打包数据(13位的head,1位校验码,不定长数据段)
        data = struct.pack(">13s1B" + str(len(m.buff.encode()) + 1) + "s", m.head.encode(), m.checknum, m.buff.encode())

        print("SocketManager.send_msg()", data)
        """
        try:
            buf = s.recv(2048)
            except socket.error, e:
            print "Error receiving data: %s" % e
            sys.exit(1)
        try:
            s.send("Hello, World!")
            ...
        except socket.timeout:
            # whatever you need to do when the connection is dropped

        """
        try:
            size = self.__sockfd.send(data)  # 发送数据
        except socket.timeout as e:
            print("SocketManager.send_msg()", e)
        self.__event.clear()
        return size if self.__event.wait(2.0) else -1

        # self.__rsp_Connect['event'].clear()
        # return 0 if self.__rsp_Connect['event'].wait(self.TIMEOUT) else -4
        # return size

    def run(self):
        thread = threading.current_thread()
        print(">>> SocketManager.run() thread.getName()=", thread.getName())

        while True:
            if self.__RecvN:  # RecvN状态正常
                try:
                    # 接收数据1038个字节(与服务器端统一:13位head+1位checknum+1024数据段)
                    # data = self.__sockfd.recv(30 * 1024 + 14)
                    data = self.RecvN(self.__sockfd, 30 * 1024 + 14)
                except socket.error as e:
                    print(e)

                # 解包数据
                if data is None:
                    return
                head, checknum, buff = struct.unpack(">13s1B" + str(len(data) - 14) + "s", data)
                # print(head, checknum, buff, '\n')
                # 将解包的数据封装为Message结构体
                m = Message(head.decode().split('\x00')[0], checknum, buff.decode())
                tmp_checknum = self.msg_check(m)
                m = Message(head.decode().split('\x00')[0], tmp_checknum, buff.decode().split('\x00')[0])

                # 将收到的标志位与收到数据重新计算的标志位进行对比+head内容对比
                if (m.checknum == checknum) and (m.head == "gmqh_sh_2016"):
                    # 打印接收到的数据
                    dict_buff = eval(m.buff)  # str to dict
                    # print("SocketManager.run() 调用self.signal_send_message.emit(dict_buff)之前")
                    self.signal_send_message.emit(dict_buff)
                    # print("SocketManager.run() 调用self.signal_send_message.emit(dict_buff)之后")
                    # time.sleep(5.0)
                    if dict_buff['MsgRef'] == self.__msg_ref:  # 收到服务端发送的收到消息回报
                        self.__event.set()
                        print("SocketManager.run() 收到数据，解除收发数据协程锁")
                else:
                    print("SocketManager.run() 接收到的数据有误", m.buff)
                    continue


    """
    # 消息处理函数
    def handle_message(dict_buff):
        if not isinstance(dict_buff, dict):
            print("QLogin.set_login_message() 客户端收到的消息转换成dict出错")
            return False
        if 'MsgResult' not in dict_buff:
            print("QLogin.set_login_message() 客户端收到的消息中不包含字段MsgResult")
            return False

        # 处理trader登录验证消息
        if dict_buff['MsgType'] == 4:
            if dict_buff['MsgResult'] == 0:  # 服务端返回登录成功消息
                q_ctp = QCTP()  # 创建最外围的大窗口
                q_login_form.set_QCTP(q_ctp)
                # q_login_form.get_SocketManager().set_QCTP(q_ctp)

                q_account_widget = QAccountWidget()  # 创建账户窗口

                q_ctp.tab_accounts.addTab(q_account_widget, "总账户")  # 账户窗口添加到QCTP窗口的tab

                # self.__QLogin.label_login_error.setText("登录成功")
                # self.__QLogin.get_QCTP().show()
                # self.__QLogin.hide()  # 隐藏登录窗口

                # self.__QCTP.show()

                # q_order_widget = QOrderWidget()  # 创建订单窗口
                # q_login_form.set_QCTP(q_order_widget)
                # q_login_form.get_SocketManager().set_QCTP(q_order_widget)

            elif dict_buff['MsgResult'] == 1:  # 服务端发送登录失败消息
                # self.__QLogin.label_login_error.setText("登录失败")
                # self.__QLogin.label_login_error.setText(dict_buff['MsgErrorReason'])
                # self.__QLogin.pushButton_login.setEnabled(True)  # 激活登录按钮，可以重新登录
                pass
        return True
    """

if __name__ == '__main__':
    # 创建socket套接字
    socket_manager = SocketManager("10.0.0.33", 8888)  # 192.168.5.13
    socket_manager.connect()
    socket_manager.start()

    # 输入提示符
    prompt = b'->'
    while True:
        buff = input(prompt)
        if buff == "":
            continue
        # 发送数据buff
        sm = socket_manager.send_msg(buff)
        if sm < 0:
            print("sm=", sm)
            print("buff=", buff)
            print("send msg error")
            print("socket error")


