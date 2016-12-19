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

    def set_CTPManager(self, obj_CTPManager):
        self.__CTPManager = obj_CTPManager

    def get_CTPManager(self):
        return self.__CTPManager
    
    def set_ClientMain(self, obj_QClientMain):
        self.__q_client_main = obj_QClientMain
        
    def get_QClientMain(self):
        return self.__q_client_main

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
        try:
            size = self.__sockfd.send(data)  # 发送数据
        except socket.timeout as e:
            print("SocketManager.send_msg()", e)
        self.__event.clear()
        return size if self.__event.wait(2.0) else -1

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
                    # self.signal_send_message.emit(dict_buff)
                    self.receive_msg(dict_buff)
                    # print("SocketManager.run() 调用self.signal_send_message.emit(dict_buff)之后")
                    # time.sleep(5.0)
                    if dict_buff['MsgRef'] == self.__msg_ref:  # 收到服务端发送的收到消息回报
                        self.__event.set()
                        print("SocketManager.run() 收到数据，解除收发数据协程锁")
                else:
                    print("SocketManager.run() 接收到的数据有误", m.buff)
                    continue

    # 处理收到的消息
    def receive_msg(self, buff):
        # 消息源MsgSrc值：0客户端、1服务端
        if buff['MsgSrc'] == 0:  # 由客户端发起的消息类型
            # 内核初始化未完成
            if self.__CTPManager.get_init_finished() is False:
                if buff['MsgType'] == 1:  # 交易员登录验证，MsgType=1
                    print("ClientMain.slot_output_message() MsgType=1", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 验证通过
                        # self.get_QLoginForm().label_login_error.setText(buff['MsgErrorReason'])  # 界面提示信息
                        self.get_QLoginForm().label_login_error.setText('登陆成功，初始化中...')  # 界面提示信息
                        self.__CTPManager.set_trader_id(buff['TraderID'])  # 将TraderID设置为CTPManager的属性
                        self.__CTPManager.set_trader_name(buff['TraderName'])  # 将TraderID设置为CTPManager的属性
                        # self.__CTPManager.create_trader({"trader_id": buff['TraderID'], "trader_name": buff['TraderName']})
                        self.__TraderID = buff['TraderID']
                        self.__TraderName = buff['TraderName']
                        self.QryMarketInfo()  # 查询行情配置
                        # self.__sm.signal_send_message.emit(self.slot_output_message)  # 绑定自定义信号槽
                    elif buff['MsgResult'] == 1:  # 验证不通过
                        self.get_QLoginForm().label_login_error.setText(buff['MsgErrorReason'])  # 界面提示错误信息
                        self.get_QLoginForm().pushButton_login.setEnabled(True)  # 登录按钮激活
                elif buff['MsgType'] == 4:  # 查询行情配置，MsgType=4
                    print("ClientMain.slot_output_message() MsgType=4", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listMarketInfo = buff['Info']  # 转存行情信息到本类的属性里
                        self.QryUserInfo()  # 查询期货账户
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 2:  # 查询期货账户，MsgType=2
                    print("ClientMain.slot_output_message() MsgType=2", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listUserInfo = buff['Info']  # 转存期货账户信息到本类的属性里
                        self.QryAlgorithmInfo()  # 查询下单算法信息
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 11:  # 查询下单算法编号，MsgType=11
                    print("ClientMain.slot_output_message() MsgType=11", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listAlgorithmInfo = buff['Info']  # 转存期货账户信息到本类的属性里
                        self.QryStrategyInfo()  # 查询策略信息
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 3:  # 查询策略，MsgType=3
                    print("ClientMain.slot_output_message() MsgType=3", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listStrategyInfo = buff['Info']  # 转存策略信息到本类的属性里
                        self.QryYesterdayPosition()
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 10:  # 查询策略昨仓，MsgType=10
                    print("ClientMain.slot_output_message() MsgType=10", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listYesterdayPosition = buff['Info']  # 所有策略昨仓的list
                        self.__CTPManager.set_YesterdayPosition(buff['Info'])  # 所有策略昨仓的list设置为CTPManager属性
                        if self.__CTPManager.get_init_finished() is False:
                            self.__CTPManager.init()  # 跳转到开始初始化程序，有CTPManager开始初始化
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
            # 内核初始化完成
            elif self.__CTPManager.get_init_finished():
                if buff['MsgType'] == 3:  # 查询策略，MsgType=3
                    print("ClientMain.slot_output_message() MsgType=3", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listStrategyInfoOnce = buff['Info']  # 转存策略信息到本类的属性里(单次查询)
                        # 遍历查询到的消息结果列表
                        for i_Info in self.__listStrategyInfoOnce:
                            # 遍历策略对象列表，将服务器查询到的策略参数传递给策略，并调用set_arguments方法更新内核参数值
                            for i_strategy in self.__CTPManager.get_list_strategy():
                                if i_Info['user_id'] == i_strategy.get_user_id() and i_Info[
                                    'strategy_id'] == i_strategy.get_strategy_id():
                                    i_strategy.set_arguments(i_Info)  # 将查询参数结果设置到策略内核，所有的策略
                                    self.signal_UI_update_strategy.emit(
                                        i_strategy)  # 更新策略在界面显示，（槽绑定到所有窗口对象槽函数update_strategy）
                                    break
                        self.signal_pushButton_query_strategy_setEnabled.emit(True)  # 收到消息后将按钮激活
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=3 查询策略失败")
                elif buff['MsgType'] == 6:  # 新建策略，MsgType=6
                    print("ClientMain.slot_output_message() MsgType=6", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.get_CTPManager().create_strategy(buff['Info'][0])  # 内核创建策略对象
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() ", buff['MsgErrorReason'])
                elif buff['MsgType'] == 5:  # 修改策略参数，MsgType=5
                    print("ClientMain.slot_output_message() MsgType=5", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        for i_strategy in self.__CTPManager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] \
                                    and i_strategy.get_strategy_id() == buff['StrategyID']:
                                i_strategy.set_arguments(buff['Info'][0])
                                # self.signal_UI_update_strategy.emit(i_strategy)  # 更新策略在界面显示，（槽绑定到所有窗口对象槽函数update_strategy）
                            break
                            # for i_widget in self.__list_QAccountWidget:
                            #     i_widget.update_groupBox_trade_args_for_set()  # 更新策略参数框goupBox
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=5 修改策略参数失败")
                elif buff['MsgType'] == 12:  # 修改策略持仓，MsgType=12
                    print("ClientMain.slot_output_message() MsgType=12", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        # 更新内核中的策略持仓
                        for i_strategy in self.__CTPManager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] \
                                    and i_strategy.get_strategy_id() == buff['StrategyID']:
                                i_strategy.set_position(buff['Info'][0])
                            break
                        self.signal_pushButton_set_position_setEnabled.emit()  # 激活设置持仓按钮，禁用仓位输入框
                        pass
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=12 修改策略持仓失败")
                elif buff['MsgType'] == 7:  # 删除策略，MsgType=7
                    print("ClientMain.slot_output_message() MsgType=7", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        dict_args = {'user_id': buff['UserID'], 'strategy_id': buff['StrategyID']}
                        self.__CTPManager.delete_strategy(dict_args)
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=7 删除策略失败")
                elif buff['MsgType'] == 13:  # 修改策略交易开关
                    print("ClientMain.slot_output_message() MsgType=13", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        for i_strategy in self.__CTPManager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] and i_strategy.get_strategy_id() == buff[
                                'StrategyID']:
                                i_strategy.set_on_off(buff['OnOff'])  # 更新内核中策略开关
                                # self.signal_update_strategy.emit(i_strategy)  # 更新策略在界面显示
                                # self.get_clicked_item().setFlags(self.get_clicked_item().flags() ^ (QtCore.Qt.ItemIsEnabled))
                                break
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=13 修改策略交易开关失败")
                elif buff['MsgType'] == 14:  # 修改策略只平开关
                    print("ClientMain.slot_output_message() MsgType=14", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        for i_strategy in self.__CTPManager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] and i_strategy.get_strategy_id() == buff[
                                'StrategyID']:
                                i_strategy.set_only_close(buff['OnOff'])  # 更新内核中策略只平开关
                                # self.signal_update_strategy.emit(i_strategy)  # 更新策略在界面显示
                                # self.get_clicked_item().setFlags(self.get_clicked_item().flags() ^ (QtCore.Qt.ItemIsEnabled))
                                break
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=14 修改策略只平开关失败")
                elif buff['MsgType'] == 8:  # 修改交易员开关
                    print("ClientMain.slot_output_message() MsgType=8", buff)
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
                        print("ClientMain.slot_output_message() MsgType=8 修改交易员开关失败")
                elif buff['MsgType'] == 9:  # 修改期货账户开关
                    print("ClientMain.slot_output_message() MsgType=9", buff)
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
                        print("ClientMain.slot_output_message() MsgType=9 修改期货账户开关失败")
        elif buff['MsgSrc'] == 1:  # 由服务端发起的消息类型
            pass

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


