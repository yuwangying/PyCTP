# -*- coding: utf-8 -*-

import os
from collections import namedtuple
import socket
import copy
import sys
import struct
import threading
import json
import queue
from MessageBox import MessageBox
from MarketManager import MarketManagerForUi
import time
from PyQt4 import QtCore, QtGui
from multiprocessing import Process, Queue  #, Manager, Value, Array, Pipe
from User import User
from xml.dom import minidom
# import copy
# from QCTP import QCTP
# from QAccountWidget import QAccountWidget

Message = namedtuple("Message", "head checknum buff")


# 创建user(期货账户)
def static_create_user_process(dict_user_info, Queue_main, Queue_user):
    # print("SocketManager.static_create_user_process dict_user_info =", dict_user_info['server']['user_info']['userid'])
    user_id = dict_user_info['server']['user_info']['userid']

    # 标准输出重定向
    # log_directory = 'log/' + user_id + '.log'
    # sys.stdout = open(log_directory, 'w')
    #
    # error_log_directory = 'log/' + user_id + '_error.log'
    # sys.stderr = open(error_log_directory, 'w')

    # print("static_create_user_process() dict_user_info =", dict_user_info)
    # print("static_create_user_process() user_id =", dict_user_info['userid'], ", process_id =", os.getpid(), ", dict_user_info =", dict_user_info)
    # ClientMain.socket_manager.signal_label_login_error_text.emit('创建User', dict_user_info['server']['user_info']['userid'])
    obj_user = User(dict_user_info, Queue_main, Queue_user)
    while True:
        dict_data = Queue_main.get()  # user进程get数据
        obj_user.handle_Queue_get(dict_data)  # user进程get到数据之后的处理


