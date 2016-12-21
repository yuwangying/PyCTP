# -*- coding: utf-8 -*-

from collections import namedtuple
import socket
import sys
import struct
import threading
import json
import queue
from QCTP import QCTP
from QAccountWidget import QAccountWidget
import time
from PyQt4 import QtCore

Message = namedtuple("Message", "head checknum buff")


class SocketManager(QtCore.QThread):

    signal_label_login_error_text = QtCore.pyqtSignal(str)  # 定义信号：设置登录界面的消息框文本
    signal_pushButton_login_set_enabled = QtCore.pyqtSignal(bool)  # 定义信号：登录界面登录按钮设置为可用
    signal_ctp_manager_init = QtCore.pyqtSignal()  # 定义信号：调用CTPManager的初始化方法
    signal_update_strategy = QtCore.pyqtSignal()  # 定义信号：收到服务端收到策略类的回报消息

    def __init__(self, ip_address, port, parent=None):
        # threading.Thread.__init__(self)
        super(SocketManager, self).__init__(parent)
        self.__ip_address = ip_address
        self.__port = port
        self.__sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__event = threading.Event()  # 初始化协程threading.Event()
        self.__msg_ref = 0  # 发送消息引用
        self.__RecvN = True  # RecvN方法运行状态，True正常，False异常
        self.__queue_send_msg = queue.Queue(maxsize=100)  # 创建队列，存储将要发送的消息
        self.__thread_send_msg = threading.Thread(target=self.run_send_msg)  # 创建发送消息线程
        self.__thread_send_msg.start()

    def set_QCTP(self, obj_QCTP):
        self.__q_ctp = obj_QCTP

    def get_QCTP(self):
        return self.__q_ctp

    def set_QLogin(self, obj_QLogin):
        self.__q_login = obj_QLogin

    def get_QLogin(self):
        return self.__q_login

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

    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager

    def get_CTPManager(self):
        return self.__ctp_manager
    
    def set_ClientMain(self, obj_ClientMain):
        self.__client_main = obj_ClientMain
        
    def get_QClientMain(self):
        return self.__client_main

    # 设置交易员id
    def set_trader_id(self, str_TraderID):
        self.__trader_id = str_TraderID

    # 获得交易员id
    def get_trader_id(self):
        return self.__trader_id

    def set_trader_name(self, str_TraderName):
        self.__trader_name = str_TraderName

    def get_trader_name(self):
        return self.__trader_name

    def set_list_market_info(self, list_input):
        self.__list_market_info = list_input

    def get_list_market_info(self):
        return self.__list_market_info

    def set_list_user_info(self, list_input):
        self.__list_user_info = list_input

    def get_list_user_info(self):
        return self.__list_user_info

    def set_list_algorithm_info(self, list_input):
        self.__list_algorithm_info = list_input

    def get_list_algorithm_info(self):
        return self.__list_algorithm_info

    def set_list_strategy_info(self, list_input):
        self.__list_strategy_info = list_input
        
    def get_list_strategy_info(self):
        return self.__list_strategy_info

    def set_list_yesterday_position(self, list_input):
        self.__list_yesterday_position = list_input

    def get_list_yesterday_position(self):
        return self.__list_yesterday_position

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
            checknum = ((checknum + ord(i)) % 255)
        return checknum

    # 向socket服务端发送数据
    @QtCore.pyqtSlot(str)
    def send_msg_to_server(self, buff):  # sockfd为socket套接字，buff为消息体json数据
        # 构造Message
        m = Message("gmqh_sh_2016", 0, buff)

        # 数据发送前,将校验数据填入Message结构体
        checknum = self.msg_check(m)
        m = Message("gmqh_sh_2016", checknum, buff)
        # print("send m.buff = ", m.buff.encode())
        # print("send m.checknum = ", m.checknum)
        # 打包数据(13位的head,1位校验码,不定长数据段)
        data = struct.pack(">13s1B" + str(len(m.buff.encode()) + 1) + "s", m.head.encode(), m.checknum, m.buff.encode())

        print("SocketManager.slot_send_msg()", data)
        try:
            size = self.__sockfd.send(data)  # 发送数据
        except socket.timeout as e:
            print("SocketManager.slot_send_msg()", e)
        self.__event.clear()
        return size if self.__event.wait(2.0) else -1

    # 将发送消息加入队列
    @QtCore.pyqtSlot(str)
    def slot_send_msg(self, buff):
        # thread = threading.current_thread()
        # print(">>> SocketManager.run() thread.getName()=", thread.getName())
        self.__queue_send_msg.put_nowait(buff)

    # 接收消息线程
    def run(self):
        # thread = threading.current_thread()
        # print(">>> SocketManager.run() thread.getName()=", thread.getName())
        while True:
            # 收消息
            if self.__RecvN:  # RecvN状态正常
                try:
                    # 接收数据1038个字节(与服务器端统一:13位head+1位checknum+1024数据段)
                    # data = self.__sockfd.recv(30 * 1024 + 14)
                    data = self.RecvN(self.__sockfd, 30 * 1024 + 14)
                except socket.error as e:
                    print(e)

                # 解包数据
                if data is not None:
                    # return
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
                        self.receive_msg(dict_buff)
                        if dict_buff['MsgRef'] == self.__msg_ref:  # 收到服务端发送的收到消息回报
                            self.__event.set()
                    else:
                        print("SocketManager.run() 接收到的数据有误", m.buff)
                        continue

    # 发送消息线程
    def run_send_msg(self):
        thread = threading.current_thread()
        print(">>> SocketManager.run_send_msg() thread.getName()=", thread.getName())
        # 发消息
        while True:
            if self.__queue_send_msg.qsize() > 0:
                tmp_msg = self.__queue_send_msg.get_nowait()
                if tmp_msg is not None:
                    self.send_msg_to_server(tmp_msg)

    # 处理收到的消息
    def receive_msg(self, buff):
        # 消息源MsgSrc值：0客户端、1服务端
        if buff['MsgSrc'] == 0:  # 由客户端发起的消息类型
            # 内核初始化未完成
            if self.__ctp_manager.get_init_finished() is False:
                if buff['MsgType'] == 1:  # 交易员登录验证，MsgType=1
                    print("SocketManager.slot_send_msg() MsgType=1", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 验证通过
                        self.signal_label_login_error_text.emit('登陆成功，初始化中...')
                        self.set_trader_name(buff['TraderName'])
                        self.set_trader_id(buff['TraderID'])
                        self.__client_main.set_trader_name(buff['TraderName'])
                        self.__client_main.set_trader_id(buff['TraderID'])
                        self.__ctp_manager.set_trader_name(buff['TraderName'])
                        self.__ctp_manager.set_trader_id(buff['TraderID'])
                        self.qry_market_info()  # 查询行情配置
                    elif buff['MsgResult'] == 1:  # 验证不通过
                        self.signal_label_login_error_text.emit(buff['MsgErrorReason'])  # 界面显示错误消息
                        self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
                elif buff['MsgType'] == 4:  # 查询行情配置，MsgType=4
                    print("SocketManager.slot_send_msg() MsgType=4", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.signal_label_login_error_text.emit('查询行情配置成功')
                        self.__ctp_manager.set_list_market_info(buff['Info'])  # 将行情信息设置为ctp_manager的属性
                        self.set_list_market_info(buff['Info']) 
                        self.qry_user_info()  # 查询期货账户
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        self.signal_label_login_error_text.emit(buff['MsgErrorReason'])  # 界面显示错误消息
                        self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
                elif buff['MsgType'] == 2:  # 查询期货账户，MsgType=2
                    print("SocketManager.slot_send_msg() MsgType=2", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.signal_label_login_error_text.emit('查询期货账户成功')
                        self.__ctp_manager.set_list_user_info(buff['Info'])  # 将期货账户信息设置为ctp_manager的属性
                        self.set_list_user_info(buff['Info'])
                        self.qry_algorithm_info()  # 查询下单算法
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        self.signal_label_login_error_text.emit(buff['MsgErrorReason'])  # 界面显示错误消息
                        self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
                elif buff['MsgType'] == 11:  # 查询下单算法编号，MsgType=11
                    print("SocketManager.slot_send_msg() MsgType=11", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.signal_label_login_error_text.emit('查询下单算法成功')
                        self.set_list_algorithm_info(buff['Info'])
                        self.qry_strategy_info()  # 查询策略信息
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        self.signal_label_login_error_text.emit(buff['MsgErrorReason'])  # 界面显示错误消息
                        self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
                elif buff['MsgType'] == 3:  # 查询策略，MsgType=3
                    print("SocketManager.slot_send_msg() MsgType=3", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.signal_label_login_error_text.emit('查询策略成功')
                        self.set_list_strategy_info(buff['Info'])
                        self.qry_yesterday_position()  # 查询策略昨仓
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        self.signal_label_login_error_text.emit(buff['MsgErrorReason'])  # 界面显示错误消息
                        self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
                elif buff['MsgType'] == 10:  # 查询策略昨仓，MsgType=10
                    print("SocketManager.slot_send_msg() MsgType=10", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.signal_label_login_error_text.emit('查询策略昨仓成功')
                        self.set_list_yesterday_position(buff['Info'])  # 所有策略昨仓的list
                        self.signal_ctp_manager_init.emit()  # 调用CTPManager的初始化方法
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        self.signal_label_login_error_text.emit(buff['MsgErrorReason'])  # 界面显示错误消息
                        self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            # 内核初始化完成
            elif self.__ctp_manager.get_init_finished():
                if buff['MsgType'] == 3:  # 查询策略，MsgType=3
                    print("SocketManager.slot_send_msg() MsgType=3", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listStrategyInfoOnce = buff['Info']  # 转存策略信息到本类的属性里(单次查询)
                        # 遍历查询到的消息结果列表
                        for i_Info in self.__listStrategyInfoOnce:
                            # 遍历策略对象列表，将服务器查询到的策略参数传递给策略，并调用set_arguments方法更新内核参数值
                            for i_strategy in self.__ctp_manager.get_list_strategy():
                                if i_Info['user_id'] == i_strategy.get_user_id() and i_Info['strategy_id'] == i_strategy.get_strategy_id():
                                    i_strategy.set_arguments(i_Info)  # 将查询参数结果设置到策略内核，所有的策略
                                    self.signal_UI_update_strategy.emit(
                                        i_strategy)  # 更新策略在界面显示，（槽绑定到所有窗口对象槽函数update_strategy）
                                    break
                        self.signal_pushButton_query_strategy_setEnabled.emit(True)  # 收到消息后将按钮激活
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=3 查询策略失败")
                elif buff['MsgType'] == 6:  # 新建策略，MsgType=6
                    print("SocketManager.slot_send_msg() MsgType=6", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.get_CTPManager().create_strategy(buff['Info'][0])  # 内核创建策略对象
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() ", buff['MsgErrorReason'])
                elif buff['MsgType'] == 5:  # 修改策略参数，MsgType=5
                    print("SocketManager.slot_send_msg() MsgType=5", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        for i_strategy in self.__ctp_manager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] \
                                    and i_strategy.get_strategy_id() == buff['StrategyID']:
                                i_strategy.set_arguments(buff['Info'][0])
                                # self.signal_UI_update_strategy.emit(i_strategy)  # 更新策略在界面显示，（槽绑定到所有窗口对象槽函数update_strategy）
                            break
                            # for i_widget in self.__list_QAccountWidget:
                            #     i_widget.update_groupBox_trade_args_for_set()  # 更新策略参数框goupBox
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=5 修改策略参数失败")
                elif buff['MsgType'] == 12:  # 修改策略持仓，MsgType=12
                    print("SocketManager.slot_send_msg() MsgType=12", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        # 更新内核中的策略持仓
                        for i_strategy in self.__ctp_manager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] \
                                    and i_strategy.get_strategy_id() == buff['StrategyID']:
                                i_strategy.set_position(buff['Info'][0])
                            break
                        self.signal_pushButton_set_position_setEnabled.emit()  # 激活设置持仓按钮，禁用仓位输入框
                        pass
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=12 修改策略持仓失败")
                elif buff['MsgType'] == 7:  # 删除策略，MsgType=7
                    print("SocketManager.slot_send_msg() MsgType=7", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        dict_args = {'user_id': buff['UserID'], 'strategy_id': buff['StrategyID']}
                        self.__ctp_manager.delete_strategy(dict_args)
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=7 删除策略失败")
                elif buff['MsgType'] == 13:  # 修改策略交易开关
                    print("SocketManager.slot_send_msg() MsgType=13", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        for i_strategy in self.__ctp_manager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] and i_strategy.get_strategy_id() == buff[
                                'StrategyID']:
                                i_strategy.set_on_off(buff['OnOff'])  # 更新内核中策略开关
                                # self.signal_update_strategy.emit(i_strategy)  # 更新策略在界面显示
                                # self.get_clicked_item().setFlags(self.get_clicked_item().flags() ^ (QtCore.Qt.ItemIsEnabled))
                                break
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=13 修改策略交易开关失败")
                elif buff['MsgType'] == 14:  # 修改策略只平开关
                    print("SocketManager.slot_send_msg() MsgType=14", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        for i_strategy in self.__ctp_manager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] and i_strategy.get_strategy_id() == buff[
                                'StrategyID']:
                                i_strategy.set_only_close(buff['OnOff'])  # 更新内核中策略只平开关
                                # self.signal_update_strategy.emit(i_strategy)  # 更新策略在界面显示
                                # self.get_clicked_item().setFlags(self.get_clicked_item().flags() ^ (QtCore.Qt.ItemIsEnabled))
                                break
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=14 修改策略只平开关失败")
                elif buff['MsgType'] == 8:  # 修改交易员开关
                    print("SocketManager.slot_send_msg() MsgType=8", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        # 更新界面
                        for i_widget in self.__list_QAccountWidget:
                            if i_widget.get_widget_name() == "总账户":
                                self.get_CTPManager().set_on_off(buff['OnOff'])  # 设置内核值
                                # 界面按钮文字显示
                                # if buff['OnOff'] == 1:
                                #     i_widget.pushButton_start_strategy.setText("停止策略")
                                # elif buff['OnOff'] == 0:
                                #     i_widget.pushButton_start_strategy.setText("开始策略")
                                # i_widget.pushButton_start_strategy.setEnabled(True)  # 解禁按钮setEnabled
                                break
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=8 修改交易员开关失败")
                elif buff['MsgType'] == 9:  # 修改期货账户开关
                    print("SocketManager.slot_send_msg() MsgType=9", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        # 更新界面
                        for i_widget in self.__list_QAccountWidget:
                            if i_widget.get_widget_name() == buff['UserID']:
                                # 设置内核设值
                                for i_user in self.get_CTPManager().get_list_user():
                                    if i_user.get_user_id().decode() == buff['UserID']:
                                        i_user.set_on_off(buff['OnOff'])
                                # 界面按钮文字显示
                                # if buff['OnOff'] == 1:
                                #     i_widget.pushButton_start_strategy.setText("停止策略")
                                # elif buff['OnOff'] == 0:
                                #     i_widget.pushButton_start_strategy.setText("开始策略")
                                # i_widget.pushButton_start_strategy.setEnabled(True)  # 解禁按钮
                                break
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("SocketManager.slot_send_msg() MsgType=9 修改期货账户开关失败")
        elif buff['MsgSrc'] == 1:  # 由服务端发起的消息类型
            pass

    # 查询行情信息
    def qry_market_info(self):
        dict_qry_market_info = {'MsgRef': self.msg_ref_add(),
                                'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                'MsgType': 4,  # 查询行情信息
                                'TraderID': self.__trader_id
                                }
        json_qry_market_info = json.dumps(dict_qry_market_info)
        self.slot_send_msg(json_qry_market_info)

    # 查询期货账户信息
    def qry_user_info(self):
        dict_qry_user_info = {'MsgRef': self.msg_ref_add(),
                              'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                              'MsgSrc': 0,  # 消息源，客户端0，服务端1
                              'MsgType': 2,  # 查询期货账户
                              'TraderID': self.__trader_id,
                              'UserID': ''
                              }
        json_qry_user_info = json.dumps(dict_qry_user_info)
        self.slot_send_msg(json_qry_user_info)

    # 查询下单算法
    def qry_algorithm_info(self):
        dict_qry_algorithm_info = {'MsgRef': self.msg_ref_add(),
                                   'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                   'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                   'MsgType': 11,  # 查询期货账户
                                   'TraderID': self.__trader_id,
                                   }
        json_qry_algorithm_info = json.dumps(dict_qry_algorithm_info)
        self.slot_send_msg(json_qry_algorithm_info)

    # 查询策略
    def qry_strategy_info(self):
        dict_qry_strategy_info = {'MsgRef': self.msg_ref_add(),
                                  'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                  'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                  'MsgType': 3,  # 查询策略
                                  'TraderID': self.__trader_id,
                                  'UserID': '',
                                  'StrategyID': ''
                                  }
        json_qry_strategy_info = json.dumps(dict_qry_strategy_info)
        self.slot_send_msg(json_qry_strategy_info)

    # 查询策略昨仓
    def qry_yesterday_position(self):
        dict_qry_yesterday_position = {
            'MsgRef': self.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 10,  # 查询策略昨仓
            'TraderID': self.__trader_id,
            'UserID': ""  # self.__user_id, 键值为空时查询所有UserID的策略
        }
        json_qry_yesterday_position = json.dumps(dict_qry_yesterday_position)
        self.slot_send_msg(json_qry_yesterday_position)


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
        sm = socket_manager.slot_send_msg(buff)
        if sm < 0:
            print("sm=", sm)
            print("buff=", buff)
            print("send msg error")
            print("socket error")