class SocketManager(QtCore.QThread):

    signal_label_login_error_text = QtCore.pyqtSignal(str)  # 定义信号：设置登录界面的消息框文本
    signal_pushButton_login_set_enabled = QtCore.pyqtSignal(bool)  # 定义信号：登录界面登录按钮设置为可用
    signal_ctp_manager_init = QtCore.pyqtSignal()  # 定义信号：调用CTPManager的初始化方法
    signal_update_strategy = QtCore.pyqtSignal()  # 定义信号：收到服务端收到策略类的回报消息
    signal_restore_groupBox = QtCore.pyqtSignal()  # 定义信号：收到查询策略信息后出发信号 -> groupBox界面状态还原（激活查询按钮、恢复“设置持仓”按钮）
    signal_q_ctp_show = QtCore.pyqtSignal()  # 定义信号：收到查询策略信息后出发信号 -> groupBox界面状态还原（激活查询按钮、恢复“设置持仓”按钮）
    signal_QAccountWidget_addTabBar = QtCore.pyqtSignal(str)  # 定义信号：SocketManager发出信号 -> QAccountWidget创建tabBar
    signal_init_tableWidget = QtCore.pyqtSignal(list)  # 定义信号：SocketManager发出信号 -> QAccountWidget初始化tableWidget
    signal_create_QNewStrategy = QtCore.pyqtSignal()  # 定义信号：SocketManager发出信号 -> QAccountWidget创建“新建策略”窗口
    signal_insert_strategy = QtCore.pyqtSignal(dict)  # 定义信号：SocketManager发出信号 -> QAccountWidget界面插入一行策略
    signal_QNewStrategy_hide = QtCore.pyqtSignal()  # 定义信号：SocketManager发出信号 -> QNewStrategy“新建策略窗口”隐藏
    # signal_set_data_list = QtCore.pyqtSignal(list)  # 定义信号:SocketManager发出信号 -> QAccountWidget接收tableView数据模型,并刷新界面
    signal_update_panel_show_account = QtCore.pyqtSignal(list)  # 定义信号：SocketManger收到进程通信user进程发来的资金账户信息 -> 向界面发送数据，并更新界面
    signal_activate_query_strategy_pushbutton = QtCore.pyqtSignal()  # 定义信号：SocketManager收到查询策略回报消息 -> 向界面发送信号，激活查询策略按钮
    signal_tab_changed = QtCore.pyqtSignal()  # 定义信号：SocketMananger收到查询策略
    signal_init_ui_on_off = QtCore.pyqtSignal(int)  # 定义信号：SocketManager收到交易员登录成功信息 -> 初始化界面“开始策略”按钮
    signal_update_strategy_on_off = QtCore.pyqtSignal(dict)  # 定义信号：SocketManager收到修改策略开关回报 -> 界面talbeView更新特定的index
    signal_init_groupBox_order_algorithm = QtCore.pyqtSignal(list)  # 定义信号LSocketManger下单算法信息 -> 界面groupBox初始化下单算法选项
    signal_show_message = QtCore.pyqtSignal(list)  # 定义信号显示提示朝窗口 -> 消息弹窗
    signal_setTabIcon = QtCore.pyqtSignal(int)  # Socket收到修改期货账户开关或交易员开关 -> 设置tabbar样式
    signal_init_setTabIcon = QtCore.pyqtSignal()  # Socket收到查询期货账户信息 -> 界面初始化tab样式
    signal_show_alert = QtCore.pyqtSignal(dict)  # 定义信号：显示弹窗
    signal_on_pushButton_set_position_active = QtCore.pyqtSignal()  # 定义信号：激活界面设置持仓按钮

    def __init__(self, parent=None):
        # threading.Thread.__init__(self)
        super(SocketManager, self).__init__(parent)
        self.read_ip_address()  # 读取本地xml文件，获得ip_address
        # self.__ip_address = ip_address
        # self.__port = port
        self.__sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__list_info_group = list()  # 一个消息分为多条发送，临时保存已经接收到的消息

        socket_value = self.__sockfd.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        if socket_value == 0:
            self.__sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.__sockfd.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 3000))# 激活心跳功能，10秒激活时间，频率3秒
        self.__event = threading.Event()  # 初始化协程threading.Event()
        self.__msg_ref = 0  # 发送消息引用
        self.__RecvN = True  # RecvN方法运行状态，True正常，False异常
        self.__queue_send_msg = queue.Queue(maxsize=100)  # 创建队列，存储将要发送的socket消息
        self.__thread_send_msg = threading.Thread(target=self.run_send_msg)  # 创建发送socket消息线程
        self.__thread_send_msg.setDaemon(True)  # 设置主线程退出该线程也退出
        self.__thread_send_msg.start()  # 开始线程：发送socket消息线程
        # self.__dict_user_Queue_data = dict()  # 进程间通信，接收到User进程发来的消息，存储结构
        self.__list_instrument_info = list()  # 所有合约信息
        self.__list_update_widget_data = list()  # 向ui发送更新界面信号的数据结构
        self.__dict_table_view_data = dict()  # 保存所有期货账户更新tableView的数据
        self.__dict_panel_show_account_data = dict()  # 保存所有期货账户更新panel_show_account的数据
        self.__dict_tab_index = dict()  #  键名：user_id,键值：tab的index
        self.__clicked_row = -1  # 鼠标点击tableView中的行数，初始值为-1
        self.__clicked_column = -1
        self.__clicked_user_id = ''  # 鼠标点击的策略信息中user_id，初始值为空字符串，界面被点击时修改值
        self.__clicked_strategy_id = ''
        self.__dict_user_process_finished = dict()  # 子进程初始化完成信息
        self.__total_process_finished = False  # 所有进程初始化完成标志位，初始值为False
        self.__dict_user_on_off = dict()  # 期货账户开关信息dict{user_id: 1,}
        self.__recive_msg_flag = False  # 接收socket消息线程运行标志
        self.msg_box = MessageBox()  # 创建消息弹窗
        self.__list_panel_show_account = list()  # 更新界面资金条数据结构# 读取xml文件

        self.__thread_connect = threading.Thread(target=self.connect)
        self.__thread_connect.setDaemon(True)
        self.__thread_connect.start()

    def read_ip_address(self):
        xml_path = "config/trade_server_ip.xml"
        # xml文件不存在跳出
        if os.path.exists(xml_path) is False:
            return
        else:
            self.__xml_exist = True

        # 解析文件employ.xml
        self.__doc_read = minidom.parse(xml_path)
        # 定位到根元素
        self.__root_read = self.__doc_read.documentElement
        NodeList_ip_address = self.__root_read.getElementsByTagName("ip_address")
        # for i in NodeList_ip_address:  # i:Element
        #     ip = i.attributes['ip'].value
        #     port = i.attributes['port'].value
        self.__ip_address = NodeList_ip_address[0].attributes['ip'].value
        self.__port = int(NodeList_ip_address[0].attributes['port'].value)
        print(">>> StocketManager.read_ip_address() ip_address =", self.__ip_address, self.__port)

    def set_XML_Manager(self, obj):
        self.__xml_manager = obj

    def get_XML_Manager(self):
        return self.__xml_manager

    def get_market_manager(self):
        return self.__market_manager_for_ui

    def set_QNewStrategy(self, obj):
        self.__q_new_strategy = obj

    # 程序主窗口
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

    def set_QAlert(self, obj_QAlertBox):
        self.__q_alert_box = obj_QAlertBox

    def get_QAlert(self):
        return self.__q_alert_box

    def get_dict_Queue_main(self):
        return self.__dict_Queue_main

    def get_sockfd(self):
        return self.__sockfd

    def get_msg_ref(self):
        return self.__msg_ref

    def get_dict_tab_index(self):
        return self.__dict_tab_index

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

    def set_trader_on_off(self, int_on_off):
        self.__trader_on_off = int_on_off

    def get_trader_on_off(self):
        return self.__trader_on_off

    # 获得交易员id
    def get_trader_id(self):
        return self.__trader_id

    def set_trader_name(self, str_TraderName):
        self.__trader_name = str_TraderName

    def get_trader_name(self):
        return self.__trader_name

    def set_dict_trader_info(self, dict_input):
        self.__dict_trader_info = dict_input

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

    def set_list_position_detail_for_order(self, list_input):
        for i in list_input:
            i['Direction'] = chr(i['Direction'])
            i['CombOffsetFlag'] = chr(i['CombOffsetFlag'])
            i['CombHedgeFlag'] = chr(i['CombHedgeFlag'])
            i['OrderStatus'] = chr(i['OrderStatus'])
            # print(">>> SocketManager.set_list_position_detail_for_order() i =", i)
        self.__list_position_detail_for_order = list_input

    def get_list_position_detail_for_order(self):
        return self.__list_position_detail_for_order

    def set_list_position_detail_for_trade(self, list_input):
        for i in list_input:
            i['Direction'] = chr(i['Direction'])
            i['OffsetFlag'] = chr(i['OffsetFlag'])
            i['HedgeFlag'] = chr(i['HedgeFlag'])
            # print(">>> SocketManager.set_list_position_detail_for_trade() i =", i)
        self.__list_position_detail_for_trade = list_input

    def get_list_position_detail_for_trade(self):
        return self.__list_position_detail_for_trade

    def set_list_position_detail_for_order_today(self, list_input):
        for i in list_input:
            i['Direction'] = chr(i['Direction'])
            i['CombOffsetFlag'] = chr(i['CombOffsetFlag'])
            i['CombHedgeFlag'] = chr(i['CombHedgeFlag'])
            i['OrderStatus'] = chr(i['OrderStatus'])
            # print(">>> SocketManager.set_list_position_detail_for_order() i =", i)
        self.__list_position_detail_for_order_today = list_input

    def get_list_position_detail_for_order_today(self):
        return self.__list_position_detail_for_order_today

    def set_list_position_detail_for_trade_today(self, list_input):
        for i in list_input:
            i['Direction'] = chr(i['Direction'])
            i['OffsetFlag'] = chr(i['OffsetFlag'])
            i['HedgeFlag'] = chr(i['HedgeFlag'])
            # print(">>> SocketManager.set_list_position_detail_for_trade() i =", i)
        self.__list_position_detail_for_trade_today = list_input

    def get_list_position_detail_for_trade_today(self):
        return self.__list_position_detail_for_trade_today

    def get_dict_user_process_data(self):
        return self.__dict_user_process_data

    def get_list_instrument_info(self):
        return self.__list_instrument_info

    def set_list_instrument_id(self, list_instrument_info):
        self.__list_instrument_id = list()
        for i in list_instrument_info:
            if len(i['InstrumentID']) <= 6:
                self.__list_instrument_id.append(i['InstrumentID'])

    def get_list_instrument_id(self):
        return self.__list_instrument_id

    def set_clicked_info(self, row, column, user_id, strategy_id):
        self.__clicked_row = row
        self.__clicked_column = column
        self.__clicked_user_id = user_id
        self.__clicked_strategy_id = strategy_id

    def get_dict_table_view_data(self):
        return self.__dict_table_view_data

    def get_dict_panel_show_account_data(self):
        return self.__dict_panel_show_account_data

    def get_list_panel_show_account(self):
        return self.__list_panel_show_account

    def get_dict_user_on_off(self):
        return self.__dict_user_on_off

    def get_total_process_finished(self):
        return self.__total_process_finished

    # 接收socket消息线程结束标志位，False结束线程，True运行线程
    def set_recive_msg_flag(self, bool_in):
        self.__recive_msg_flag = bool_in

    # 连接服务器
    def connect(self):
        while self.__recive_msg_flag is False:
            self.__recive_msg_flag = True
            # 创建socket套接字
            if self.__sockfd:
                # 连接服务器: IP,port
                try:
                    print("SocketManager.connect() self.__ip_address", self.__ip_address)
                    # 进行与服务端的连接(ip地址根据实际情况进行更改)
                    self.__sockfd.connect((self.__ip_address, self.__port))
                except socket.error as e:
                    self.__recive_msg_flag = False
                    print("SocketManager.connect() socket error", e)
                    # self.signal_label_login_error_text.emit('登录失败,自动重连')
                    MessageBox().showMessage("错误", "连接服务器失败！")
                    time.sleep(5)
                    # self.connect()
                    # dict_args = {"title": "消息", "main": "连接服务器失败"}
                    # self.signal_show_alert.emit(dict_args)
                    # sys.exit(1)
                finally:
                    if self.__recive_msg_flag is not False:
                        self.__recive_msg_flag = True

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
                MessageBox().showMessage("错误", "接收消息失败！")
                self.__sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__thread_connect.start()
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
            MessageBox().showMessage("错误", "发送消息失败")
            self.__recive_msg_flag = False
            self.__sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__thread_connect.start()
        self.__event.clear()
        return size if self.__event.wait(2.0) else -1

    # 将发送消息加入队列
    @QtCore.pyqtSlot(str)
    def slot_send_msg(self, buff):
        # thread = threading.current_thread()
        # print(">>> SocketManager.run() thread.getName()=", thread.getName())
        self.__queue_send_msg.put(buff)

    # 接收消息线程
    def run(self):
        # thread = threading.current_thread()
        # print(">>> SocketManager.run() thread.getName()=", thread.getName())
        while self.__recive_msg_flag:
            start_time = time.time()
            # 收消息
            if self.__RecvN:  # RecvN状态正常
                try:
                    # 接收数据1038个字节(与服务器端统一:13位head+1位checknum+1024数据段)
                    # data = self.__sockfd.recv(30 * 1024 + 14)
                    data = self.RecvN(self.__sockfd, 2 * 1024 + 14)
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
                        self.receive_part_msg(dict_buff)
                        if dict_buff['MsgRef'] == self.__msg_ref:  # 收到服务端发送的收到消息回报
                            self.__event.set()
                    else:
                        print("SocketManager.run() 接收到的数据有误", m.buff)
                        continue
            # print(">>> SocketManager run() takes time = %s" % (time.time() - start_time))
        print(">>> SocketManager run() stop")

    # 发送消息线程
    def run_send_msg(self):
        # thread = threading.current_thread()
        # print(">>> SocketManager.run_send_msg() thread.getName()=", thread.getName())
        # 发消息
        while True:
            tmp_msg = self.__queue_send_msg.get()
            if tmp_msg is not None:
                self.send_msg_to_server(tmp_msg)

    # 收到部分消息，当IsLast标志位1，收到一条完整的消息
    def receive_part_msg(self, buff):
        if buff['IsLast'] == 0:
            self.__list_info_group.append(buff['Info'][0])
        elif buff['IsLast'] == 1:
            # full_msg = copy.deepcopy(buff)
            if buff['MsgType'] in [1, 8, 9, 13, 14, 18, 19]:
                # self.receive_msg(buff)
                pass
                print(">>> SocketManager.receive_part_msg() IsLast = 1, MsgType =", buff['MsgType'], "full_msg =", buff)
            else:
                if len(buff['Info']) > 0:
                    self.__list_info_group.append(buff['Info'][0])
                buff['Info'] = self.__list_info_group
                self.__list_info_group = list()
                print(">>> SocketManager.receive_part_msg() IsLast = 1，Info长度 =", len(buff['Info']), "MsgType =", buff['MsgType'], "full_msg =", buff)
            self.receive_msg(buff)
        else:
            print(">>> SocketManager.receive_part_msg() IsLast字段异常，buff =", buff)

    # 处理收到的消息
    def receive_msg(self, buff):
        # 消息源MsgSrc值：0客户端、1服务端
        if buff['MsgSrc'] == 0:  # 由客户端发起的消息类型
            # 内核初始化未完成
            # if self.__ctp_manager.get_init_finished() is False:
            if buff['MsgType'] == 1:  # 收到：交易员登录验证，MsgType=1
                print("SocketManager.receive_msg() MsgType=1，交易员登录", buff)
                if buff['MsgResult'] == 0:  # 验证通过
                    self.signal_label_login_error_text.emit('登陆成功')
                    self.set_trader_name(buff['TraderName'])
                    self.set_trader_id(buff['TraderID'])
                    self.set_trader_on_off(buff['OnOff'])
                    self.signal_init_ui_on_off.emit(buff['OnOff'])  # 初始化界面“开始策略”按钮
                    # self.__client_main.set_trader_name(buff['TraderName'])
                    # self.__client_main.set_trader_id(buff['TraderID'])
                    # self.__ctp_manager.set_trader_name(buff['TraderName'])
                    # self.__ctp_manager.set_trader_id(buff['TraderID'])
                    # self.__ctp_manager.set_on_off(buff['OnOff'])
                    # self.qry_market_info()  # 发送：查询行情配置，MsgType=4
                    self.set_dict_trader_info(buff)
                    self.__dict_user_on_off['所有账户'] = buff['OnOff']
                elif buff['MsgResult'] == 1:  # 验证不通过
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 4:  # 收到：查询行情配置，MsgType=4
                print("SocketManager.receive_msg() MsgType=4，查询行情配置", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    # self.__ctp_manager.set_list_market_info(buff['Info'])  # 将行情信息设置为ctp_manager的属性
                    self.set_list_market_info(buff['Info'])
                    self.__market_manager_for_ui = MarketManagerForUi(buff['Info'][0])
                    self.__market_manager_for_ui.set_QAccountWidget(self.__QAccountWidget)  # 窗口对象设置为其属性
                    self.__market_manager_for_ui.signal_update_spread_ui.connect(self.__QAccountWidget.slot_update_spread_ui)
                    # self.qry_user_info()  # 发送：查询期货账户信息，MsgType=2
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 2:  # 收到：查询期货账户信息，MsgType=2
                print("SocketManager.receive_msg() MsgType=2，查询期货账户", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    # self.__ctp_manager.set_list_user_info(buff['Info'])  # 将期货账户信息设置为ctp_manager的属性
                    self.set_list_user_info(buff['Info'])
                    self.__update_ui_user_id = buff['Info'][0]['userid']
                    for i in buff['Info']:
                        user_id = i['userid']
                        self.__dict_user_on_off[user_id] = i['on_off']
                        self.__dict_table_view_data[user_id] = list()  # 初始化更新tableView的数据
                        self.__dict_panel_show_account_data[user_id] = list()  # 初始化更新panel_show_account的数据
                    print(">>> self.__dict_user_on_off =", self.__dict_user_on_off)
                    # print(">>> self.__update_ui_user_id =", self.__update_ui_user_id)
                    # self.qry_algorithm_info()  # 发送：查询下单算法，MsgType=11
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 11:  # 收到：查询下单算法编号，MsgType=11
                print("SocketManager.receive_msg() MsgType=11，查询下单算法", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    self.set_list_algorithm_info(buff['Info'])
                    # self.qry_strategy_info()  # 发送：查询策略信息，MsgType=3
                    self.signal_init_groupBox_order_algorithm.emit(buff['Info'])
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 3:  # 收到：查询策略，MsgType=3
                print("SocketManager.receive_msg() MsgType=3，查询策略", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    self.set_list_strategy_info(buff['Info'])
                    print(">>> ScoketManager.receive_msg() self.signal_init_tableWidget.emit(buff['Info'])")
                    # self.signal_init_tableWidget.emit(buff['Info'])
                    # self.qry_position_detial_for_order()  # 发送：查询持仓明细order，MsgType=15
                    # user进程初始化完成，则将信息转发给user进程
                    if self.__total_process_finished:
                        self.process_communicate_query_strategy(buff['Info'])
                        # self.signal_tab_changed.emit()  # 主动触发一次tab_changed操作，目的更新界面全部元素
                    # self.process_communicate_query_strategy(buff['Info'])
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
                # 收到查询策略回报消息，激活“查询”按钮
                self.signal_activate_query_strategy_pushbutton.emit()
            elif buff['MsgType'] == 15:  # 收到：查询昨持仓明细order，MsgType=15
                print("SocketManager.receive_msg() MsgType=15，查询昨持仓明细order", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    self.set_list_position_detail_for_order(buff['Info'])
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 17:  # 收到：查询昨持仓明细，MsgType=17
                print("SocketManager.receive_msg() MsgType=17，查询昨持仓明细trade", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    self.set_list_position_detail_for_trade(buff['Info'])
                    # self.initialize()  # 初始化，创建user进程
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 20:  # 收到：查询今持仓明细order，MsgType=20
                print("SocketManager.receive_msg() MsgType=20，查询修改持仓时的策略持仓明细order", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    self.set_list_position_detail_for_order_today(buff['Info'])
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 21:  # 收到：查询今持仓明细，MsgType=21
                print("SocketManager.receive_msg() MsgType=21，查询修改持仓时的策略持仓明细trade", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    self.set_list_position_detail_for_trade_today(buff['Info'])
                    self.initialize()  # 初始化，创建user进程
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    self.signal_label_login_error_text.emit(buff['MsgErrorReason'])
                    self.signal_pushButton_login_set_enabled.emit(True)  # 登录按钮激活
            elif buff['MsgType'] == 6:  # 新建策略，MsgType=6
                print("SocketManager.receive_msg() MsgType=6，新建策略", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    # self.__ctp_manager.create_strategy(buff['Info'][0])  # 内核创建策略对象
                    # self.create_strategy(buff['Info'][0])
                    # 进程间通信：main->user
                    user_id = buff['Info'][0]['user_id']  # 策略参数dict
                    # self.signal_insert_strategy.emit(buff['Info'][0])  # 界面中新插入一行策略
                    self.__QAccountWidget.StrategyDataModel.set_update_once(True)  # 设置定时任务中刷新一次全部tableView
                    self.signal_QNewStrategy_hide.emit()  # 隐藏新建策略窗口
                    self.__dict_Queue_main[user_id].put(buff)
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    # print("SocketManager.receive_msg() ", buff['MsgErrorReason'])
                    # MessageBox().showMessage("错误", buff['MsgErrorReason'])
                    dict_args = {"title": "消息", "main": buff['MsgErrorReason']}
                    self.signal_show_alert.emit(dict_args)
            elif buff['MsgType'] == 5:  # 修改策略参数，MsgType=5
                print("SocketManager.receive_msg() MsgType=5，修改策略参数", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    dict_args = buff['Info'][0]  # 策略参数dict
                    user_id = dict_args['user_id']
                    self.__dict_Queue_main[user_id].put(buff)
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    print("SocketManager.receive_msg() MsgType=5 修改策略参数失败")
            elif buff['MsgType'] == 12:  # 修改策略持仓，MsgType=12
                print("SocketManager.receive_msg() MsgType=12，修改策略持仓", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    # # 更新内核中的策略持仓
                    # for i_strategy in self.__ctp_manager.get_list_strategy():
                    #     if i_strategy.get_user_id() == buff['UserID'] \
                    #             and i_strategy.get_strategy_id() == buff['StrategyID']:
                    #         i_strategy.set_position(buff['Info'][0])
                    #         break
                    dict_args = buff['Info'][0]  # 策略参数dict
                    user_id = dict_args['user_id']
                    self.__dict_Queue_main[user_id].put(buff)
                    dict_args = {"title": "消息", "main": "修改策略持仓成功"}
                    self.signal_show_alert.emit(dict_args)
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    print("SocketManager.receive_msg() MsgType=12 修改策略持仓失败")
                    # message_list = ['消息', 'TS：修改策略持仓失败']
                    # self.signal_show_message.emit(message_list)
                    dict_args = {"title": "消息", "main": "错误：修改策略持仓失败"}
                    self.signal_show_alert.emit(dict_args)
                self.signal_on_pushButton_set_position_active.emit()
            elif buff['MsgType'] == 7:  # 删除策略，MsgType=7
                print("SocketManager.receive_msg() MsgType=7，删除策略", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    dict_args = {'user_id': buff['UserID'], 'strategy_id': buff['StrategyID']}
                    # self.__ctp_manager.delete_strategy(dict_args)
                    # {'MsgSendFlag': 1, 'MsgResult': 0, 'MsgErrorReason': '', 'MsgRef': 15, 'UserID': '058176', 'StrategyID': '20', 'MsgType': 7, 'MsgSrc': 0, 'TraderID': '1601'}
                    user_id = buff['UserID']
                    self.__QAccountWidget.StrategyDataModel.set_update_once(True)  # 设置定时任务中刷新一次全部tableView
                    self.__dict_Queue_main[user_id].put(buff)
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    print("SocketManager.receive_msg() MsgType=7 删除策略失败")
            elif buff['MsgType'] == 13:  # 修改策略交易开关
                print("SocketManager.receive_msg() MsgType=13，修改策略交易开关", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    # 进程通信，将消息发给对应的user进程
                    user_id = buff['UserID']
                    self.__dict_Queue_main[user_id].put(buff)
                    # self.__QAccountWidget.StrategyDataModel.set_update_once(True)  # 更新一次全部数据
                    # self.signal_init_ui_on_off.emit(buff)  # 发送信号，更新tableView中特定的index
                    self.__QAccountWidget.set_clicked_strategy_on_off(buff['OnOff'])
                    self.signal_update_strategy_on_off.emit(buff)  # 更新策略开关
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    print("SocketManager.receive_msg() MsgType=13 修改策略交易开关失败")
            # elif buff['MsgType'] == 14:  # 修改策略只平开关
            #     print("SocketManager.receive_msg() MsgType=14，修改策略只平开关", buff)
            #     if buff['MsgResult'] == 0:  # 消息结果成功
            #         for i_strategy in self.__ctp_manager.get_list_strategy():
            #             if i_strategy.get_user_id() == buff['UserID'] \
            #                     and i_strategy.get_strategy_id() == buff['StrategyID']:
            #                 i_strategy.set_only_close(buff['OnOff'])  # 更新内核中策略只平开关
            #                 break
            #     elif buff['MsgResult'] == 1:  # 消息结果失败
            #         print("SocketManager.receive_msg() MsgType=14 修改策略只平开关失败")
            elif buff['MsgType'] == 8:  # 修改交易员开关
                print("SocketManager.receive_msg() MsgType=8，修改交易员开关", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    # self.__ctp_manager.set_on_off(buff['OnOff'])  # 设置内核中交易员开关
                    self.__dict_user_on_off['所有账户'] = buff['OnOff']
                    # print(">>> SocketManager.receive_msg() self.__dict_user_on_off =", self.__dict_user_on_off)
                    for user_id in self.__dict_Queue_main:
                        self.__dict_Queue_main[user_id].put(buff)  # 将修改交易员开关回报发送给所有user进程
                    self.signal_setTabIcon.emit(buff['OnOff'])
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    print("SocketManager.receive_msg() MsgType=8 修改交易员开关失败")
            elif buff['MsgType'] == 9:  # 修改期货账户开关
                print("SocketManager.receive_msg() MsgType=9，修改期货账户开关", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    user_id = buff['UserID']
                    self.__dict_user_on_off[user_id] = buff['OnOff']
                    # print(">>> SocketManager.receive_msg() self.__dict_user_on_off =", self.__dict_user_on_off)
                    self.__dict_Queue_main[user_id].put(buff)  # 将修改期货账户开关回报发送给user进程
                    # for i_user in self.__ctp_manager.get_list_user():
                    #     if i_user.get_user_id().decode() == buff['UserID']:
                    #         i_user.set_on_off(buff['OnOff'])  # 设置内核中期货账户开关
                    #         break
                    self.signal_setTabIcon.emit(buff['OnOff'])
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    print("SocketManager.receive_msg() MsgType=9 修改期货账户开关失败")
            elif buff['MsgType'] == 22:  # 查询策略，查询单个策略
                print("SocketManager.receive_msg() MsgType=22，查询策略，查询单个策略", buff)
                self.print_strategy_info_for_soket(buff)  # 打印从服务端收到的持仓信息
                if buff['MsgResult'] == 0:  # 消息结果成功
                    user_id = buff['UserID']
                    strategy_id = buff['StrategyID']
                    # self.__dict_Queue_main[user_id].put(buff)  # 将修改期货账户开关回报发送给user进程
                    # for i_user in self.__ctp_manager.get_list_user():
                    #     if i_user.get_user_id().decode() == buff['UserID']:
                    #         i_user.set_on_off(buff['OnOff'])  # 设置内核中期货账户开关
                    #         break
                    self.check_strategy_position(buff)  # 核对策略市场
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    print("SocketManager.receive_msg() MsgType=9 修改期货账户开关失败")
                # 收到查询策略回报消息，激活“查询”按钮
                self.signal_activate_query_strategy_pushbutton.emit()
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
        self.signal_label_login_error_text.emit('查询行情信息')

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
        self.signal_label_login_error_text.emit('查询期货账户信息')

    # 查询期货账户会话ID
    def qry_sessions_info(self):
        dict_qry_sessions_info = {'MsgRef': self.msg_ref_add(),
                                  'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                  'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                  'MsgType': 16,  # 查询sessions
                                  'TraderID': self.__trader_id,
                                  'UserID': ''
                                  }
        # {"MsgRef": 1, "MsgSendFlag": 0, "MsgSrc": 0, "MsgType": 16, "TraderID": "1601", "UserID": ""} UserID为空，返回TraderID所属的所有user的sessions
        json_qry_sessions_info = json.dumps(dict_qry_sessions_info)
        self.slot_send_msg(json_qry_sessions_info)
        self.signal_label_login_error_text.emit('查询sessions')

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
        self.signal_label_login_error_text.emit('查询下单算法')

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
        self.signal_label_login_error_text.emit('查询策略')

    """
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
        self.signal_label_login_error_text.emit('查询策略昨仓')
    """

    # 查询期货账户昨日持仓明细（order）
    def qry_position_detial_for_order(self):
        dict_qry_position_detial_for_order = {
            'MsgRef': self.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 15,  # 查询期货账户昨日持仓明细order
            'TraderID': self.__trader_id,
            'UserID': ""  # self.__user_id, 键值为空时查询所有UserID的持仓明细
        }
        json_qry_position_detial_for_order = json.dumps(dict_qry_position_detial_for_order)
        self.slot_send_msg(json_qry_position_detial_for_order)
        self.signal_label_login_error_text.emit('查询期货账户昨日持仓明细(order)')

    # 查询期货账户昨日持仓明细（trade）
    def qry_position_detial_for_trade(self):
        dict_qry_position_detial_for_trade = {
            'MsgRef': self.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 17,  # 查询期货账户昨日持仓明细trade
            'TraderID': self.__trader_id,
            'UserID': ""  # self.__user_id, 键值为空时查询所有UserID的持仓明细
        }
        json_qry_position_detial_for_trade = json.dumps(dict_qry_position_detial_for_trade)
        self.slot_send_msg(json_qry_position_detial_for_trade)
        self.signal_label_login_error_text.emit('查询期货账户昨日持仓明细(trade)')

    """
    # 查询交易员开关
    def qry_trader_on_off(self):
        dict_qry_trader_on_off = {
            'MsgRef': self.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 8,  # 查询交易员开关
            'TraderID': self.__trader_id,
            'UserID': ""  # self.__user_id, 键值为空时查询所有UserID的策略
        }
        # {"MsgRef": 1, "MsgSendFlag": 0, "MsgType": 8, "TraderID": "1601", "OnOff": 1, "MsgSrc": 0}
        json_qry_trader_on_off = json.dumps(dict_qry_trader_on_off)
        self.slot_send_msg(json_qry_trader_on_off)
        self.signal_label_login_error_text.emit('查询交易员开关')

    # 查询期货账户开关
    def qry_user_on_off(self):
        dict_qry_user_on_off = {
            'MsgRef': self.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 10,  # 查询策略昨仓
            'TraderID': self.__trader_id,
            'UserID': ""  # self.__user_id, 键值为空时查询所有UserID的策略
        }
        json_qry_user_on_off = json.dumps(dict_qry_user_on_off)
        self.slot_send_msg(json_qry_user_on_off)
        self.signal_label_login_error_text.emit('查询期货账户开关')
    """

    # user进程将内部计算核心数据发给主进程，主进程UI显示
    def handle_Queue_get(self, Queue_user):
        while True:
            dict_data = Queue_user.get()  # 主进程get，user进程put
            start_time = time.time()
            user_id = dict_data['UserId']
            data_flag = dict_data['DataFlag']
            data_main = dict_data['DataMain']
            self.__list_widget_data = data_main  # 转存最新的策略列表信息，包含gorupBox更新所需信息
            # print("SocketManager.handle_Queue_get() 进程通信user->main，user_id =", user_id, 'data_flag =', data_flag, " data_main =", data_main)

            if data_flag == 'table_widget_data':  # 更新策略列表信息
                for i in data_main:
                    check_box = QtGui.QCheckBox()
                    if i[0] == 1:
                        check_box.setText('开')
                        check_box.setCheckState(QtCore.Qt.Checked)
                    else:
                        check_box.setText('关')
                        check_box.setCheckState(QtCore.Qt.Unchecked)
                    i[0] = check_box
                self.__dict_table_view_data[user_id] = data_main  # 主进程接收并更新user进程发来的界面更新数据-tableView
                # print(">>> SocketManager.handle_Queue_get() self.__dict_table_view_data[user_id] =", self.__dict_table_view_data[user_id])
                # print(">>> SocketManager.handle_Queue_get() data_flag = table_widget_data, len(data_main) =", len(data_main))
                # print(">>> SocketManager.handle_Queue_get() data_flag = table_widget_data, user_id =", user_id, "len(data_main) =", len(data_main))
                # current_tab_name = self.__QAccountWidget.get_current_tab_name()  # 当前tab页面
                # # 更新tableView
                # if current_tab_name == '所有账户':
                #     # 收到任何user发来的数据添加到list的尾部，合并为一个list，发送信号更新界面tableView
                #     print(">>> SocketManager.handle_Queue_get() 拼接之前，self.__list_update_widget_data =", len(self.__list_update_widget_data), self.__list_update_widget_data)
                #     self.__list_update_widget_data.extend(data_main)
                #     print(">>> SocketManager.handle_Queue_get() 拼接之后，self.__list_update_widget_data =", len(self.__list_update_widget_data), self.__list_update_widget_data)
                #     # 收到特定的user_id发来的数据更新界面，并清空更新界面的树结构，一直循环
                #     # print(">>> SocketManager.handle_Queue_get() if user_id == self.__update_ui_user_id", user_id, self.__update_ui_user_id)
                #     if user_id == self.__update_ui_user_id:
                #         # print(">>> SocketManager.handle_Queue_get() 刷新界面，self.__list_update_widget_data =", len(self.__list_update_widget_data), self.__list_update_widget_data)
                #         list_update_widget_data = copy.deepcopy(self.__list_update_widget_data)
                #         self.signal_set_data_list.emit(list_update_widget_data)
                #         self.__list_update_widget_data.clear()
                # else:
                #     # 收到与tabName相同的期货账户更新界面
                #     if user_id == current_tab_name:
                #         self.signal_set_data_list.emit(data_main)

                # # 更新groupBox
                # if self.__clicked_strategy_id != '' and self.__clicked_user_id != '':
                #     if current_tab_name == '所有账户':
                #         # 收到任何user发来的数据添加到list的尾部，合并为一个list，发送信号更新界面tableView
                #         self.__list_update_widget_data.extend(data_main)
                #         # 收到特定的user_id发来的数据更新界面，并清空更新界面的树结构，一直循环
                #         if user_id == self.__update_ui_user_id:
                #             self.signal_set_data_list.emit(self.__list_update_widget_data)
                #             self.__list_update_widget_data = list()
                #     elif user_id == current_tab_name:
                #         if len(data_main) > 0:
                #             self.signal_set_data_list.emit(data_main)
                #             try:
                #                 list_update_group_box = data_main[self.__clicked_row]
                #             except:
                #                 print(">>> SocketManager.handle_Queue_get() user_id =", user_id," data_main =", data_main)
                #             # print(">>> SocketManager.handle_Queue_get() list_update_group_box =", list_update_group_box)
            elif data_flag == 'panel_show_account_data':  # 更新账户资金情况
                # print("SocketManager.handle_Queue_get() user_id =", user_id, 'data_flag = panel_show_account_data  data_main =', data_main)
                self.__dict_panel_show_account_data[user_id] = data_main  # 主进程接收并更新user进程发来的界面更新数据-panel_show_account
                current_tab_name = self.__QAccountWidget.get_current_tab_name()  # 当前tab页面
                if current_tab_name == '所有账户':  # 所有账户tab
                    variable_equity = 0  # 0:动态权益
                    PreBalance = 0  # 1:静态权益
                    profit_position = 0  # 2:持仓盈亏
                    profit_close = 0  # 3:平仓盈亏
                    commission = 0  # 4:手续费
                    available_equity = 0  # 5:可用资金
                    used_margin = 0  # 6:占用保证金
                    # risk = ''    # 7:风险度,str
                    Deposit = 0  # 8:今日入金
                    Withdraw = 0  # 9:今日出金
                    # print("SocketManager.handle_Queue_get() user_id =", user_id, 'self.__dict_panel_show_account_data =', self.__dict_panel_show_account_data)
                    for i_user_id in self.__dict_panel_show_account_data:
                        list_panel_show_account_data_single_user = self.__dict_panel_show_account_data[i_user_id]
                        if len(list_panel_show_account_data_single_user) > 0:
                            variable_equity += list_panel_show_account_data_single_user[0]
                            PreBalance += list_panel_show_account_data_single_user[1]
                            profit_position += list_panel_show_account_data_single_user[2]
                            profit_close += list_panel_show_account_data_single_user[3]
                            commission += list_panel_show_account_data_single_user[4]
                            available_equity += list_panel_show_account_data_single_user[5]
                            used_margin += list_panel_show_account_data_single_user[6]
                            Deposit += list_panel_show_account_data_single_user[8]
                            Withdraw += list_panel_show_account_data_single_user[9]
                    # 风险度 = 占用保证金 / 动态权益
                    risk = str(round((used_margin / variable_equity) * 100)) + '%'  # 7:风险度,str
                    self.__list_panel_show_account = [variable_equity, PreBalance, profit_position, profit_close, commission, available_equity, used_margin, risk, Deposit, Withdraw]
                else:  # 单账户tab
                    if user_id == current_tab_name:
                        self.__list_panel_show_account = data_main
                        # self.signal_update_panel_show_account.emit(data_main)
            elif data_flag == 'QryInstrument':
                if len(self.__list_instrument_info) > 0:
                    pass
                elif len(self.__list_instrument_info) == 0:
                    self.__list_instrument_info = data_main  # 保存所有合约信息为本类属性
                    self.set_list_instrument_id(self.__list_instrument_info)  # 设置合约代码list
                    # print(">>> SocketManager.handle_Queue_get() self.__list_instrument_info =", self.__list_instrument_info)
                    # 待续，创建窗口：新建策略窗口，2017年3月20日16:58:50
                    # self.__QAccountWidget.create_QNewStrategy()  # 初始化“新建策略”弹窗
                    self.signal_create_QNewStrategy.emit()
            # 期货账户初始化完成
            elif data_flag == 'all_strategy_finished':
                pass
            # 期货账户合约统计信息，DataFlag:'instrument_statistics'
            elif data_flag == 'instrument_statistics':
                # self.__dict_user_Queue_data[user_id]['instrument_statistics'] = data_main
                self.__dict_user_process_data[user_id]['running']['instrument_statistics'] = data_main
            # 策略参数，DataFlag:'strategy_arguments'，由socket收到修改策略参数类消息回报后修改
            elif data_flag == 'strategy_arguments':
                strategy_id = data_main['strategy_id']
                # self.__dict_user_Queue_data[user_id]['strategy_arguments'][strategy_id] = data_main
                self.__dict_user_process_data[user_id]['running']['strategy_arguments'][strategy_id] = data_main
            # 策略统计，'strategy_statistics'
            elif data_flag == 'strategy_statistics':
                strategy_id = data_main['strategy_id']
                # self.__dict_user_Queue_data[user_id]['strategy_statistics'][strategy_id] = data_main
                self.__dict_user_process_data[user_id]['running']['strategy_statistics'][strategy_id] = data_main
            # 策略仓位
            elif data_flag == 'strategy_position':
                strategy_id = data_main['strategy_id']
                # self.__dict_user_Queue_data[user_id]['strategy_position'][strategy_id] = data_main
                self.__dict_user_process_data[user_id]['running']['strategy_position'][strategy_id] = data_main
                # print(">>> SocketManager.handle_Queue_get() self.__dict_user_process_data[user_id]['running']['strategy_position'][strategy_id] =", self.__dict_user_process_data[user_id]['running']['strategy_position'][strategy_id])
            # 'OnRtnOrder'
            elif data_flag == 'OnRtnOrder':
                # self.__dict_user_Queue_data[user_id]['OnRtnOrder'].append(data_main)
                self.__dict_user_process_data[user_id]['running']['OnRtnOrder'].append(data_main)
            # 'OnRtnTrade'
            elif data_flag == 'OnRtnTrade':
                # self.__dict_user_Queue_data[user_id]['OnRtnTrade'].append(data_main)
                self.__dict_user_process_data[user_id]['running']['OnRtnTrade'].append(data_main)
            # print(">>> handle_Queue_get take user_id = %s data_flag = %s time = %s " %(user_id, data_flag, str(time.time() - start_time)))
            elif data_flag == 'user_init_finished':
                print(">>> SocketManager.handle_Queue_get() data_flag == 'user_init_finished'")
                self.__dict_user_process_finished[user_id] = data_main
                if len(self.__dict_user_process_finished) == len(self.__list_process):
                    self.__total_process_finished = True
                    self.__QAccountWidget.set_total_process_finished(True)
                    print(">>> SocketManager.handle_Queue_get() 所有user子进程初始化完成，子进程数 =", len(self.__list_process))

    # 主进程往对应的user通信Queue里放数据
    def Queue_put(self, user_id, dict_data):
        self.__dict_Queue_main[user_id].put(dict_data)

    def write_dict_user_Queue_data(self, list_data):
        pass

    # 开始初始化
    def initialize(self):
        self.data_structure()  # 组织和创建客户端运行数据结构
        self.create_user_process()  # 创建user进程
        self.signal_q_ctp_show.emit()  # 显示主窗口，显示qctp，显示QCTP
        # self.__q_ctp.show()  # 显示主窗口
        # self.__q_login.hide()  # 隐藏登录窗口

    # 组织创建user进程所需要的所有信息，含xml文件信息和server端接收信息，合并为一个dict
    def data_structure(self):
        """
        样本数据结构
        self.__dict_user_process_data =
        {
            'user_id_1':
            {
                'xml':
                {
                    'user_statistics':
                    [
                        {'user_id': '078681', 'instrument_id': 'rb1705', 'action_count': 0, 'open_count': 0},
                        {'user_id': '078681', 'instrument_id': 'rb1710', 'action_count': 0, 'open_count': 0}
                    ],
                    'arguments':
                    [
                        {user_id="078681" strategy_id="01" trade_model="" order_algorithm="01" lots="10" lots_batch="1" stop_loss="0" strategy_on_off="1" spread_shift="0" a_instrument_id="rb1705" b_instrument_id="rb1705" a_limit_price_shift="0" b_limit_price_shift="0" a_wait_price_tick="0" b_wait_price_tick="0" a_order_action_limit="0" b_order_action_limit="0" buy_open="0" sell_close="0" sell_open="0" buy_close="0" sell_open_on_off="0" buy_close_on_off="0" buy_open_on_off="0" sell_close_on_off="0" position_a_buy="0" position_a_buy_today="0" position_a_buy_yesterday="0" position_b_buy="0" position_b_buy_today="0" position_b_buy_yesterday="0" position_a_sell="0" position_a_sell_today="0" position_a_sell_yesterday="0" position_b_sell="0" position_b_sell_today="0" position_b_sell_yesterday},

                    ],
                    'statistics':
                    [
                        {a_action_count="0" a_commission_count="0" a_order_count="0" a_profit_close="0" a_trade_rate="0" a_traded_amount="0" a_traded_count="0" b_action_count="0" b_commission_count="0" b_order_count="0" b_profit_close="0" b_trade_rate="0" b_traded_amount="0" b_traded_count="0" profit="0" profit_close="0" strategy_id="01" user_id="078681"},
                    ],
                    'position_detail_for_order':
                    [
                        {combhedgeflag="0" comboffsetflag="0" direction="0" insertdate="20170220" inserttime="11:18:30" instrumentid="cu1705" limitprice="3401.0" orderref="100000000401" orderstatus="a" strategy_id="01" tradingday="20170220" tradingdayrecord="20170221" user_id="078681" volumetotal="1" volumetotaloriginal="1" volumetraded="1" volumetradedbatch="1"}，

                    ],
                    'position_detail_for_trade':
                    [
                        {direction="0" hedgeflag="1" instrumentid="cu1705" offsetflag="0" orderref="100000000401" price="3401.0" strategy_id="01" tradedate="20170221" tradingday="20170220" tradingdayrecord="20170221" user_id="078681" volume="1"},
                    ],
                    'xml_status':
                    {
                        'datetime': "2017-03-02 10:42:36", 'tradingday': "2017-03-02", 'status': "True"
                    }
                },
                'server':
                {
                    'user_info': {},
                    'market_info': {},
                    'strategy_info': [{}, {}],
                    'list_position_detail_for_order': [{}, {}],
                    'list_position_detail_for_trade': [{}, {}],
                    'list_algorithm_info': {}
                },
                'running':
                {

                }
            },
            'user_id_2:
            {
                'xml':
                {
                },
                'server':
                {
                },
                'running':
                {
                }
            }
        }
        """
        self.__dict_user_process_data = dict()
        for i_user_info in self.__list_user_info:  # i_user_info为dict
            user_id = i_user_info['userid']  # str，期货账户id
            self.__dict_user_process_data[user_id] = dict()
            self.__dict_user_process_data[user_id]['xml'] = dict()  # 保存从本地xml获取到的数据
            self.__dict_user_process_data[user_id]['server'] = dict()  # 保存从server端获取到的数据
            self.__dict_user_process_data[user_id]['running'] = dict()  # 保存程序运行中最新的数据结构

            # 组织从xml获取到的数据
            if self.__xml_manager.get_xml_exist():
                # 获取xml中user级别统计，一个user有多条，数量与user交易的合约数量相等
                dict_user_save_info = list()
                for i_xml in self.__xml_manager.get_list_user_save_info():  # i_xml为dict
                    if i_xml['user_id'] == user_id:
                        dict_user_save_info.append(i_xml)
                self.__dict_user_process_data[user_id]['xml']['dict_user_save_info'] = dict_user_save_info

                # 获取xml中的list_user_instrument_statistics
                list_user_instrument_statistics = list()
                for i_xml in self.__xml_manager.get_list_user_instrument_statistics():
                    if i_xml['user_id'] == user_id:
                        list_user_instrument_statistics.append(i_xml)
                self.__dict_user_process_data[user_id]['xml'][
                    'list_user_instrument_statistics'] = list_user_instrument_statistics

                # 获取xml中的strategy参数，数量与strategy个数相等
                list_strategy_arguments = list()
                for i_xml in self.__xml_manager.get_list_strategy_arguments():
                    if i_xml['user_id'] == user_id:
                        list_strategy_arguments.append(i_xml)
                self.__dict_user_process_data[user_id]['xml']['list_strategy_arguments'] = list_strategy_arguments

                # 获取xml中的strategy统计数据，数量与strategy个数相等
                list_strategy_statistics = list()
                for i_xml in self.__xml_manager.get_list_strategy_statistics():
                    if i_xml['user_id'] == user_id:
                        list_strategy_statistics.append(i_xml)
                self.__dict_user_process_data[user_id]['xml']['list_strategy_statistics'] = list_strategy_statistics

                # 获取xml中的持仓明细order数据，数量不定
                list_position_detail_for_order = list()
                for i_xml in self.__xml_manager.get_list_position_detail_for_order():
                    if i_xml['user_id'] == user_id:
                        list_position_detail_for_order.append(i_xml)
                self.__dict_user_process_data[user_id]['xml'][
                    'list_position_detail_for_order'] = list_position_detail_for_order

                # 获取xml中的持仓明细trade数据，数量不定
                list_position_detail_for_trade = list()
                for i_xml in self.__xml_manager.get_list_position_detail_for_trade():
                    if i_xml['user_id'] == user_id:
                        list_position_detail_for_trade.append(i_xml)
                self.__dict_user_process_data[user_id]['xml'][
                    'list_position_detail_for_trade'] = list_position_detail_for_trade

                # 获取xml中的xml保存状态数据
                self.__dict_user_process_data[user_id]['xml']['xml_exist'] = True
            else:
                # 获取xml失败
                self.__dict_user_process_data[user_id]['xml']['xml_status'] = False

            # 组织从server获取到的数据
            if True:
                # 获取server的数据：trader_info
                self.__dict_user_process_data[user_id]['server']['trader_info'] = self.__dict_trader_info

                # 获取server的数据：user_info
                self.__dict_user_process_data[user_id]['server']['user_info'] = i_user_info

                # 获取server的数据：market_info
                self.__dict_user_process_data[user_id]['server']['market_info'] = self.__list_market_info[0]

                # 获取server的数据：strategy_info
                list_strategy_info = list()
                for i_strategy_info in self.__list_strategy_info:
                    if i_strategy_info['user_id'] == user_id:
                        list_strategy_info.append(i_strategy_info)
                self.__dict_user_process_data[user_id]['server']['strategy_info'] = list_strategy_info

                # 获取server的数据：list_position_detail_for_order
                list_position_detail_for_order = list()
                for i_position_detail_for_order in self.__list_position_detail_for_order:
                    if i_position_detail_for_order['UserID'] == user_id:
                        list_position_detail_for_order.append(i_position_detail_for_order)
                self.__dict_user_process_data[user_id]['server'][
                    'list_position_detail_for_order'] = list_position_detail_for_order

                # 获取server的数据：list_position_detail_for_trade
                list_position_detail_for_trade = list()
                for i_position_detail_for_trade in self.__list_position_detail_for_trade:
                    if i_position_detail_for_trade['UserID'] == user_id:
                        list_position_detail_for_trade.append(i_position_detail_for_trade)
                self.__dict_user_process_data[user_id]['server'][
                    'list_position_detail_for_trade'] = list_position_detail_for_trade

                # 获取server的数据：list_position_detail_for_order_today
                list_position_detail_for_order_today = list()
                for i_position_detail_for_order_today in self.__list_position_detail_for_order_today:
                    if i_position_detail_for_order_today['UserID'] == user_id:
                        list_position_detail_for_order_today.append(i_position_detail_for_order_today)
                self.__dict_user_process_data[user_id]['server'][
                    'list_position_detail_for_order_today'] = list_position_detail_for_order_today

                # 获取server的数据：list_position_detail_for_trade
                list_position_detail_for_trade_today = list()
                for i_position_detail_for_trade_today in self.__list_position_detail_for_trade_today:
                    if i_position_detail_for_trade_today['UserID'] == user_id:
                        list_position_detail_for_trade_today.append(i_position_detail_for_trade_today)
                self.__dict_user_process_data[user_id]['server'][
                    'list_position_detail_for_trade_today'] = list_position_detail_for_trade_today

            # 初始化程序运行中的数据结构
            if True:
                self.__dict_user_process_data[user_id]['running']['strategy_arguments'] = list_strategy_info  # server中获取发来
                self.__dict_user_process_data[user_id]['running']['strategy_statistics'] = dict()  # user进程发来，策略统计
                self.__dict_user_process_data[user_id]['running']['strategy_position'] = dict()  # user进程发来，策略参数
                self.__dict_user_process_data[user_id]['running']['instrument_statistics'] = dict()  # user进程发来，合约统计
                self.__dict_user_process_data[user_id]['running']['OnRtnOrder'] = list()  # user进程发来，OnRtnOrder
                self.__dict_user_process_data[user_id]['running']['OnRtnTrade'] = list()  # user进程发来，OnRtnTrade

    # 创建user进程
    def create_user_process(self):
        # 初始化存放Queue结构的dict
        self.__dict_Queue_main = dict()  # 主进程put，user进程get
        self.__dict_Queue_user = dict()  # user进程put，主进程get
        self.__dict_Thread = dict()  # 存放线程对象，键名为user_id
        self.__list_process = list()  # 存放user进程的list
        index = 0
        self.__dict_tab_index['所有账户'] = index
        for user_id in self.__dict_user_process_data:
            index += 1
            self.signal_QAccountWidget_addTabBar.emit(user_id)  # 创建窗口的tabBar
            self.__dict_tab_index[user_id] = index  # 键名：user_id,键值：tab的index

            self.__dict_user_process_data[user_id]['running']['strategy_arguments'] = dict()  # sockt发来
            self.__dict_user_process_data[user_id]['running']['strategy_statistics'] = dict()  # user进程发来，策略统计
            self.__dict_user_process_data[user_id]['running']['strategy_position'] = dict()  # user进程发来，策略参数
            self.__dict_user_process_data[user_id]['running']['instrument_statistics'] = dict()  # user进程发来，合约统计
            self.__dict_user_process_data[user_id]['running']['OnRtnOrder'] = list()  # user进程发来，OnRtnOrder
            self.__dict_user_process_data[user_id]['running']['OnRtnTrade'] = list()  # user进程发来，OnRtnTrade

            dict_user_info = self.__dict_user_process_data[user_id]  # 创建user进程必须的初始化参数

            Queue_main = Queue()  # 主进程put，user进程get
            Queue_user = Queue()  # user进程put，主进程get
            self.__dict_Queue_main[user_id] = Queue_main
            self.__dict_Queue_user[user_id] = Queue_user

            # 创建user独立进程
            p = Process(target=static_create_user_process, args=(dict_user_info, Queue_main, Queue_user))
            p.daemon = True  # p进程生命周期同主进程
            self.__list_process.append(p)
            # 主进程为每个user进程创建独立的线程，用来处理user进程put到queue的数据
            qthread = threading.Thread(target=self.handle_Queue_get, args=(Queue_user,))
            self.__dict_Thread[user_id] = qthread
            qthread.setDaemon(True)  # 线程生命周期同主进程
            qthread.start()
            p.start()  # 开始user进程
        self.signal_init_setTabIcon.emit()  # 初始化tabBar样式

    # 收到查询策略回报，MsgType=3，进程间通信，将策略参数发送给对应的user进程
    def process_communicate_query_strategy(self, list_data):
        for i in list_data:
            user_id = i['user_id']
            strategy_id = i['strategy_id']
            msg_process = {'MsgType': 3, 'UserID': user_id, 'StrategyID': strategy_id, 'Info': [i]}
            self.__dict_Queue_main[user_id].put(msg_process)  # 一次发送一个策略参数

    # 核对策略持仓，服务端收到的最新策略持仓与进程间通信main进程中的策略持仓
    def check_strategy_position(self, buff):
        user_id = buff['UserID']
        strategy_id = buff['StrategyID']
        for i in self.get_dict_table_view_data()[user_id]:
            # 从user下所有的策略参数中找到特定的策略
            if strategy_id == i[2]:
                list_strategy_args = i
                print(">>> SocketManager.check_strategy_position() list_strategy_args =", list_strategy_args)
                break
        position_b_sell = int(list_strategy_args[5])
        position_b_sell_yesterday = int(list_strategy_args[34])
        position_b_buy = int(list_strategy_args[6])
        position_b_buy_yesterday = int(list_strategy_args[35])
        position_a_sell = int(list_strategy_args[30])
        position_a_sell_yesterday = int(list_strategy_args[31])
        position_a_buy = int(list_strategy_args[32])
        position_a_buy_yesterday = int(list_strategy_args[33])
        equality_flag = True
        if position_b_sell != buff['Info'][0]['position_b_sell']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_b_sell != buff['Info'][0]['position_b_sell']", position_b_sell, buff['Info'][0]['position_b_sell'], type(position_b_sell), type(buff['Info'][0]['position_b_sell']))
        if position_b_sell_yesterday != buff['Info'][0]['position_b_sell_yesterday']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_b_sell_yesterday != buff['Info'][0]['position_b_sell_yesterday']", position_b_sell_yesterday, buff['Info'][0]['position_b_sell_yesterday'], type(position_b_sell_yesterday), type(buff['Info'][0]['position_b_sell_yesterday']))
        if position_b_buy != buff['Info'][0]['position_b_buy']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_b_buy != buff['Info'][0]['position_b_buy']", position_b_buy, buff['Info'][0]['position_b_buy'], type(position_b_buy), type(buff['Info'][0]['position_b_buy']))
        if position_b_buy_yesterday != buff['Info'][0]['position_b_buy_yesterday']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_b_buy_yesterday != buff['Info'][0]['position_b_buy_yesterday']", position_b_buy_yesterday, buff['Info'][0]['position_b_buy_yesterday'], type(position_b_buy_yesterday), type(buff['Info'][0]['position_b_buy_yesterday']))
        if position_a_sell != buff['Info'][0]['position_a_sell']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_a_sell != buff['Info'][0]['position_a_sell']", position_a_sell, buff['Info'][0]['position_a_sell'], type(position_a_sell), type(buff['Info'][0]['position_a_sell']))
        if position_a_sell_yesterday != buff['Info'][0]['position_a_sell_yesterday']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_a_sell_yesterday != buff['Info'][0]['position_a_sell_yesterday']", position_a_sell_yesterday, buff['Info'][0]['position_a_sell_yesterday'], type(position_a_sell_yesterday), type(buff['Info'][0]['position_a_sell_yesterday']))
        if position_a_buy != buff['Info'][0]['position_a_buy']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_a_buy != buff['Info'][0]['position_a_buy']", position_a_buy, buff['Info'][0]['position_a_buy'], type(position_a_buy), type(buff['Info'][0]['position_a_buy']))
        if position_a_buy_yesterday != buff['Info'][0]['position_a_buy_yesterday']:
            equality_flag = False
            print(">>> SocketManager.check_strategy_position() position_a_buy_yesterday != buff['Info'][0]['position_a_buy_yesterday']", position_a_buy_yesterday, buff['Info'][0]['position_a_buy_yesterday'], type(position_a_buy_yesterday), type(buff['Info'][0]['position_a_buy_yesterday']))
        if equality_flag:
            pass
            # QMessageBox().showMessage("消息", "服务端与客户端持仓一致！")
            # message_list = ['消息', '服务端与客户端持仓一致']
            # self.signal_show_message.emit(message_list)
            # self.msg_box.exec()
            dict_args = {"title": "消息", "main": "服务端与客户端持仓一致"}
            self.signal_show_alert.emit(dict_args)
        else:
            # QMessageBox().showMessage("消息", "服务端与客户端持仓不一致！")
            # message_list = ['消息', '注意：服务端与客户端持仓不一致']
            # self.signal_show_message.emit(message_list)
            # self.msg_box.exec()
            dict_args = {"title": "消息", "main": "注意，服务端与客户端持仓不一致"}
            self.signal_show_alert.emit(dict_args)

    # 输出特定策略的持仓变量，格式如下
    # A总卖 0 A昨卖 0
    # B总买 0 B昨卖 0
    # A总买 0 A昨买 0
    # B总卖 0 B昨卖 0
    def print_strategy_data(self, user_id, strategy_id):
        dict_table_view_data = self.get_dict_table_view_data()
        for i_user_id in dict_table_view_data:
            if i_user_id == user_id:
                for list_strategy_info in dict_table_view_data[i_user_id]:
                    if list_strategy_info[2] == strategy_id:
                        print("SocketManager.print_position() 主进程数据 user_id =", user_id, "strategy_id =", strategy_id)
                        print("A总卖", list_strategy_info[30], "A昨卖", list_strategy_info[31])
                        print("B总买", list_strategy_info[6], "B昨买", list_strategy_info[35])
                        print("A总买", list_strategy_info[32], "A昨买", list_strategy_info[33])
                        print("B总卖", list_strategy_info[5], "B昨卖", list_strategy_info[34])
                        print("平仓盈亏-手续费=净盈亏", list_strategy_info[9], list_strategy_info[10], list_strategy_info[11])
                        break  # 跳出1282行for
                break  # 跳出1280行for

    def print_strategy_info_for_soket(self, buff):
        print("SocketManager.print_strategy_info_for_soket() 服务端数据程数据 user_id =", buff['UserID'], "strategy_id =", buff['StrategyID'])
        print("A总卖", buff['Info'][0]['position_a_sell'], "A昨卖", buff['Info'][0]['position_a_sell_yesterday'])
        print("B总买", buff['Info'][0]['position_b_buy'], "B昨买", buff['Info'][0]['position_b_buy_yesterday'])
        print("A总买", buff['Info'][0]['position_a_buy'], "A昨买", buff['Info'][0]['position_a_buy_yesterday'])
        print("B总卖", buff['Info'][0]['position_b_sell'], "B昨卖", buff['Info'][0]['position_b_sell_yesterday'])

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


