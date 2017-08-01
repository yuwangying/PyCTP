# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""

import os
import sys
import time
import threading
from operator import itemgetter
from datetime import datetime
import copy
from PyCTP_Trade import PyCTP_Trader_API
import Utils
from pandas import DataFrame, Series
import queue
from MarketManager import MarketManager
from Strategy import Strategy
import PyCTP
# from pymongo import MongoClient
# from PyQt4 import QtCore
# import pandas as pd


# class User(QtCore.QObject):
class User():
    # signal_update_pushButton_start_strategy = QtCore.pyqtSignal()  # 定义信号：内核设置期货账户交易开关 -> 更新窗口“开始策略”按钮状态
    # signal_label_login_error_text = QtCore.pyqtSignal(str)  # 定义信号：->更新登录窗口文本
    # signal_update_panel_show_account = QtCore.pyqtSignal(dict)  # 定义信号：更新界面账户资金信息

    # 初始化参数BrokerID\UserID\Password\frontaddress，参数格式为二进制字符串
    # def __init__(self, dict_arguments, parent=None, ctp_manager=None):
    def __init__(self, dict_arguments, Queue_main, Queue_user):
        self.save_log(dict_arguments)  # 日志重定向到本地文件夹

        # print('process_id =', os.getpid(), ', User.__init__() dict_arguments =', dict_arguments)
        self.__init_arguments = dict_arguments  # 转存形参
        self.__Queue_main = Queue_main  # 主进程put，user进程get
        self.__Queue_user = Queue_user  # user进程put，主进程get
        self.__queue_OnRtnTrade = queue.Queue(maxsize=0)  # 缓存OnRtnTrade回调数据，仅本套利系统的记录
        self.__queue_OnRtnOrder = queue.Queue(maxsize=0)  # 缓存OnRtnOrder回调数据，仅本套利系统的记录
        self.__queue_OnRtnOrder_user = queue.Queue(maxsize=0)  # 缓存OnRtnOrder回调数据，期货账户的所有order数据
        self.__threading_OnRtnOrder = threading.Thread(target=self.threading_run_OnRtnOrder)
        self.__threading_OnRtnTrade = threading.Thread(target=self.threading_run_OnRtnTrade)
        self.__threading_count_commission_order = threading.Thread(target=self.threading_count_commission_order)
        self.__threading_OnRtnOrder.setDaemon(True)
        self.__threading_OnRtnTrade.setDaemon(True)
        self.__threading_count_commission_order.setDaemon(True)
        self.__dict_commission = dict()  # 保存手续费的字典，字典内元素格式为{'cu':{'OpenRatioByVolume': 0.0, 'OpenRatioByMoney': 2.5e-05, 'CloseTodayRatioByVolume': 0.0, 'CloseTodayRatioByMoney': 0.0, 'CloseRatioByVolume': 0.0, 'CloseRatioByMoney': 2.5e-05, 'InstrumentID': 'cu',  'InvestorRange': '1'}}
        self.__dict_strategy = dict()  # 存放策略对象的dict,{strategy_id: obj_strategy}
        self.__dict_strategy_finished = dict()  # 存放策略对象初始化完成标志{strategy_id: False}
        self.__dict_instrument_statistics = dict()  # 合约统计dict，{'rb1705': {'open_count': 0, 'action_count': 0}}
        self.__dict_action_counter = dict()  # 记录合约撤单次数的字典，撤单操作时添加次数，交易日换日时初始化值
        self.__dict_open_counter = dict()  # 记录合约开仓次数的字典
        self.__list_panel_show_account_data = list()  # 界面更新期货账户资金情况数据结构
        self.__commission_order = 0  # 申报费，中金所股指期货合约存在申报费
        self.__list_OrderRef_for_count_commission_order = list()  # 统计申报费的OrderRef管理list
        self.__dict_last_tick = dict()  # 存放所有订阅合约的最后一个tick
        self.__Margin_Occupied_CFFEX = 0  # 上期所品种的持仓占用保证金初始值
        self.__Margin_Occupied_SHFE = 0
        self.__Margin_Occupied_CZCE = 0
        self.__Margin_Occupied_DCE = 0

        self.load_server_data(self.__init_arguments)  # 组织从server获取到的数据
        self.load_xml_data(self.__init_arguments)  # 组织从xml获取到的数据

        self.__qry_api_last_time = time.time()  # 类型浮点数，最后一次查询Trade_Api的时间
        self.__order_ref_part2 = 0  # 所有策略共用报单引用编号，报单引用首位固定为1，后两位为策略编号，中间部分递增1

        # 创建行情，获取交易日
        self.__dict_create_user_status = dict()  # User创建状态详情，包含marekt创建信息
        self.__market_manager = MarketManager(self.__server_dict_market_info)
        self.__market_manager.set_User(self)  # User设置为属性
        self.__dict_create_user_status['result_market_connect'] = self.__market_manager.get_result_market_connect()
        self.__dict_create_user_status['get_result_market_login'] = self.__market_manager.get_result_market_login()
        self.__create_market_failed = False  # 创建行情失败标志位
        for i in self.__dict_create_user_status:
            if self.__dict_create_user_status[i] != 0:
                print("User.__init__() user_id =", self.__user_id, "创建行情失败, self.__dict_create_user_status =", self.__dict_create_user_status)
                self.__create_market_failed = True
        if not self.__create_market_failed:
            print("User.__init__() user_id =", self.__user_id, "创建行情成功, self.__dict_create_user_status =", self.__dict_create_user_status)
        self.__MdApi_TradingDay = self.__market_manager.get_TradingDay()  # 获取行情接口的交易日
        self.tdapi_start_model()  # 根据xml导入数据情况判断TdApi启动模式:RESTART、RESUME
        # self.init_instrument_statistics()  # 初始化期货账户合约统计：撤单次数和开仓手数

        # 连接交易前置
        self.connect_trade_front()  # 连接交易前置
        self.login_trade_account()  # 登录期货账户，期货账户登录成功一刻开始OnRtnOrder、OnRtnTrade就开始返回历史数据
        self.qry_trading_account()  # 查询资金账户
        self.qry_instrument_info()  # 查询合约信息
        # self.qry_investor_position()  # 查询投资者持仓
        self.qry_inverstor_position_detail()  # 查询投资者持仓明细
        self.__create_user_success = True  # 初始化创建user失败标志
        for i in self.__dict_create_user_status:
            if self.__dict_create_user_status[i] != 0:
                self.__create_user_success = False  # 创建期货账户失败
        if self.__create_user_success:
            print("User.__init__() User创建成功 user_id =", self.__user_id, ", self.__dict_create_user_status =", self.__dict_create_user_status)
        else:
            print("User.__init__() User创建失败 user_id =", self.__user_id, ", self.__dict_create_user_status =", self.__dict_create_user_status)
            return

        # 从TdApi获取必要的参数
        # for obj_strategy in self.__list_strategy:
        #     obj_strategy.get_td_api_arguments()  # 将期货账户api查询参数赋值给strategy对象
        #     obj_strategy.load_xml()  # strategy装载xml
        #     obj_strategy.start_run_count()  # 开始核心统计运算线程
            # 遍历strategy初始化完成之前的order和trade回调记录，完成strategy初始化工作，遍历queue_strategy_order\queue_strategy_trade

        # 创建策略
        for i in self.__server_list_strategy_info:
            self.create_strategy(i)
        # 策略初始化完成，启动转发OnRtnOrder、OnRtnTrade的线程
        self.__threading_OnRtnOrder.start()
        self.__threading_OnRtnTrade.start()
        self.__threading_count_commission_order.start()

        # user初始化完成
        self.set_init_finished(True)

        # 定时进程间通信,user子进程发送信息给main进程,主进程接收到信息后更新界面
        self.__timer_thread = threading.Thread(target=self.timer_queue_put)
        self.__timer_thread.daemon = True
        self.__timer_thread.start()

        # strategy创建完成，发送进程间通信给主进程，主进程收到之后让user查询合约信息


        # 查询user的持仓明细
        # order结构的持仓明细
        # for i in self.__ctp_manager.get_SocketManager().get_list_position_detail_info_for_order():
        #     if i['userid'] == self.__user_id:
        #         self.__server_list_position_detail_for_order_yesterday.append(i)

        # trade结构的持仓明细
        # for i in self.__ctp_manager.get_SocketManager().get_list_position_detail_info_for_trade():
        #     if i['userid'] == self.__user_id:
        #         self.__server_list_position_detail_for_trade_yesterday.append(i)

        # 查询成交记录
        # time.sleep(1.0)
        # self.qry_api_interval_manager()  # API查询时间间隔管理
        # self.QryTrade()  # 保存查询当天的Trade和Order记录，正常值格式为DataFrame，异常值为None
        # print(">>> User.__init__() len(self.__list_QryTrade) =", len(self.__list_QryTrade))
        # QryTrade查询结果的状态记录到CTPManager的user状态字典，成功为0
        # if isinstance(self.__list_QryTrade, list):
        #     self.__ctp_manager.get_dict_create_user_status()[self.__user_id]['QryTrade'] = 0  # 初始过程中一个步骤的标志位
        #     print("User.__init__() user_id=", self.__user_id, '查询成交记录成功，self.__list_QryTrade=', self.__list_QryTrade)
        # else:
        #     self.__ctp_manager.get_dict_create_user_status()[self.__user_id]['QryTrade'] = 1
        #     print("User.__init__() user_id=", self.__user_id, '查询成交记录失败，self.__list_QryOrder=', self.__list_QryOrder)
        # self.__ctp_manager.get_dict_create_user_status()[self.__user_id]['login_trade_account'] = login_trade_account

        # 查询报单记录
        # time.sleep(1.0)
        # self.qry_api_interval_manager()  # API查询时间间隔管理
        # self.QryOrder()
        # QryOrder查询结果的状态记录到CTPManager的user状态字典，成功为0
        # if isinstance(self.__list_QryOrder, list):
        #     self.__ctp_manager.get_dict_create_user_status()[self.__user_id]['QryOrder'] = 0
        #     print("User.__init__() user_id=", self.__user_id, '查询报单记录成功，self.__list_QryOrder=', self.__list_QryOrder)
        # else:
        #     self.__ctp_manager.get_dict_create_user_status()[self.__user_id]['QryOrder'] = 1
        #     print("User.__init__() user_id=", self.__user_id, '查询报单记录失败')

        # print("User.__init__() user_id=", self.__user_id, "CTPManager记录User初始化信息 ", {self.__user_id: self.__ctp_manager.get_dict_create_user_status()[self.__user_id]})

        # 初始化策略持仓明细列表
        # if self.init_list_position_detail() is not True:
        #     print("Strategy.__init__() 策略初始化错误：初始化策略持仓明细列表出错")
        #     self.__init_finished = False  # 策略初始化失败
        #     return

    # 日志重定向到本地文件夹
    def save_log(self, dict_arguments):
        user_id = dict_arguments['server']['user_info']['userid']
        # 删除log文件夹，创建log文件夹
        if os.path.exists('log'):
            pass  # 已存在文件夹，什么都不用操作
            # print("ClientMin.'__main__' log文件夹存在，删除重建log文件夹")
            # shutil.rmtree('log')
        else:
            # print("ClientMin.'__main__' log文件夹不存在，创建log文件夹")
            os.mkdir('log')
        # print全部存到log本地文件
        time_str = datetime.now().strftime('%Y%m%d %H%M%S')

        file_path_error = 'log/' + user_id + '_error_' + time_str + '.log'
        stderr_handler = open(file_path_error, 'w')
        sys.stderr = stderr_handler

        file_path_stdout = 'log/' + user_id + '_out_' + time_str + '.log'
        stdout_handler = open(file_path_stdout, 'w')
        sys.stdout = stdout_handler

    # 连接交易前置
    def connect_trade_front(self):
        """连接交易前置"""
        # 为每个user创建独立的流文件夹
        s_path = b'conn/td/' + self.__user_id.encode() + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__trader_api = PyCTP_Trader_API.CreateFtdcTraderApi(s_path)
        self.__trader_api.set_user(self)  # 将该类设置为trade的属性

        # 0：发送成功；-1：因网络原因发送失败；-2：未处理请求队列总数量超限；-3：每秒发送请求数量超限
        connect_trade_front = self.__trader_api.Connect(self.__FrontAddress, self.__TdApi_start_model)
        # 连接前置地址状态记录到CTPManager的user状态字典，成功为0
        self.__dict_create_user_status['connect_trade_front'] = connect_trade_front

        # 连接交易前置错误提示
        if connect_trade_front == -1:
            self.signal_label_login_error_text.emit("期货账户" + self.__user_id + "因网络原因发送失败")
            self.__dict_create_user_status['connect_trade_front'] = "因网络原因发送失败"
        elif connect_trade_front == -2:
            self.signal_label_login_error_text.emit("期货账户" + self.__user_id + "未处理请求队列总数量超限")
            self.__dict_create_user_status[
                'connect_trade_front'] = "未处理请求队列总数量超限"
        elif connect_trade_front == -3:
            self.signal_label_login_error_text.emit("期货账户" + self.__user_id + "每秒发送请求数量超限")
            self.__dict_create_user_status['connect_trade_front'] = "每秒发送请求数量超限"
        elif connect_trade_front == -4:
            self.signal_label_login_error_text.emit("期货账户" + self.__user_id + "连接交易前置异常")
            self.__dict_create_user_status['connect_trade_front'] = "连接交易前置异常"

        if connect_trade_front != 0:
            self.__init_finished_succeed = False  # 初始化失败
            print("User.__init__() user_id=", self.__user_id, '连接交易前置失败',
                  Utils.code_transform(connect_trade_front))
        else:
            print("User.__init__() user_id=", self.__user_id, '连接交易前置成功', Utils.code_transform(connect_trade_front))

    # 登录期货账号
    def login_trade_account(self):
        """登录期货账号"""
        self.qry_api_interval_manager()  # API查询时间间隔管理
        login_trade_account = self.__trader_api.Login(self.__BrokerID.encode(), self.__user_id.encode(), self.__Password.encode())
        # 登录期货账号状态记录到CTPManager的user状态字典，成功为0
        # self.__dict_create_user_status['login_trade_account'] = login_trade_account
        if login_trade_account != 0:
            self.__init_finished_succeed = False  # 初始化失败
            print("User.login_trade_account() user_id=", self.__user_id, '登录期货账号失败',
                  Utils.code_transform(login_trade_account))
            return
        else:
            self.__front_id = self.__trader_api.get_front_id()  # 获取前置编号
            self.__session_id = self.__trader_api.get_session_id()  # 获取会话编号
            self.__TradingDay = self.__trader_api.get_TradingDay().decode()  # 获取交易日
            print("User.login_trade_account() user_id=", self.__user_id, 'self.__TradingDay =', self.__TradingDay)
            print("User.login_trade_account() user_id=", self.__user_id, '登录期货账号成功', Utils.code_transform(login_trade_account))

    # 查询资金账户
    def qry_trading_account(self):
        """查询资金账户"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        time_now = datetime.now()
        self.__date_qry_trading_account = time_now.strftime('%Y%m%d')  # 查询投资者持仓明细的北京时间
        self.__time_qry_trading_account = time_now.strftime('%H:%M:%S')  # 查询投资者持仓明细的北京时间
        list_QryTradingAccount = self.__trader_api.QryTradingAccount()
        if isinstance(list_QryTradingAccount, list):
            if isinstance(list_QryTradingAccount[0], dict):
                self.__QryTradingAccount = Utils.code_transform(list_QryTradingAccount[0])
                self.__dict_trading_account = copy.deepcopy(self.__QryTradingAccount)  # 转存为程序运行中的数据结构，实时更新
                # dict_msg = {
                #     'DataFlag': 'trading_account',
                #     'UserId': self.__user_id,
                #     'DataMain': self.__dict_trading_account  # 最新策略统计
                # }
                # print(">>> User.qry_trading_account() user_id =", self.__user_id, 'data_flag = trading_account', 'data_msg =', dict_msg)
                # self.__Queue_user.put(dict_msg)
                self.__dict_create_user_status['QryTradingAccount'] = 0  # user初始化状态信息
                self.__profit_close = self.__dict_trading_account['CloseProfit']  # 平仓盈亏
                self.__commission = self.__dict_trading_account['Commission']  # 手续费
                print("User.__init__() user_id=", self.__user_id, '查询资金账户成功', self.__QryTradingAccount)
            else:
                print("User.__init__() user_id=", self.__user_id, '查询资金账户失败', Utils.code_transform(list_QryTradingAccount))
                self.__dict_create_user_status['QryTradingAccount'] = Utils.code_transform(list_QryTradingAccount)
        else:
            print("User.__init__() user_id=", self.__user_id, '查询资金账户失败',
                  Utils.code_transform(list_QryTradingAccount))
            self.__dict_create_user_status['QryTradingAccount'] = Utils.code_transform(list_QryTradingAccount)

    # 查询投资者持仓
    def qry_investor_position(self):
        """查询投资者持仓"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        self.__QryInvestorPosition = Utils.code_transform(self.__trader_api.QryInvestorPosition())
        if isinstance(self.__QryInvestorPosition, list):
            self.__dict_create_user_status['QryInvestorPosition'] = 0
            print("User.__init__() user_id=", self.__user_id, '查询投资者持仓成功', self.__QryInvestorPosition)
        else:
            self.__dict_create_user_status[
                'QryInvestorPosition'] = self.__QryInvestorPosition
            print("User.__init__() user_id=", self.__user_id, '查询投资者持仓失败', self.__QryInvestorPosition)

    # 查询投资者持仓明细
    def qry_inverstor_position_detail(self):
        """查询投资者持仓明细"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        time_now = datetime.now()
        self.__date_qry_inverstor_position_detail = time_now.strftime('%Y%m%d')  # 查询投资者持仓明细的北京时间
        self.__time_qry_inverstor_position_detail = time_now.strftime('%H:%M:%S')  # 查询投资者持仓明细的北京时间
        self.__QryInvestorPositionDetail = Utils.code_transform(self.__trader_api.QryInvestorPositionDetail())
        if isinstance(self.__QryInvestorPositionDetail, list):
            self.__dict_create_user_status['QryInvestorPositionDetail'] = 0
            print("User.__init__() user_id=", self.__user_id, '查询投资者持仓明细成功，长度', len(self.__QryInvestorPositionDetail), self.__QryInvestorPositionDetail)
            # self.__qry_investor_position_detail = copy.deepcopy(self.__QryInvestorPositionDetail)  # 深度拷贝，通过OnRtnTrade持续更新

            # 将从API查询的持仓明细转换格式为程序维护的持仓明细
            self.__qry_investor_position_detail = list()
            for i in self.__QryInvestorPositionDetail:
                if i['Volume'] > 0:
                    instrument_id = i['InstrumentID']
                    instrument_multiple = self.get_instrument_multiple(instrument_id)
                    instrument_margin_ratio = self.get_instrument_margin_ratio(instrument_id)
                    current_margin = i['OpenPrice'] * i['Volume'] * instrument_multiple * instrument_margin_ratio
                    j = {
                        'UserID': i['InvestorID'],
                        'TradingDay': i['OpenDate'],  # 开仓交易日
                        # 'OrderRef': i['OrderRef'],
                        'InstrumentID': i['InstrumentID'],
                        'Direction': i['Direction'],
                        'OffsetFlag': '0',  # 持仓单全部定义为开仓标志
                        'HedgeFlag': i['HedgeFlag'],
                        'Price': i['OpenPrice'],
                        'ExchangeID': i['ExchangeID'],
                        'TradeDate': i['OpenDate'],  # 开仓的交易日
                        'Volume': i['Volume'],
                        'CurrMargin': current_margin,
                        'LastSettlementPrice': i['LastSettlementPrice']
                    }
                    self.__qry_investor_position_detail.append(j)
            print("User.__init__() user_id=", self.__user_id, 'self.__qry_investor_position_detail，长度', len(self.__qry_investor_position_detail), self.__qry_investor_position_detail)
        else:
            self.__dict_create_user_status[
                'QryInvestorPositionDetail'] = self.__QryInvestorPositionDetail
            print("User.__init__() user_id=", self.__user_id, '查询投资者持仓明细失败', self.__QryInvestorPositionDetail)

    # 查询合约信息
    def qry_instrument_info(self):
        # 查询合约，所有交易所的所有合约
        self.qry_api_interval_manager()  # API查询时间间隔管理
        self.__QryInstrument = Utils.code_transform(self.__trader_api.QryInstrument())
        if isinstance(self.__QryInstrument, list):
            if len(self.__QryInstrument) > 0:
                self.__dict_create_user_status['QryInstrument'] = 0
                # print("User.qry_instrument_info() user_id=", self.__user_id, "查询合约信息成功", self.__QryInstrument)

                dict_msg = {
                    'DataFlag': 'QryInstrument',
                    'UserId': self.__user_id,
                    'DataMain': self.__QryInstrument  # 最新策略统计
                }
                # print(">>> User.qry_instrument_info() user_id =", self.__user_id, 'data_flag = QryInstrument', 'data_msg =', dict_msg)
                self.__Queue_user.put(dict_msg)
            else:
                self.__dict_create_user_status['QryInstrument'] = self.__QryInstrument
                print("User.qry_instrument_info() user_id=", self.__user_id, "查询合约信息失败", self.__QryInstrument)
        else:
            self.__dict_create_user_status['QryInstrument'] = self.__QryInstrument
            print("User.qry_instrument_info() user_id=", self.__user_id, "查询合约信息失败", self.__QryInstrument)

    # API查询操作管理，记录最后一次查询时间，且与上一次查询时间至少间隔一秒，该方法放置位置在对api查询之前
    def qry_api_interval_manager(self):
        time_interval = time.time() - self.__qry_api_last_time
        if time_interval < 1.0:
            time.sleep(1-time_interval)
        self.__qry_api_last_time = time.time()

    """
    # 装载xml数据
    def load_xml(self):
        # 如果从本地硬盘中正常获取到xml
        if self.__ctp_manager.get_XML_Manager().get_read_xml_status():
            self.__list_statistics = list()  # 从xml文件读取的期货账户维护的统计指标
            for i in self.__ctp_manager.get_XML_Manager().get_list_user_statistics():
                if i['user_id'] == self.__user_id:
                    self.__list_statistics.append(i)  # user对象统计数据list装载xml数据
            # 从xml中取出的数据格式：
            # [{'action_count': 0, 'user_id': '078681', 'instrument_id': 'cu1705', 'open_count': 0},
            #  {'action_count': 0, 'user_id': '078681', 'instrument_id': 'cu1710', 'open_count': 0} ]

            # 将xml中取出的user统计数据，赋值给对应的策略对象
            for obj_strategy in self.__list_strategy:  # 遍历user下的策略对象列表
                for dict_statistics in self.__list_statistics:  # 遍历user下的统计数据列表
                    if dict_statistics['instrument_id'] == obj_strategy.get_a_instrument_id():  # i = 'cu1705'
                        obj_strategy.set_a_action_count(dict_statistics['action_count'])
                        obj_strategy.set_a_open_count(dict_statistics['open_count'])
                    elif dict_statistics['instrument_id'] == obj_strategy.get_b_instrument_id():
                        obj_strategy.set_b_action_count(dict_statistics['action_count'])
                        obj_strategy.set_b_open_count(dict_statistics['open_count'])
    """

    # 组织从xml获取到的数据
    def load_xml_data(self, dict_arguments):
        # 从本地xml文件获取数据
        self.__xml_exist = dict_arguments['xml']['xml_exist']  # xml读取是否成功
        print("User.load_xml_data() user_id =", self.__user_id, "self.__xml_exist =", self.__xml_exist)
        if self.__xml_exist:
            # 从xml获取到的xml读取状态信息
            self.__xml_dict_user_save_info = dict_arguments['xml']['dict_user_save_info']
            print("User.load_xml_data() self.__xml_dict_user_save_info =", self.__xml_dict_user_save_info)
            # 从xml获取到的list_strategy_arguments
            self.__xml_list_strategy_arguments = dict_arguments['xml']['list_strategy_arguments']
            print("User.load_xml_data() self.__xml_list_strategy_arguments =", self.__xml_list_strategy_arguments)
            # 从xml获取到的list_strategy_statistics
            self.__xml_list_strategy_statistics = dict_arguments['xml']['list_strategy_statistics']
            print("User.load_xml_data() self.__xml_list_strategy_statistics =", self.__xml_list_strategy_statistics)
            # 从xml获取到的list_user_instrument_statistics
            self.__xml_list_user_instrument_statistics = dict_arguments['xml']['list_user_instrument_statistics']
            print("User.load_xml_data() self.__xml_list_user_instrument_statistics =",
                  self.__xml_list_user_instrument_statistics)
            # 从xml获取到的list_position_detail_for_order
            self.__xml_list_position_detail_for_order = dict_arguments['xml']['list_position_detail_for_order']
            print("User.load_xml_data() self.__xml_list_position_detail_for_order =",
                  self.__xml_list_position_detail_for_order)
            # 从xml获取到的list_position_detail_for_trade
            self.__xml_list_position_detail_for_trade = dict_arguments['xml']['list_position_detail_for_trade']
            print("User.load_xml_data() self.__xml_list_position_detail_for_trade =",
                  self.__xml_list_position_detail_for_trade)

    # 组织从server获取到的数据
    def load_server_data(self, dict_arguments):
        # 从服务端获取到的trader_info
        self.__server_dict_trader_info = dict_arguments['server']['trader_info']
        # 从服务端获取到的user_info
        self.__server_dict_user_info = dict_arguments['server']['user_info']
        self.__user_id = self.__server_dict_user_info['userid']
        print("User.load_server_data() user_id =", self.__user_id)
        print("User.load_server_data() self.__server_dict_user_info =", self.__server_dict_user_info)
        # 从服务端获取到的market_info
        self.__server_dict_market_info = dict_arguments['server']['market_info']
        print("User.load_server_data() self.__server_dict_market_info =", self.__server_dict_market_info)
        # 从服务端获取到的strategy_info
        self.__server_list_strategy_info = dict_arguments['server']['strategy_info']
        print("User.load_server_data() self.__server_list_strategy_info =", self.__server_list_strategy_info)
        # 从服务端获取到的list_position_detail_for_order
        self.__server_list_position_detail_for_order_yesterday = dict_arguments['server']['list_position_detail_for_order']
        print("User.load_server_data() self.__server_list_position_detail_for_order_yesterday =",
              self.__server_list_position_detail_for_order_yesterday)
        # 从服务端获取到的list_position_detail_for_trade
        self.__server_list_position_detail_for_trade_yesterday = dict_arguments['server']['list_position_detail_for_trade']
        print("User.load_server_data() self.__server_list_position_detail_for_trade_yesterday =", self.__server_list_position_detail_for_trade_yesterday)
        # 从服务端获取到的list_position_detail_for_order_today
        self.__server_list_position_detail_for_order_today = dict_arguments['server']['list_position_detail_for_order_today']
        print("User.load_server_data() self.__server_list_position_detail_for_order_today =", self.__server_list_position_detail_for_order_today)
        # 从服务端获取到的list_position_detail_for_trade_today
        self.__server_list_position_detail_for_trade_today = dict_arguments['server']['list_position_detail_for_trade_today']
        print("User.load_server_data() self.__server_list_position_detail_for_trade_today =", self.__server_list_position_detail_for_trade_today)

        self.__trader_id = self.__server_dict_user_info['traderid']
        self.__user_id = self.__server_dict_user_info['userid']
        self.__BrokerID = self.__server_dict_user_info['brokerid']
        self.__Password = self.__server_dict_user_info['password']
        self.__FrontAddress = self.__server_dict_user_info['frontaddress']
        self.__on_off = self.__server_dict_user_info['on_off']  # 期货账户交易开关

    # 根据xml导入数据情况判断TdApi启动模式:RESTART、RESUME
    def tdapi_start_model(self):
        self.__TdApi_start_model = PyCTP.THOST_TERT_RESTART  # 初始化启动模式为RESTART，如果xml文件存在且数据可用为RESUME
        if self.__xml_exist:
            market_TradingDay = '-'.join([self.__MdApi_TradingDay[:4], self.__MdApi_TradingDay[4:6], self.__MdApi_TradingDay[6:]])
            # print(">>> User.tdapi_start_model() self.__xml_dict_user_save_info =", self.__xml_dict_user_save_info)
            # 如果xml数据中未找到对应期货账号的user_save_info信息，模式设置为RESTART
            if len(self.__xml_dict_user_save_info) == 0:
                self.__TdApi_start_model = PyCTP.THOST_TERT_RESTART  # 从今天开盘到现在的数据
            else:
                # 正常保存，且保存日期是当前交易日
                if self.__xml_dict_user_save_info[0]['status'] == 'True' \
                        and self.__xml_dict_user_save_info[0]['tradingday'] == market_TradingDay:
                    self.__TdApi_start_model = PyCTP.THOST_TERT_RESUME  # 从上次断开连接到现在的数据
                else:
                    self.__TdApi_start_model = PyCTP.THOST_TERT_RESTART  # 从今天开盘到现在的数据
        else:
            self.__TdApi_start_model = PyCTP.THOST_TERT_RESTART  # 从今天开盘到现在的数据
        print("User.tdapi_start_model() user_id =", self.__user_id, ", self.__TdApi_start_model =",
              self.__TdApi_start_model, ", PyCTP.THOST_TERT_RESUME =", PyCTP.THOST_TERT_RESUME,
              ", PyCTP.THOST_TERT_RESTART =", PyCTP.THOST_TERT_RESTART)

    # 初始化期货账户合约统计：撤单次数和开仓手数
    def init_instrument_statistics(self):
        if self.__TdApi_start_model == PyCTP.THOST_TERT_RESUME:  # 装载xml数据，并将数据发送给main进程
            for i in self.__xml_list_user_instrument_statistics:
                if i['user_id'] == self.__user_id:
                    instrument_id = i['instrument_id']
                    self.__dict_instrument_statistics[instrument_id] = {
                        'action_count': i['action_count'],
                        'open_count': i['open_count']
                    }
        elif self.__TdApi_start_model == PyCTP.THOST_TERT_RESTART:
            pass
        dict_data = {
            'DataFlag': 'instrument_statistics',
            'UserId': self.__user_id,
            'DataMain': self.__dict_instrument_statistics
        }
        print("User.init_instrument_statistics() 进程通信user->main，user_id =", self.__user_id, 'data_flag = instrument_statistics', 'dict_data =', dict_data)
        self.__Queue_user.put(dict_data)  # user进程put，main进程get

    # user进程收到主进程放到Queue的数据
    def handle_Queue_get(self, dict_data):
        print(">>> User.handle_Queue_get() 进程通信main->user，user_id =", self.__user_id, "dict_data =", dict_data)
        # 修改交易员开关，"MsgType":8
        if dict_data['MsgType'] == 8:
            self.set_trader_on_off(dict_data['OnOff'])
        # 修改期货账户开关，"MsgType":9
        elif dict_data['MsgType'] == 9:
            self.set_on_off(dict_data['OnOff'])
        # 新建策略，"MsgType":6
        elif dict_data['MsgType'] == 6:
            self.create_strategy(dict_data['Info'][0])
        # 删除策略，"MsgType":7
        elif dict_data['MsgType'] == 7:
            # strategy_id = dict_data['Info'][0]['strategy_id']
            # dict_position = self.__dict_strategy[strategy_id].get_position()
            # sum_position = 0
            # for i in dict_position:
            #     sum_position += dict_position[i]
            # if sum_position != 0:
            #     print("User.handle_Queue_get() user_id =", self.__user_id, "strategy_id =", strategy_id)
            self.delete_strategy(dict_data['StrategyID'])
        # 修改策略开关，"MsgType":13
        elif dict_data['MsgType'] == 13:
            strategy_id = dict_data['StrategyID']
            on_off = dict_data['OnOff']
            self.__dict_strategy[strategy_id].set_on_off(on_off)
        # 修改单个策略参数(不带持仓修改)，"MsgType": 5
        elif dict_data['MsgType'] == 5:
            strategy_id = dict_data['Info'][0]['strategy_id']
            dict_args = dict_data['Info'][0]
            self.__dict_strategy[strategy_id].set_arguments(dict_args)
        # 修改单个策略持仓，"MsgType": 12
        elif dict_data['MsgType'] == 12:
            strategy_id = dict_data['Info'][0]['strategy_id']
            dict_args = dict_data['Info'][0]
            self.__dict_strategy[strategy_id].set_list_position_detail(dict_args)  # 设置持仓明细
            # self.__dict_strategy[strategy_id].set_position(dict_args)  # 设置持仓变量
        # 查询策略
        # 界面点击“查询”按钮触发的特殊进程间通信
        elif dict_data['MsgType'] == 91:
            print(">>> User.handle_Queue_get() 进程通信main->user，user_id =", self.__user_id, "界面点击“查询”按钮触发的特殊进程间通信", dict_data)
            # 91:保存OnRtnOrder、OnRtnTrade
            # for strategy_id in self.__dict_strategy:
                # self.__dict_strategy[strategy_id].save_df_order_trade()
                # pass
            user_id = dict_data['UserID']
            strategy_id = dict_data['StrategyID']
            self.action_for_UI_query()
            self.__dict_strategy[strategy_id].action_for_UI_query()

    # 创建策略实例
    def create_strategy(self, dict_args):
        strategy_id = dict_args['strategy_id']
        obj_strategy = Strategy(dict_args, self)
        self.__dict_strategy[strategy_id] = obj_strategy  # 保存strategy对象的dict，由user对象维护
        self.__dict_strategy_finished[strategy_id] = False  # 初始化“策略完成初始化”为False
        self.__market_manager.set_dict_strategy(self.__dict_strategy)  # 将策略对象dict设置为market_manager属性
        # print(">>>>>>>>>> dict_args['list_instrument_id'] =", dict_args['list_instrument_id'])
        list_instrument_id = [dict_args['a_instrument_id'], dict_args['b_instrument_id']]
        self.__market_manager.sub_market(list_instrument_id, dict_args['user_id'], dict_args['strategy_id'])

    # 删除策略
    def delete_strategy(self, strategy_id):
        # 退订行情
        obj_strategy = self.__dict_strategy[strategy_id]
        list_instrument_id = obj_strategy.get_list_instrument_id()
        user_id = obj_strategy.get_user_id()
        print(">>> User.delete_strategy() user_id =", self.__user_id, "strategy_id =", strategy_id, "调用了删除策略，退订行情方法")
        self.__market_manager.un_sub_market(list_instrument_id, user_id, strategy_id)
        # 删除策略之前需判断：策略开关关闭、空仓
        self.__dict_strategy.pop(strategy_id)
        # self.__market_manager.set_dict_strategy(self.__dict_strategy)  # 将策略对象dict设置为market_manager属性

    # 设置策略初始化完成标志
    def set_strategy_init_finished(self, strategy_id, bool_finished):
        self.__dict_strategy_finished[strategy_id] = bool_finished
        all_strategy_finished = True
        for i_strategy_id in self.__dict_strategy_finished:
            if self.__dict_strategy_finished[i_strategy_id] is False:
                all_strategy_finished = False
        if all_strategy_finished:
            dict_msg = {
                'DataFlag': 'all_strategy_finished',
                'UserId': self.__user_id,
                'DataMain': True  # 最新策略参数
            }
            print(">>> Strategy.set_arguments() user_id =", self.__user_id, 'data_flag =', 'all_strategy_finished',
                  'data_msg =', dict_msg)
            self.__Queue_user.put(dict_msg)

    # 获取从server中获取的数据
    def get_server_list_position_detail_for_order_yesterday(self):
        return self.__server_list_position_detail_for_order_yesterday

    # 获取从server中获取的数据
    def get_server_list_position_detail_for_trade_yesterday(self):
        return self.__server_list_position_detail_for_trade_yesterday

    # 获取从server中获取的数据
    def get_server_list_position_detail_for_order_today(self):
        return self.__server_list_position_detail_for_order_today

    # 获取从server中获取的数据
    def get_server_list_position_detail_for_trade_today(self):
        return self.__server_list_position_detail_for_trade_today

    # 获取从xml中读取的数据
    def get_dict_user_write_xml_status(self):
        return self.__xml_dict_user_save_info

    # 获取从xml中读取的数据
    def get_xml_list_strategy_arguments(self):
        return self.__xml_list_strategy_arguments

    # 获取从xml中读取的数据
    def get_xml_list_strategy_statistics(self):
        return self.__xml_list_strategy_statistics

    def get_xml_list_user_instrument_statistics(self):
        return self.__xml_list_user_instrument_statistics

    # 获取从xml中读取的数据
    def get_xml_list_position_detail_for_order(self):
        return self.__xml_list_position_detail_for_order

    # 获取从xml中读取的数据
    def get_xml_list_position_detail_for_trade(self):
        return self.__xml_list_position_detail_for_trade

    # 将CTPManager类设置为user的属性
    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager

    # 获取CTPManager属性
    def get_CTPManager(self):
        return self.__ctp_manager

    # 获取行情端口交易日
    def get_MdApi_TradingDay(self):
        return self.__MdApi_TradingDay

    # 获取TdApi初始化方式：PyCTP.THOST_TERT_RESUME = 1 , PyCTP.THOST_TERT_RESTART = 0
    def get_TdApi_start_model(self):
        return self.__TdApi_start_model

    # 设置数据库管理类DBManager为该类对象
    def set_DBManager(self, obj_DBManager):
        self.__DBManager = obj_DBManager

    # QAccountWidegt设置为属性
    def set_QAccountWidget_signal(self, obj_QAccountWidget):
        self.__QAccountWidget_signal = obj_QAccountWidget

    def get_QAccountWidget_signal(self):
        return self.__QAccountWidget_signal

    # QAccountWidegtTotal设置为属性（总账户的窗口）
    def set_QAccountWidget_total(self, obj_QAccountWidgetTotal):
        self.__QAccountWidget_total = obj_QAccountWidgetTotal

    def get_QAccountWidget_total(self):
        return self.__QAccountWidget_total

    # 获得数据库
    def get_mongodb_CTP(self):
        return self.__mongo_client.CTP

    # 获取进程间通信Queue结构:main->user
    def get_Queue_main(self):
        return self.__Queue_main

    # 获取进程间通信Queue结构:user->main
    def get_Queue_user(self):
        return self.__Queue_user

    # 从数据库获取user的strategy参数集合
    def get_col_strategy(self):
        return self.__mongo_client.CTP.get_collection(self.__user_id+'_strategy')

    # 从数据库获取user的持仓汇总集合
    def get_col_position(self):
        return self.__mongo_client.CTP.get_collection(self.__user_id+'_position')

    # 从数据库获取user的持仓明细集合
    def get_col_position_detail(self):
        return self.__mongo_client.CTP.get_collection(self.__user_id+'_position_detail')

    # 从数据库获取user的trade集合
    def get_col_trade(self):
        return self.__mongo_client.CTP.get_collection(self.__user_id+'_trade')

    # 从数据库获取user的order列表
    def get_col_order(self):
        return self.__mongo_client.CTP.get_collection(self.__user_id + '_order')

    def get_read_xml_status(self):
        return self.__read_xml_status

    def set_read_xml_status(self, bool_input):
        self.__read_xml_status = bool_input

    # 获取期货账号
    def get_user_id(self):
        return self.__user_id

    # 获取交易员id
    def get_trader_id(self):
        return self.__trader_id

    # 获取trade实例(TD)
    def get_trader_api(self):
        return self.__trader_api

    # 获取self.__instrument_info
    def get_instrument_info(self):
        return self.__QryInstrument

    # 设置user的交易开关，0关、1开
    def set_on_off(self, int_on_off):
        print("User.set_on_off() user_id=", self.__user_id, "设置交易账户开关：", int_on_off)
        self.__on_off = int_on_off
        # self.signal_update_pushButton_start_strategy.emit()  # 触发信号：内核设置期货账户交易开关 -> 更新窗口“开始策略”按钮状态

    # 设置trader的交易开关，0关、1开
    def set_trader_on_off(self, int_on_off):
        print("User.set_trader_on_off() user_id =", self.__user_id, "设置交易员开关：", int_on_off)
        self.__trader_on_off = int_on_off

    # 获取user的交易开关，0关、1开
    def get_on_off(self):
        return self.__on_off

    # # 设置user的交易开关，0关、1开
    # def set_only_close(self, int_only_close):
    #     self.__only_close = int_only_close
    #
    # # 获取user的交易开关，0关、1开
    # def get_only_close(self):
    #     return self.__only_close

    # 设置user初始化状态
    def set_init_finished(self, bool_input):
        self.__init_finished = bool_input
        # 进程间通信：'DataFlag': 'instrument_statistics'
        dict_data = {
            'DataFlag': 'user_init_finished',
            'UserId': self.__user_id,
            'DataMain': 'True'
        }
        self.__Queue_user.put(dict_data)  # user进程put，main进程get

    # 获取user初始化状态
    def get_init_finished(self):
        return self.__init_finished

    # 获取交易日
    def GetTradingDay(self):
        return self.__TradingDay

    # 获取用户自己维护的账户资金情况
    def get_dict_trading_account(self):
        return self.__dict_trading_account

    # 获取从TdApi获取到的账户资金情况数据接口
    def get_QryTradingAccount(self):
        return self.__QryTradingAccount

    # 获取界面tableWidget窗口更新所需的数据,单个策略数据为一个list,所有策略的数据合并为一个list
    def get_table_widget_data(self):
        list_table_widget_data = []  # 一个user下面所有的策略数据
        for strategy_id in self.__dict_strategy:
            list_strategy_data = []  # 单个策略数据
            strategy_arguments = self.__dict_strategy[strategy_id].get_arguments()
            strategy_position = self.__dict_strategy[strategy_id].get_position()
            strategy_statistics = self.__dict_strategy[strategy_id].get_statistics()
            a_instrument_id = strategy_arguments['a_instrument_id']
            b_instrument_id = strategy_arguments['b_instrument_id']
            min_move = self.__dict_strategy[strategy_id].get_price_tick(a_instrument_id)
            list_strategy_data.append(strategy_arguments['on_off'])  # 0:策略开关
            list_strategy_data.append(strategy_arguments['user_id'])  # 1:期货账号
            list_strategy_data.append(strategy_arguments['strategy_id'])  # 2:策略编号
            list_strategy_data.append(','.join([a_instrument_id, b_instrument_id]))  # 3:交易合约
            list_strategy_data.append(str(strategy_position['position']))  # 4:总持仓，核对正确
            list_strategy_data.append(str(strategy_position['position_b_sell']))  # 5:买持仓=B总卖，正确
            list_strategy_data.append(str(strategy_position['position_b_buy']))  # 6:卖持仓=B总买，正确
            list_strategy_data.append(round(strategy_statistics['current_margin']))  # 7:保证金
            list_strategy_data.append(round(strategy_statistics['profit_position']))  # 8:持仓盈亏
            list_strategy_data.append(round(strategy_statistics['profit_close']))  # 9:平仓盈亏
            list_strategy_data.append(round(strategy_statistics['commission']))  # 10:手续费
            list_strategy_data.append(round(strategy_statistics['profit']))  # 11:净盈亏
            list_strategy_data.append(strategy_statistics['total_traded_count'])  # 12:成交量=A成交手数+B成交手数，正确
            list_strategy_data.append(strategy_statistics['total_traded_amount'])  # 13:成交金额=A成交金额+B成交金额，正确
            list_strategy_data.append(round(strategy_statistics['a_trade_rate'], 2))  # 14:A成交率=A成交手数/A委托手数，错误
            list_strategy_data.append(round(strategy_statistics['b_trade_rate'], 2))  # 15:B成交率=B成交手数/B委托手数，错误
            list_strategy_data.append(strategy_arguments['trade_model'])  # 16:交易模型
            list_strategy_data.append(strategy_arguments['order_algorithm'])  # 17:下单算法
            # list_strategy_data的后半部分放oupBox更新所需数据
            list_strategy_data.append(str(strategy_arguments['lots']))  # 18: 总手
            list_strategy_data.append(str(strategy_arguments['lots_batch']))  # 19: 每份
            list_strategy_data.append(strategy_arguments['stop_loss'])  # 20: 价差止损
            list_strategy_data.append(strategy_arguments['spread_shift'])  # 21: 超价触发
            list_strategy_data.append(strategy_arguments['a_wait_price_tick'])  # 22: A撤单等待
            list_strategy_data.append(strategy_arguments['a_limit_price_shift'])  # 23: A报单偏移
            list_strategy_data.append(strategy_arguments['b_wait_price_tick'])  # 24:B报单等待
            list_strategy_data.append(strategy_arguments['b_limit_price_shift'])  # 25:B报单偏移
            list_strategy_data.append(str(strategy_arguments['a_order_action_limit']))  # 26:A撤单限制
            list_strategy_data.append(str(strategy_arguments['b_order_action_limit']))  # 27:B撤单限制
            if a_instrument_id in self.__dict_instrument_statistics:
                a_action_count = self.__dict_instrument_statistics[a_instrument_id]['action_count']
            else:
                a_action_count = 0
            if b_instrument_id in self.__dict_instrument_statistics:
                b_action_count = self.__dict_instrument_statistics[b_instrument_id]['action_count']
            else:
                b_action_count = 0
            str_a_action = '/'.join([str(strategy_statistics['a_action_count_strategy']), str(a_action_count)])
            str_b_action = '/'.join([str(strategy_statistics['b_action_count_strategy']), str(b_action_count)])
            list_strategy_data.append(str_a_action)  # 28:A撤单次数, 内容：“本策略A合约撤单次数/期货账户A合约撤单次数”
            list_strategy_data.append(str_b_action)  # 29:B撤单次数, 内容：“本策略B合约撤单次数/期货账户B合约撤单次数”
            list_strategy_data.append(str(strategy_position['position_a_sell']))  # 30:A总卖
            list_strategy_data.append(str(strategy_position['position_a_sell_yesterday']))  # 31:A昨卖
            list_strategy_data.append(str(strategy_position['position_a_buy']))  # 32:A总买
            list_strategy_data.append(str(strategy_position['position_a_buy_yesterday']))  # 33:A昨买
            list_strategy_data.append(str(strategy_position['position_b_sell_yesterday']))  # 34:B昨卖
            list_strategy_data.append(str(strategy_position['position_b_buy_yesterday']))  # 35:B昨买
            list_strategy_data.append(min_move)  # 36:最小跳价
            list_strategy_data.append(strategy_arguments['sell_open'])  # 37:卖开
            list_strategy_data.append(strategy_arguments['buy_close'])  # 38:买平
            list_strategy_data.append(strategy_arguments['sell_close'])  # 39:卖平
            list_strategy_data.append(strategy_arguments['buy_open'])  # 40:买开
            list_strategy_data.append(strategy_arguments['sell_open_on_off'])  # 41:卖开-开关
            list_strategy_data.append(strategy_arguments['buy_close_on_off'])  # 42:买平-开关
            list_strategy_data.append(strategy_arguments['sell_close_on_off'])  # 43:卖平-开关
            list_strategy_data.append(strategy_arguments['buy_open_on_off'])  # 44:买开-开关
            list_strategy_data.append(strategy_arguments['a_instrument_id'])  # 45:A合约代码
            list_strategy_data.append(strategy_arguments['b_instrument_id'])  # 46:B合约代码
            list_strategy_data.append(strategy_arguments['instrument_a_scale'])  # 47:A合约乘数
            list_strategy_data.append(strategy_arguments['instrument_b_scale'])  # 48:B合约乘数
            list_table_widget_data.append(list_strategy_data)
        list_table_widget_data = sorted(list_table_widget_data, key=itemgetter(2))
        return list_table_widget_data

    # 获取界面panel_show_account_data(账户资金条)更新所需的数据,一个user的数据是一个list，（所有策略实例数据综合）
    # def get_panel_show_account_data(self):
    #     list_panel_show_account_data = list()
    #     profit_position = 0  # 所有策略持仓盈亏求和
    #     profit_close = 0  # 所有策略平仓盈亏求和
    #     commission = 0  # 所有策略手续费求和
    #     used_margin = 0  # 所有策略占用保证金求和
    #     for strategy_id in self.__dict_strategy:
    #         # print(">>> User.get_panel_show_account_data() user_id =", self.__user_id, "strategy_id =", strategy_id, "调用get_statistics()")
    #         strategy_statistics = self.__dict_strategy[strategy_id].get_statistics()
    #         profit_position += strategy_statistics['profit_position']  # 持仓盈亏
    #         profit_close += strategy_statistics['profit_close']  # 平仓盈亏
    #         commission += strategy_statistics['commission']  # 手续费
    #         used_margin += strategy_statistics['current_margin']  # 保证金
    #     # 动态权益 = 静态权益 + 入金 - 出金 + 持仓盈亏 + 平仓盈亏 - 手续费
    #     variable_equity = self.__QryTradingAccount['PreBalance'] \
    #                       + self.__QryTradingAccount['Deposit'] - self.__QryTradingAccount['Withdraw'] \
    #                       + profit_position + profit_close - commission
    #     # 可用资金 = 动态权益 - 占用保证金
    #     available_equity = variable_equity - used_margin
    #     # 风险度 = 占用保证金 / 动态权益
    #     risk = str(round((used_margin / variable_equity) * 100)) + '%'
    #     list_panel_show_account_data.append(str(round(variable_equity)))  # 动态权益
    #     list_panel_show_account_data.append(str(round(self.__QryTradingAccount['PreBalance'])))  # 静态权益  ThostFtdUserApiStruct.h"上次结算准备金"
    #     list_panel_show_account_data.append(str(round(profit_position)))  # 持仓盈亏
    #     list_panel_show_account_data.append(str(round(profit_close)))  # 平仓盈亏
    #     list_panel_show_account_data.append(str(round(commission)))  # 手续费
    #     list_panel_show_account_data.append(str(round(available_equity)))  # 可用资金
    #     list_panel_show_account_data.append(str(round(used_margin)))  # 占用保证金
    #     list_panel_show_account_data.append(risk)  # 风险度
    #     list_panel_show_account_data.append(str(round(self.__QryTradingAccount['Deposit'])))  # 今日入金
    #     list_panel_show_account_data.append(str(round(self.__QryTradingAccount['Withdraw'])))  # 今日出金
    #     return list_panel_show_account_data

    # 获取界面panel_show_account_data(账户资金条)更新所需的数据,一个user的数据是一个list，（期货账户数据，包含但不限于套利系统策略数据）
    def get_panel_show_account_data_for_user(self):
        list_panel_show_account_data = list()
        profit_position = self.count_profit_position()  # 计算期货账户持仓盈亏
        used_margin = self.update_current_margin()  # 所有策略占用保证金求和
        # print(">>>User.get_panel_show_account_data_for_user() user_id =", self.__user_id, "used_margin =", used_margin)
        # print(">>> User.get_panel_show_account_data_for_user() user_id =", self.__user_id, "used_margin =", used_margin)
        # 动态权益 = 静态权益 + 入金 - 出金 + 持仓盈亏 + 平仓盈亏 - 手续费
        variable_equity = self.__QryTradingAccount['PreBalance'] \
                          + self.__QryTradingAccount['Deposit'] - self.__QryTradingAccount['Withdraw'] \
                          + profit_position + self.__profit_close - self.__commission
        # 可用资金 = 动态权益 - 占用保证金
        available_equity = variable_equity - used_margin
        # 风险度 = 占用保证金 / 动态权益
        risk = str(round((used_margin / variable_equity) * 100)) + '%'
        list_panel_show_account_data.append(round(variable_equity))  # 0:动态权益
        list_panel_show_account_data.append(round(self.__QryTradingAccount['PreBalance']))  # 1:静态权益  ThostFtdUserApiStruct.h"上次结算准备金"
        list_panel_show_account_data.append(round(profit_position))  # 2:持仓盈亏
        list_panel_show_account_data.append(round(self.__profit_close))  # 3:平仓盈亏
        list_panel_show_account_data.append(round(self.__commission + self.__commission_order))  # 4:手续费
        list_panel_show_account_data.append(round(available_equity))  # 5:可用资金
        list_panel_show_account_data.append(round(used_margin))  # 6:占用保证金
        list_panel_show_account_data.append(risk)  # 7:风险度
        list_panel_show_account_data.append(round(self.__QryTradingAccount['Deposit']))  # 8:今日入金
        list_panel_show_account_data.append(round(self.__QryTradingAccount['Withdraw']))  # 9:今日出金
        # print(">>>User.get_panel_show_account_data_for_user() user_id =", self.__user_id, "list_panel_show_account_data =", list_panel_show_account_data)
        return list_panel_show_account_data

    # 定时进程间通信,将tableWidget\panel_show_account更新所需数据发给主进程
    def timer_queue_put(self):
        while True:
            dict_msg = {
                'DataFlag': 'panel_show_account_data',
                'UserId': self.__user_id,
                'DataMain': self.get_panel_show_account_data_for_user()
            }
            self.__Queue_user.put(dict_msg)  # 进程通信:发送资金账户更新信息
            dict_msg = {
                'DataFlag': 'table_widget_data',
                'UserId': self.__user_id,
                'DataMain': self.get_table_widget_data()  # 进程通信:发送策略信息
            }
            self.__Queue_user.put(dict_msg)
            time.sleep(1.0)

    # 获取报单引用，自增1，位置处于第1到第10位，共9位阿拉伯数字，user的所有策略共用
    def add_order_ref_part2(self):
        self.__order_ref_part2 += 1
        return self.__order_ref_part2

    # 添加交易策略实例，到self.__list_strategy
    # def add_strategy(self, obj_strategy):
    #     self.__list_strategy.append(obj_strategy)  # 将交易策略实例添加到本类的交易策略列表
    #     self.__trader_api.set_list_strategy(self.__list_strategy)  # 将本类的交易策略列表转发给trade
    #     obj_strategy.set_user(self)  # 将user设置为strategy属性

    # 添加合约代码到user类的self.__dict_action_counter
    # def add_instrument_id_action_counter(self, list_instrument_id):
    #     for i in list_instrument_id:
    #         if i not in self.__dict_action_counter:
    #             self.__dict_action_counter[i] = 0

    # 统计合约撤单次数，被OnRtnOrder调用，{'rb1705': {'open_count': 0, 'action_count': 0}}
    def instrument_action_count(self, Order):
        if len(Order['OrderSysID']) == 0:  # 只统计有交易所编码的order
            return
        instrument_id = Order['InstrumentID']
        if Order['OrderStatus'] == '5':  # 值为5：撤单
            if instrument_id in self.__dict_instrument_statistics:  # 已经存在的合约，撤单次数加+1
                self.__dict_instrument_statistics[instrument_id]['action_count'] += 1
            else:  # 不存在的合约，初始化开仓手数和撤单次数
                self.__dict_instrument_statistics[instrument_id] = {'action_count': 1, 'open_count': 0}
            # 撤单次数赋值到策略对象的合约撤单次数
            for strategy_id in self.__dict_strategy:
                if self.__dict_strategy[strategy_id].get_a_instrument_id() == instrument_id:
                    self.__dict_strategy[strategy_id].set_a_action_count(self.__dict_instrument_statistics[instrument_id]['action_count'])
                elif self.__dict_strategy[strategy_id].get_b_instrument_id() == instrument_id:
                    self.__dict_strategy[strategy_id].set_b_action_count(self.__dict_instrument_statistics[instrument_id]['action_count'])
            # print(">>> User.instrument_action_count() instrument_id =", instrument_id, "self.__dict_instrument_statistics[instrument_id] =", self.__dict_instrument_statistics[instrument_id])

    # 统计合约开仓手数，被OnRtnTrade调用，{'rb1705': {'open_count': 0, 'action_count': 0}}
    def instrument_open_count(self, Trade):
        instrument_id = Trade['InstrumentID']
        if instrument_id in self.__dict_instrument_statistics:  # 已经存在的合约，开仓手数叠加
            self.__dict_instrument_statistics[instrument_id]['open_count'] += Trade['Volume']
        else:  # 不存在的合约，初始化开仓手数和撤单次数
            self.__dict_instrument_statistics[instrument_id] = {'action_count': 0, 'open_count': Trade['Volume']}
        # 撤单次数赋值到策略对象的合约撤单次数
        for strategy_id in self.__dict_strategy:
            if self.__dict_strategy[strategy_id].get_a_instrument_id() == instrument_id:
                self.__dict_strategy[strategy_id].set_a_action_count(self.__dict_instrument_statistics[instrument_id]['action_count'])
            elif self.__dict_strategy[strategy_id].get_b_instrument_id() == instrument_id:
                self.__dict_strategy[strategy_id].set_b_action_count(self.__dict_instrument_statistics[instrument_id]['action_count'])

    # 删除交易策略实例，从self.__list_strategy
    def del_strategy(self, strategy_id):
        for i in self.__list_strategy:
            if i.get_strategy_id() == strategy_id:
                self.__list_strategy.remove(i)

    # 获取strategy对象的list
    def get_list_strategy(self):
        return self.__list_strategy

    # 获取strategy对象dict
    def get_dict_strategy(self):
        return self.__dict_strategy

    # 获取合约撤单次数的字典
    def get_dict_action(self):
        return self.__dict_action_counter

    # 查询行情
    def qry_depth_market_data(self, instrument_id):
        return self.__trader_api.QryDepthMarketData(instrument_id)

    # 转PyCTP_Market_API类中回调函数OnRtnOrder
    def OnRtnTrade(self, Trade):
        t = datetime.now()  # 取接收到回调数据的本地系统时间
        # print(">>>User.OnRtnTrade() Trade =", Trade)
        # Trade新增字段
        Trade['OperatorID'] = self.__trader_id  # 客户端账号（也能区分用户身份或交易员身份）:OperatorID
        Trade['StrategyID'] = Trade['OrderRef'][-2:]  # 报单引用末两位是策略编号
        Trade['ReceiveLocalTime'] = t.strftime("%Y-%m-%d %H:%M:%S %f")  # 收到回报的本地系统时间

        # self.statistics(trade=Trade)  # 统计期货账户的合约开仓手数
        self.statistics_for_trade(Trade)  # 期货账户统计，基于trade
        self.__queue_OnRtnTrade.put(Trade)  # 缓存OnRtnTrade回调数据

    # 从Queue结构取出trade的处理
    def handle_OnRtnTrade(self, trade):
        if trade['TradeDate'] > self.__date_qry_trading_account \
                or (trade['TradeDate'] == self.__date_qry_trading_account
                    and trade['TradeTime'] >= self.__time_qry_trading_account):
            self.update_list_position_detail_for_trade(trade)  # 更新user的持仓明细，同时统计平仓盈亏
            self.__commission += self.count_commission(trade)
        else:
            print("User.handle_OnRtnTrade() 过滤掉查询投资者持仓明细之前的trade，trade['Date'] =", trade['TradeDate'], "trade['TradeTime'] =", trade['TradeTime'])

    # 转PyCTP_Market_API类中回调函数OnRtnOrder
    def OnRtnOrder(self, Order):
        t = datetime.now()  #取接收到回调数据的本地系统时间
        # print(">>>User.OnRtnOrder() Order =", Order)
        self.__queue_OnRtnOrder_user.put(Order)  # 缓存期货账户的所有order
        
        # 根据字段“OrderRef”筛选出本套利系统的记录，OrderRef规则：第1位为‘1’，第2位至第10位为递增数，第11位至第12位为StrategyID
        if len(Order['OrderRef']) == 12 and Order['OrderRef'][:1] == '1':
            # Order新增字段
            Order['OperatorID'] = self.__trader_id  # 客户端账号（也能区分用户身份或交易员身份）:OperatorID
            strategy_id = Order['OrderRef'][-2:]
            Order['StrategyID'] = strategy_id  # 报单引用末两位是策略编号
            Order['ReceiveLocalTime'] = t.strftime("%Y-%m-%d %H:%M:%S %f")  # 收到回报的时间
            # Order['RecMicrosecond'] = t.strftime("%f")  # 收到回报中的时间毫秒

            self.instrument_action_count(Order)  # 统计合约撤单次数

            # 进程间通信：'DataFlag': 'instrument_statistics'
            # dict_data = {
            #     'DataFlag': 'instrument_statistics',
            #     'UserId': self.__user_id,
            #     'DataMain': self.__dict_instrument_statistics
            # }
            # self.__Queue_user.put(dict_data)  # user进程put，main进程get

            # # 进程间通信：'DataFlag': 'OnRtnOrder'
            # dict_data = {
            #     'DataFlag': 'OnRtnOrder',
            #     'UserId': self.__user_id,
            #     'DataMain': Order
            # }
            # self.__Queue_user.put(dict_data)  # user进程put，main进程get

            # 缓存，待提取，提取发送给特定strategy对象
            self.__queue_OnRtnOrder.put_nowait(Order)  # 缓存OnRtnTrade回调数据，本套利系统的order
            # self.__dict_strategy[strategy_id].OnRtnOrder(Order)
        else:
            print("User.OnRtnOrder() 异常 user_id =", self.__user_id, "过滤掉非小蜜蜂套利系统的order")

    def OnErrRtnOrderInsert(self, InputOrder, RspInfo):
        """报单录入错误回报"""
        # print('PyCTP_Trade.OnErrRtnOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo)
        # if InputOrder is not None:
        #     InputOrder = Utils.code_transform(InputOrder)
        # if RspInfo is not None:
        #     RspInfo = Utils.code_transform(RspInfo)
        # if Utils.PyCTP_Trade_API_print:
        #     print('PyCTP_Trade.OnErrRtnOrderInsert()', 'InputOrder:', InputOrder, 'RspInfo:', RspInfo)
        # self.__user.OnErrRtnOrderInsert(InputOrder, RspInfo)  # 转到user回调函数
        # for i in self.__user.get_list_strategy():  # 转到strategy回调函数
        #     if InputOrder['OrderRef'][-2:] == i.get_strategy_id():
        #         i.OnErrRtnOrderInsert(InputOrder, RspInfo)
        strategy_id = InputOrder['OrderRef'][-2:]
        if strategy_id in self.__dict_strategy:
            self.__dict_strategy[strategy_id].OnErrRtnOrderInsert(InputOrder, RspInfo)

    # 转行情回调
    def OnRtnDepthMarketData(self, tick):
        instrument_id = tick['InstrumentID']
        self.__dict_last_tick[instrument_id] = tick
        # print(">>> User.OnRtnDepthMarketData() tick =", tick['InstrumentID'], tick)
        # print(">>> User.OnRtnDepthMarketData() user_id =", self.__user_id, "len(self.__dict_last_tick) =", len(self.__dict_last_tick))

    # 处理OnRtnOrder的线程
    def threading_run_OnRtnOrder(self):
        print(">>> User.threading_run_OnRtnOrder() user_id =", self.__user_id)
        while True:
            order = self.__queue_OnRtnOrder.get()
            # print(">>> User.threading_run_OnRtnOrder() user_id =", self.__user_id, "order =", order)
            for strategy_id in self.__dict_strategy:
                if order['StrategyID'] == self.__dict_strategy[strategy_id].get_strategy_id():
                    self.__dict_strategy[strategy_id].OnRtnOrder(order)

    # 统计申报费线程
    def threading_count_commission_order(self):
        while True:
            Order = self.__queue_OnRtnOrder_user.get()
            # 计算申报费
            if Order['InsertDate'] > self.__date_qry_trading_account \
                    or (Order['InsertDate'] == self.__date_qry_trading_account
                        and Order['InsertTime'] >= self.__time_qry_trading_account):
                self.count_commission_order(Order)
            else:
                print("User.handle_OnRtnTrade() 过滤掉查询投资者持仓明细之前的trade，Order['InsertDate'] =", Order['InsertDate'],
                      "Order['InsertTime'] =", Order['InsertTime'])
                # self.count_commission_order(Order)

    # 处理OnRtnTrade的线程
    def threading_run_OnRtnTrade(self):
        print(">>> User.threading_run_OnRtnTrade() user_id =", self.__user_id)
        while True:
            trade = self.__queue_OnRtnTrade.get()
            self.process_trade_offset_flag(trade)  # 如果平仓标志位为1，则根据持仓明细转换为3或4
            # print(">>> User.threading_run_OnRtnTrade() user_id =", self.__user_id, "trade =", trade)
            # 过滤出本套利系统的trade，并将trade传给Strategy对象
            if len(trade['OrderRef']) == 12 and trade['OrderRef'][:1] == '1':
                found_flag = False
                for strategy_id in self.__dict_strategy:
                    if trade['StrategyID'] == self.__dict_strategy[strategy_id].get_strategy_id():
                        self.__dict_strategy[strategy_id].OnRtnTrade(trade)
                        found_flag = True
                if not found_flag:
                    print("User.threading_run_OnRtnTrade() 异常 user_id =", self.__user_id, "trade未传递给策略对象,Trade结构体中StrategyID=", trade['StrategyID'])
            self.handle_OnRtnTrade(trade)  # User的trade运算
            # self.update_list_position_detail_for_trade(trade)  # 更新user的持仓明细
            # self.__commission += self.count_commission(trade)

    # 将order和trade记录保存到本地
    def save_df_order_trade(self):
        str_user_id = self.__user_id
        str_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
        order_file_path = "data/order_" + str_user_id + "_" + str_time + '.csv'
        trade_file_path = "data/trade_" + str_user_id + "_" + str_time + '.csv'
        log_file_path = "data/log_" + str_user_id + "_" + str_time + '.csv'
        # qry_order_file_path = "data/qry_order_" + str_user_id + "_" + str_time + '.csv'
        # qry_trade_file_path = "data/qry_trade_" + str_user_id + "_" + str_time + '.csv'
        print(">>> PyCTP_Trade.save_df_order_trade() order_file_path =", order_file_path)
        print(">>> PyCTP_Trade.save_df_order_trade() trade_file_path =", trade_file_path)
        print(">>> PyCTP_Trade.save_df_order_trade() log_file_path =", log_file_path)
        self.__df_order.to_csv(order_file_path)
        self.__df_trade.to_csv(trade_file_path)
        self.__df_log.to_csv(log_file_path)
        # self.__df_qry_order.to_csv(qry_order_file_path)
        # self.__df_qry_trade.to_csv(qry_trade_file_path)

    # 转PyCTP_Market_API类中回调函数QryTrade
    def QryTrade(self):
        list_QryTrade = self.__trader_api.QryTrade()  # 正确返回值为list类型，否则为异常
        self.__list_QryTrade = list()  # 保存本套利系统的Trade记录
        if isinstance(list_QryTrade, list):
            list_QryTrade = Utils.code_transform(list_QryTrade)
            print("User.QryTrade() QryTrade成功，len(list_QryTrade) =", len(list_QryTrade))
        else:
            print("User.QryTrade() QryTrade失败，返回值 =", list_QryTrade)
            return
        # print(">>> User.QryTrade() QryTrade从api获得的样本数 =", len(list_QryTrade))
        # 筛选条件：OrderRef第一位为1，长度为12
        for i in list_QryTrade:
            if len(i['OrderRef']) == 12 and i['OrderRef'][:1] == '1':
                i['StrategyID'] = i['OrderRef'][-2:]  # 增加字段：策略编号"StrategyID"
                self.__list_QryTrade.append(i)
        # print(">>> User.QryTrade() QryTrade过滤后样本数 =", len(self.__list_QryTrade))

    # 转PyCTP_Market_API类中回调函数QryOrder
    def QryOrder(self):
        list_QryOrder = self.__trader_api.QryOrder()  # 正确返回值为list类型，否则为异常
        self.__list_QryOrder = list()  # 保存本套利系统的Order记录
        if isinstance(list_QryOrder, list):
            list_QryOrder = Utils.code_transform(list_QryOrder)
            print("User.QryTrade() QryOrder成功，len(list_QryOrder) =", len(list_QryOrder))
        else:
            print("User.QryTrade() QryOrder失败，返回值 =", list_QryOrder)
            return
        # 筛选条件：OrderRef第一位为1，长度为12
        # print(">>> User.QryOrder() QryOrder过滤前样本数 =", len(list_QryOrder))
        for i in list_QryOrder:
            self.action_counter(i)  # 撤单计数
            if len(i['OrderRef']) == 12 and i['OrderRef'][:1] == '1':
                i['StrategyID'] = i['OrderRef'][-2:]  # 增加字段：策略编号"StrategyID"
                self.__list_QryOrder.append(i)
        # print(">>> User.QryOrder() QryOrder过滤后样本数 =", len(self.__list_QryOrder))

    # 获取listQryOrder
    def get_list_QryOrder(self):
        return self.__list_QryOrder

    # 获取listQryTrade
    def get_list_QryTrade(self):
        return self.__list_QryTrade

    def get_QryTradingAccount(self):
        return self.__QryTradingAccount

    # 形参为包含字段成交量'VolumeTradedBatch'和成交价'Price'的Order结构体
    # 保存手续费的dict结构为{'cu':{'}, 'zn':{}}
    # 形参：合约代码'cu1703'，交易所代码'SHFE'
    def get_commission(self, instrument_id, exchange_id):
        # 获取品种代码，例如cu、zn
        # if exchange_id == 'SHFE':
        #     if len(instrument_id) == 6:
        #         commodity_id = instrument_id[:2]
        #     elif len(instrument_id) == 5:
        #         commodity_id = instrument_id[:1]
        # elif exchange_id in ['CFFEX', 'DZCE']:
        #     commodity_id = instrument_id[:2]
        # elif exchange_id in ['DCE']:
        #     commodity_id = instrument_id[:1]
        # else:
        #     commodity_id = ''
        #     print("User.get_commission() 异常，交易所代码在四个交易所之外 user_id =", self.__user_id, "instrument_id =", instrument_id, "exchange_id =", exchange_id)
        commodity_id = Utils.extract_commodity_id(instrument_id)
        # print(">>>User.get_commission() commodity_id =", commodity_id)

        if commodity_id not in self.__dict_commission:
            # 通过API查询单个品种的手续费率dict
            self.qry_api_interval_manager()  # API查询时间间隔管理
            # 尝试三次获取指定合约的手续费详细
            flag_get_commission_success = False  # 获取手续费率成功标志位，默认获取失败，False
            flag = 0
            while flag < 3:
                self.qry_api_interval_manager()  # API查询时间间隔管理
                list_commission = self.__trader_api.QryInstrumentCommissionRate(instrument_id.encode())
                if isinstance(list_commission, list) and len(list_commission) > 0:
                    # print(">>>User.get_commission() user_id =", self.__user_id, "list_commission =", list_commission)
                    dict_commission = Utils.code_transform(list_commission[0])
                    print("User.get_mmission() 获取手续费成功", "user_id =", self.__user_id, "instrument_id =", instrument_id, "exchange_id =", exchange_id, "dict_commission =", dict_commission)
                    flag_get_commission_success = True
                    break
                else:
                    flag += 1
                    print("User.get_mmission() 获取手续费失败，尝试次数", flag, "user_id =", self.__user_id, "instrument_id =", instrument_id,
                          "exchange_id =", exchange_id, "手续费获取结果 =", list_commission)
            # if flag > 0:  # 正确获取到手续费率的dict则flag值为0，否则为大于0的整数
            #     print("User.get_mmission() 获取手续费失败， user_id =", self.__user_id, "instrument_id =", instrument_id, "exchange_id =", exchange_id, "手续费获取结果 =", list_commission)
            # print(">>> User.get_commission() ", dict_commission)
            if flag_get_commission_success is False:  # 获取手续费失败，返回空dict
                dict_commission = dict()
                # 弹窗，或其他形式提醒，此处为初始化类错误，影响手续费统计结果!
            self.__dict_commission[commodity_id] = dict_commission  # 将单个品种手续费率存入到user类的所有品种手续费率dict
        return self.__dict_commission[commodity_id]

    # 添加字段"本次成交量"，order结构中加入字段VolumeTradedBatch
    def add_VolumeTradedBatch(self, order):
        order_new = copy.deepcopy(order)
        if order_new['OrderStatus'] in ['0', '1']:  # 全部成交、部分成交还在队列中
            # 原始报单量为1手，本次成交量就是1手
            if order_new['VolumeTotalOriginal'] == 1:
                order_new['VolumeTradedBatch'] = 1
            else:
                for i in self.__list_order_process:
                    if i['OrderRef'] == order['OrderRef']:  # 在列表中找到相同的OrderRef记录
                        order_new['VolumeTradedBatch'] = order_new['VolumeTraded'] - i['VolumeTraded']  # 本次成交量
                        break
        else:  # 非（全部成交、部分成交还在队列中）
            order_new['VolumeTradedBatch'] = 0
        return order_new

    # 更新user的持仓明细
    def update_list_position_detail_for_trade(self, trade):
        # 时间过滤：过滤掉查询投资者持仓明细时间之前的记录
        # if trade['TradeDate'] > self.__date_qry_inverstor_position_detail \
        #         or (trade['TradeDate'] == self.__date_qry_inverstor_position_detail
        #             and trade['TradeTime'] >= self.__time_qry_inverstor_position_detail):
        print(">>> User.update_list_position_detail_for_trade() user_id =", self.__user_id)
        # # 开仓，所有交易所的开仓标志相同
        # if trade['OffsetFlag'] == 0:
        #     pass
        # # 平今
        # elif trade['OffsetFlag'] == 3:
        #     pass
        # # 平昨
        # elif trade['OffsetFlag'] == 4:
        #     pass
        #     # order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        #     # '0'：开仓
        #     # '1'：平仓
        #     # '3'：平今
        #     # '4'：平昨
        trade_new = copy.deepcopy(trade)  # 形参深度拷贝到方法局部变量，目的是修改局部变量值不会影响到形参
        instrument_id = trade_new['InstrumentID']
        instrument_multiple = self.get_instrument_multiple(instrument_id)
        instrument_margin_ratio = self.get_instrument_margin_ratio(instrument_id)
        # self.statistics_for_trade(trade)  # 统计
        # trade_new中"OffsetFlag"值="0"为开仓，不用考虑全部成交还是部分成交，开仓trade直接添加到持仓明细列表里
        if trade_new['OffsetFlag'] == '0':
            # A合约
            # if trade_new['InstrumentID'] == self.__a_instrument_id:
            #     trade_new['CurrMargin'] = trade_new['Price'] * trade_new[
            #         'Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            # # B合约
            # elif trade_new['InstrumentID'] == self.__b_instrument_id:
            #     trade_new['CurrMargin'] = trade_new['Price'] * trade_new[
            #         'Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            trade_new['CurrMargin'] = trade_new['Price'] * trade_new['Volume'] * instrument_multiple * instrument_margin_ratio
            self.__qry_investor_position_detail.append(trade_new)  # 添加到持仓明细列表
        # trade_new中"OffsetFlag"值="3"为平今
        elif trade_new['OffsetFlag'] == '3':
            shift = 0
            len_list_position_detail_for_trade = len(self.__qry_investor_position_detail)
            for i in range(len_list_position_detail_for_trade):  # i为order结构体，类型为dict
                # 持仓明细中trade与trade_new比较：交易日相同、合约代码相同、投保标志相同
                if self.__qry_investor_position_detail[i - shift]['TradingDay'] == trade_new['TradingDay'] \
                        and self.__qry_investor_position_detail[i - shift]['InstrumentID'] == trade_new[
                            'InstrumentID'] \
                        and self.__qry_investor_position_detail[i - shift]['HedgeFlag'] == trade_new[
                            'HedgeFlag'] \
                        and self.__qry_investor_position_detail[i - shift]['Direction'] != trade_new[
                            'Direction']:
                    # trade_new的Volume等于持仓列表首个满足条件的trade的Volume
                    if trade_new['Volume'] == self.__qry_investor_position_detail[i - shift]['Volume']:
                        self.count_profit_close(trade_new, self.__qry_investor_position_detail[i - shift], instrument_multiple)
                        self.__qry_investor_position_detail.remove(
                            self.__qry_investor_position_detail[i - shift])
                        # shift += 1  # 游标修正值
                        break
                    # trade_new的Volume小于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] < self.__qry_investor_position_detail[i - shift]['Volume']:
                        self.count_profit_close(trade_new, self.__qry_investor_position_detail[i - shift], instrument_multiple)
                        # 平仓单数量小于持仓单数量，需从持仓记录中减去对应的被平仓的持仓保证金
                        minus_margin = self.__qry_investor_position_detail[i - shift]['Price'] * trade_new['Volume'] * instrument_multiple * instrument_margin_ratio
                        self.__qry_investor_position_detail[i - shift]['CurrMargin'] -= minus_margin
                        self.__qry_investor_position_detail[i - shift]['Volume'] -= trade_new['Volume']
                        break
                    # trade_new的Volume大于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] > self.__qry_investor_position_detail[i - shift]['Volume']:
                        self.count_profit_close(trade_new, self.__qry_investor_position_detail[i - shift], instrument_multiple)
                        trade_new['Volume'] -= self.__qry_investor_position_detail[i - shift]['Volume']
                        self.__qry_investor_position_detail.remove(self.__qry_investor_position_detail[i - shift])
                        shift += 1  # 游标修正值

        # trade_new中"OffsetFlag"值="4"为平昨
        elif trade_new['OffsetFlag'] == '4':
            shift = 0
            # print(">>> Strategy.update_list_position_detail_for_trade() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, " len(self.__qry_investor_position_detail) =", len(self.__qry_investor_position_detail))
            len_list_position_detail_for_trade = len(self.__qry_investor_position_detail)
            for i in range(len_list_position_detail_for_trade):  # i为trade结构体，类型为dict
                # # 持仓明细中trade与trade_new比较：交易日不相同、合约代码相同、投保标志相同
                # try:
                #     print(">>>Strategy.update_list_position_detail_for_trade() TradingDay", self.__qry_investor_position_detail[i-shift]['TradingDay'], trade_new['TradingDay'])
                # except:
                #     print(">>>Strategy.update_list_position_detail_for_trade() self.__qry_investor_position_detail[i-shift] =", self.__qry_investor_position_detail[i-shift])
                #     print(">>>Strategy.update_list_position_detail_for_trade() trade_new =", trade_new)

                if self.__qry_investor_position_detail[i - shift]['TradingDay'] != trade_new['TradingDay'] \
                        and self.__qry_investor_position_detail[i - shift]['InstrumentID'] == trade_new[
                            'InstrumentID'] \
                        and self.__qry_investor_position_detail[i - shift]['HedgeFlag'] == trade_new[
                            'HedgeFlag'] \
                        and self.__qry_investor_position_detail[i - shift]['Direction'] != trade_new[
                            'Direction']:
                    # trade_new的Volume等于持仓列表首个满足条件的trade的Volume
                    if trade_new['Volume'] == self.__qry_investor_position_detail[i - shift]['Volume']:
                        self.count_profit_close(trade_new, self.__qry_investor_position_detail[i - shift], instrument_multiple)
                        self.__qry_investor_position_detail.remove(
                            self.__qry_investor_position_detail[i - shift])
                        shift += 1  # 游标修正值
                        break
                    # trade_new的Volume小于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] < self.__qry_investor_position_detail[i - shift]['Volume']:
                        self.count_profit_close(trade_new, self.__qry_investor_position_detail[i - shift], instrument_multiple)
                        # 平仓单数量小于持仓单数量，需从持仓记录中减去对应的被平仓的持仓保证金
                        minus_margin = self.__qry_investor_position_detail[i - shift]['Price'] * trade_new['Volume'] * instrument_multiple * instrument_margin_ratio
                        self.__qry_investor_position_detail[i - shift]['CurrMargin'] -= minus_margin
                        self.__qry_investor_position_detail[i - shift]['Volume'] -= trade_new['Volume']
                        break
                    # trade_new的Volume大于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] > self.__qry_investor_position_detail[i - shift]['Volume']:
                        self.count_profit_close(trade_new, self.__qry_investor_position_detail[i - shift], instrument_multiple)
                        trade_new['Volume'] -= self.__qry_investor_position_detail[i - shift]['Volume']
                        self.__qry_investor_position_detail.remove(self.__qry_investor_position_detail[i - shift])
                        shift += 1  # 游标修正值

    # 计算平仓盈亏，形参分别为开仓和平仓的trade
    def count_profit_close(self, trade_close, trade_open, instrument_multiple):
        """
        order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        '0'：开仓
        '1'：平仓
        '3'：平今
        '4'：平昨
        """
        volume_traded = min(trade_close['Volume'], trade_open['Volume'])  # 成交量以较小值一个为准
        profit_close = 0  # 平仓盈亏临时变量
        # 区分平今和平昨的另外
        # 平今：开仓价作为开仓价
        if trade_close['OffsetFlag'] == '3':
            if trade_close['Direction'] == '0':  # 买平仓
                profit_close = (trade_open['Price'] - trade_close['Price']) * instrument_multiple * volume_traded
            elif trade_close['Direction'] == '1':  # 卖平仓
                profit_close = (trade_close['Price'] - trade_open['Price']) * instrument_multiple * volume_traded
        # 平昨：昨结算价作为开仓价
        elif trade_close['OffsetFlag'] == '4':
            if trade_close['Direction'] == '0':  # 买平仓
                profit_close = (trade_open['LastSettlementPrice'] - trade_close['Price']) * instrument_multiple * volume_traded
            elif trade_close['Direction'] == '1':  # 卖平仓
                profit_close = (trade_close['Price'] - trade_open['LastSettlementPrice']) * instrument_multiple * volume_traded
        self.__profit_close += profit_close

    # 计算持仓盈亏
    def count_profit_position(self):
        self.__profit_position = 0  # 持仓盈亏
        for trade in self.__qry_investor_position_detail:
            instrument_id = trade['InstrumentID']
            instrument_multiple = self.get_instrument_multiple(instrument_id)
            if instrument_id in self.__dict_last_tick:
                last_price = self.__dict_last_tick[instrument_id]['LastPrice']
                # 今仓
                if trade['TradingDay'] == self.__TradingDay:
                    # 买持仓
                    if trade['Direction'] == '0':
                        profit_position = (last_price - trade['Price']) * instrument_multiple * trade['Volume']
                    # 卖持仓
                    elif trade['Direction'] == '1':
                        profit_position = (trade['Price'] - last_price) * instrument_multiple * trade['Volume']
                # 昨仓
                else:
                    # 买持仓
                    if trade['Direction'] == '0':
                        profit_position = (last_price - trade['LastSettlementPrice']) * instrument_multiple * trade['Volume']
                    # 卖持仓
                    elif trade['Direction'] == '1':
                        profit_position = (trade['LastSettlementPrice'] - last_price) * instrument_multiple * trade['Volume']
            else:
                profit_position = 0
            self.__profit_position += profit_position
        return self.__profit_position

    # 计算手续费
    def count_commission(self, trade):
        instrument_id = trade['InstrumentID']
        dict_commission_detail = self.get_commission(instrument_id, trade['ExchangeID'])
        instrument_multiple = self.get_instrument_multiple(instrument_id)
        # 开仓
        if trade['OffsetFlag'] == '0':
            commission_amount = \
                dict_commission_detail['OpenRatioByMoney'] * trade['Price'] * trade[
                    'Volume'] * instrument_multiple + dict_commission_detail['OpenRatioByVolume'] * trade['Volume']
        elif trade['OffsetFlag'] == '1':
            commission_amount = 0
            print(">>>User.count_commission() user_id =", self.__user_id, "异常平仓标志位，OffsetFlag=", trade['OffsetFlag'])
        # 平今
        elif trade['OffsetFlag'] == '3':
            commission_amount = \
                dict_commission_detail['CloseTodayRatioByMoney'] * trade['Price'] * trade[
                    'Volume'] * instrument_multiple + dict_commission_detail['CloseTodayRatioByVolume'] * trade['Volume']
        # 平昨
        elif trade['OffsetFlag'] == '4':
            commission_amount = \
                dict_commission_detail['CloseRatioByMoney'] * trade['Price'] * trade[
                    'Volume'] * instrument_multiple + dict_commission_detail['CloseRatioByVolume'] * trade['Volume']
        return commission_amount

        # self.__b_instrument_multiple,正确
        # 输出A、B各自平仓盈亏检查,错误
        # print(">>> Strategy.count_profit() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__a_profit_close =", self.__a_profit_close, "self.__b_profit_close =", self.__b_profit_close)

    # 计算申报费
    def count_commission_order(self, order):
        if order['ExchangeID'] == 'CFFEX':  # 中金所品种
            InstrumentID = order['InstrumentID']
            if len(InstrumentID) == 6:
                CommodityID = InstrumentID[:2]
            elif len(InstrumentID) == 5:
                CommodityID = InstrumentID[:1]
            if CommodityID in ['IF', 'IH', 'IC']:  # 三个品种统计申报费
                OrderRef = order['OrderRef']
                if OrderRef not in self.__list_OrderRef_for_count_commission_order:
                    self.__list_OrderRef_for_count_commission_order.append(OrderRef)
                    self.__commission_order += 1
                    print(">>>User.count_commission_order() user_id =", self.__user_id, "申报费 =", self.__commission_order)
                else:
                    if order['OrderStatus'] in ['0', '5']:
                        self.__list_OrderRef_for_count_commission_order.remove(OrderRef)
                        if order['OrderStatus'] == '5':
                            self.__commission_order += 1
                            print(">>>User.count_commission_order() user_id =", self.__user_id, "申报费 =", self.__commission_order)

    # 更新占用保证金
    def update_current_margin(self):
        # print(">>> Strategy.update_current_margin() user_id =", self.__user_id, "strategy_id =", self.__strategy_id)
        # 中金所：同品种的买持仓和卖持仓，仅收较大单边保证金，同一品种内不区分不同月份合约
        # 上期所：同品种的买持仓和卖持仓，仅收较大单边保证金，同一品种内不区分不同月份合约
        # 郑商所：同一合约买、卖持仓，仅收较大单边保证金，同一品种内区分不同月份合约
        # 大商所：没有保证金免收政策
        self.__Margin_Occupied_CFFEX = self.Margin_Occupied_CFFEX()
        self.__Margin_Occupied_SHFE = self.Margin_Occupied_SHFE()
        self.__Margin_Occupied_CZCE = self.Margin_Occupied_CZCE()
        self.__Margin_Occupied_DCE = self.Margin_Occupied_DCE()
        # print(">>>User.update_current_margin() user_id =", self.__user_id, "\n    self.__Margin_Occupied_CFFEX =", self.__Margin_Occupied_CFFEX, "\n    self.__Margin_Occupied_SHFE =", self.__Margin_Occupied_SHFE, "\n    self.__Margin_Occupied_CZCE =", self.__Margin_Occupied_CZCE, "\n    self.__Margin_Occupied_DCE =", self.__Margin_Occupied_DCE)
        # self.__Margin_Occupied_total = self.__Margin_Occupied_CFFEX + self.__Margin_Occupied_SHFE + self.__Margin_Occupied_CZCE + self.__Margin_Occupied_DCE
        # 策略统计结构体中的元素：策略持仓占用保证金
        self.__current_margin = self.__Margin_Occupied_CFFEX + self.__Margin_Occupied_SHFE + self.__Margin_Occupied_CZCE + self.__Margin_Occupied_DCE
        # print(">>>User.update_current_margin() user_id =", self.__user_id, "used_margin =", self.__Margin_Occupied_CFFEX , self.__Margin_Occupied_SHFE , self.__Margin_Occupied_CZCE , self.__Margin_Occupied_DCE)
        return self.__Margin_Occupied_CFFEX + self.__Margin_Occupied_SHFE + self.__Margin_Occupied_CZCE + self.__Margin_Occupied_DCE

    # 统计持仓明细中属于上海期货交易所的持仓保证金
    def Margin_Occupied_CFFEX(self):
        Margin_Occupied_CFFEX = 0
        # 从持仓明细中过滤出上海期货交易所的持仓明细
        list_position_detail_for_trade_CFFEX = list()
        for i in self.__qry_investor_position_detail:
            if i['ExchangeID'] == 'CFFEX':
                i['CommodityID'] = Utils.extract_commodity_id(i['InstrumentID'])  # 品种代码
                list_position_detail_for_trade_CFFEX.append(i)
        if len(list_position_detail_for_trade_CFFEX) == 0:  # 无持仓，返回保证金初始值0
            return Margin_Occupied_CFFEX

        # 选出持仓明细中存在的品种代码
        list_commodity_id = list()  # 保存持仓中存在品种代码
        for i in list_position_detail_for_trade_CFFEX:
            if i['CommodityID'] in list_commodity_id:
                pass
            else:
                list_commodity_id.append(i['CommodityID'])
        # 同品种买持仓占用保证金求和n1、卖持仓保证金求和n2，保证金收取政策为max(n1,n2)
        # a合约和b合约是同一个品种
        if len(list_commodity_id) == 1:
            Margin_Occupied_CFFEX = self.count_single_instrument_margin_CFFEX(list_position_detail_for_trade_CFFEX)
            # print(">>> Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__Margin_Occupied_SHFE =", self.__Margin_Occupied_SHFE)
        # a合约和b合约是不同的品种
        elif len(list_commodity_id) == 2:
            # 分别选出两种持仓的明细
            list_position_detail_for_trade_CFFEX_0 = list()
            list_position_detail_for_trade_CFFEX_1 = list()
            for i in list_position_detail_for_trade_CFFEX:
                if list_commodity_id[0] == i['CommodityID']:
                    list_position_detail_for_trade_CFFEX_0.append(i)
                elif list_commodity_id[1] == i['CommodityID']:
                    list_position_detail_for_trade_CFFEX_1.append(i)
            # 计算两个品种分别占用的持仓保证金
            margin_0 = self.count_single_instrument_margin_SHFE(list_position_detail_for_trade_CFFEX_0)
            margin_1 = self.count_single_instrument_margin_SHFE(list_position_detail_for_trade_CFFEX_1)
            self.__Margin_Occupied_SHFE = margin_0 + margin_1
        # print(">>>User.Margin_Occupied_CFFEX() self.__Margin_Occupied_SHFE =", self.__Margin_Occupied_SHFE)
        return self.__Margin_Occupied_SHFE

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_CFFEX(self, list_input):
        list_position_detail_for_trade_CFFEX = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_CFFEX:
            instrument_id = i['InstrumentID']
            instrument_multiple = self.get_instrument_multiple(instrument_id)
            instrument_margin_ratio = self.get_instrument_margin_ratio(instrument_id)
            i['CurrMargin'] = i['Price'] * i['Volume'] * instrument_multiple * instrument_margin_ratio
            if i['Direction'] == '0':
                margin_buy += i['CurrMargin']
            elif i['Direction'] == '1':
                margin_sell += i['CurrMargin']
        margin = max(margin_buy, margin_sell)
        return margin

    # 统计持仓明细中属于上海期货交易所的持仓保证金
    def Margin_Occupied_SHFE(self):
        self.__Margin_Occupied_SHFE = 0
        # 从持仓明细中过滤出上海期货交易所的持仓明细
        list_position_detail_for_trade_SHFE = list()
        for i in self.__qry_investor_position_detail:
            if i['ExchangeID'] == 'SHFE':
                i['CommodityID'] = i['InstrumentID'][:2]
                list_position_detail_for_trade_SHFE.append(i)
        # print(">>> User.Margin_Occupied_SHFE() user_id =", self.__user_id, "len(list_position_detail_for_trade_SHFE) =", len(list_position_detail_for_trade_SHFE))
        if len(list_position_detail_for_trade_SHFE) == 0:  # 无上期所持仓，返回初始值0
            return self.__Margin_Occupied_SHFE

        # 选出持仓明细中存在的品种代码
        list_commodity_id = list()  # 保存持仓中存在品种代码
        for i in list_position_detail_for_trade_SHFE:
            if i['CommodityID'] in list_commodity_id:
                pass
            else:
                list_commodity_id.append(i['CommodityID'])
        # print(">>> User.Margin_Occupied_SHFE() user_id =", self.__user_id, "list_commodity_id =", list_commodity_id)

        # 同品种买持仓占用保证金求和n1、卖持仓保证金求和n2，保证金收取政策为max(n1,n2)
        margin_total = 0  # 所有上期所持仓保证金之和
        for commodity_id in list_commodity_id:  # 'cu'
            list_position_detail_for_trade_SHFE_single_commodity = list()  # 存放上期所某一品种的持仓记录
            for i in list_position_detail_for_trade_SHFE:
                if commodity_id == i['CommodityID']:
                    list_position_detail_for_trade_SHFE_single_commodity.append(i)
            margin = self.count_single_instrument_margin_SHFE(list_position_detail_for_trade_SHFE_single_commodity)
            self.__Margin_Occupied_SHFE += margin
        return self.__Margin_Occupied_SHFE

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_SHFE(self, list_input):
        list_position_detail_for_trade_SHFE = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_SHFE:
            instrument_id = i['InstrumentID']
            instrument_multiple = self.get_instrument_multiple(instrument_id)
            instrument_margin_ratio = self.get_instrument_margin_ratio(instrument_id)
            i['CurrMargin'] = i['Price'] * i['Volume'] * instrument_multiple * instrument_margin_ratio
            if i['Direction'] == '0':
                margin_buy += i['CurrMargin']
            elif i['Direction'] == '1':
                margin_sell += i['CurrMargin']
        margin = max(margin_buy, margin_sell)
        return margin

    # 统计持仓明细中属于郑州期货交易所的持仓保证金
    def Margin_Occupied_CZCE(self):
        self.__Margin_Occupied_CZCE = 0
        # 从持仓明细中过滤出郑州期货交易所的持仓明细
        list_position_detail_for_trade_CZCE = list()
        # 将持仓明细中添加品种代码
        for i in self.__qry_investor_position_detail:
            if i['ExchangeID'] == 'CZCE':
                i['CommodityID'] = Utils.extract_commodity_id(i['InstrumentID'])  # 品种代码
                list_position_detail_for_trade_CZCE.append(i)
        if len(list_position_detail_for_trade_CZCE) == 0:
            return self.__Margin_Occupied_CZCE

        # 选出持仓明细中存在的合约代码
        list_instrument_id = list()  # 保存持仓中存在品种代码
        for i in list_position_detail_for_trade_CZCE:
            if i['InstrumentID'] in list_instrument_id:
                pass
            else:
                list_instrument_id.append(i['InstrumentID'])
        # 同一个合约买持仓占用保证金求和n1、卖持仓保证金求和n2，保证金收取政策为max(n1,n2)
        # a合约和b合约是同一个合约
        if len(list_instrument_id) == 1:
            self.__Margin_Occupied_CZCE = self.count_single_instrument_margin_CZCE(list_position_detail_for_trade_CZCE)
            # print(">>> Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__Margin_Occupied_CZCE =", self.__Margin_Occupied_CZCE)
        # a合约和b合约是不同的合约
        elif len(list_instrument_id) == 2:
            # 分别选出两个合约的持仓明细
            list_position_detail_for_trade_CZCE_0 = list()
            list_position_detail_for_trade_CZCE_1 = list()
            for i in list_position_detail_for_trade_CZCE:
                if list_instrument_id[0] == i['InstrumentID']:
                    list_position_detail_for_trade_CZCE_0.append(i)
                elif list_instrument_id[1] == i['InstrumentID']:
                    list_position_detail_for_trade_CZCE_1.append(i)
            # 计算两个品种分别占用的持仓保证金
            margin_0 = self.count_single_instrument_margin_CZCE(list_position_detail_for_trade_CZCE_0)
            margin_1 = self.count_single_instrument_margin_CZCE(list_position_detail_for_trade_CZCE_1)
            self.__Margin_Occupied_CZCE = margin_0 + margin_1
        return self.__Margin_Occupied_CZCE

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_CZCE(self, list_input):
        list_position_detail_for_trade_CZCE = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_CZCE:
            instrument_id = i['InstrumentID']
            instrument_multiple = self.get_instrument_multiple(instrument_id)
            instrument_margin_ratio = self.get_instrument_margin_ratio(instrument_id)
            i['CurrMargin'] = i['Price'] * i['Volume'] * instrument_multiple * instrument_margin_ratio
            if i['Direction'] == '0':
                margin_buy += i['CurrMargin']
            elif i['Direction'] == '1':
                margin_sell += i['CurrMargin']
        margin = max(margin_buy, margin_sell)
        return margin

    # 统计持仓明细中属于大连期货交易所的持仓保证金
    def Margin_Occupied_DCE(self):
        self.__Margin_Occupied_DCE = 0
        # 从持仓明细中过滤出大连期货交易所的持仓明细
        list_position_detail_for_trade_DCE = list()
        for i in self.__qry_investor_position_detail:
            if i['ExchangeID'] == 'DCE':
                i['CommodityID'] = i['InstrumentID'][:2]
                list_position_detail_for_trade_DCE.append(i)
        if len(list_position_detail_for_trade_DCE) == 0:  # 无上期所持仓，返回初始值0
            return self.__Margin_Occupied_DCE

        # 大连期货交易所无保证金免收政策
        self.__Margin_Occupied_DCE = self.count_single_instrument_margin_DCE(list_position_detail_for_trade_DCE)
        # print(">>> Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__Margin_Occupied_DCE =", self.__Margin_Occupied_DCE)
        return self.__Margin_Occupied_DCE

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_DCE(self, list_input):
        list_position_detail_for_trade_DCE = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_DCE:
            instrument_id = i['InstrumentID']
            instrument_multiple = self.get_instrument_multiple(instrument_id)
            instrument_margin_ratio = self.get_instrument_margin_ratio(instrument_id)
            i['CurrMargin'] = i['Price'] * i['Volume'] * instrument_multiple * instrument_margin_ratio
            if i['Direction'] == '0':
                margin_buy += i['CurrMargin']
            elif i['Direction'] == '1':
                margin_sell += i['CurrMargin']
        margin = margin_buy + margin_sell
        return margin

    # 获取指定合约乘数
    def get_instrument_multiple(self, instrument_id):
        for i in self.__QryInstrument:
            if i['InstrumentID'] == instrument_id:
                return i['VolumeMultiple']

    # 获取指定合约保证金率
    def get_instrument_margin_ratio(self, instrument_id):
        for i in self.__QryInstrument:
            if i['InstrumentID'] == instrument_id:
                return i['LongMarginRatio']

    # 处理客户端点击查询操作
    def action_for_UI_query(self):
        print(">>> User.action_for_UI_query() user_id =", self.__user_id, "self.__qry_investor_position_detail", self.__qry_investor_position_detail)

    # # 更新账户资金信息，并刷新界面
    # def update_panel_show_account(self):
    #     # {动态权益，静态权益，持仓盈亏，平仓盈亏，手续费，可用资金，占用保证金，下单冻结，风险度，今日入金，今日出金}
    #     # 删除下单冻结指标，无实际需求
    #     # 静态权益 PreBalance
    #     self.__dict_panel_show_account['PreBalance'] = self.__QryTradingAccount['PreBalance']
    #     # 入金金额 Deposit
    #     self.__dict_panel_show_account['Deposit'] = self.__QryTradingAccount['Deposit']
    #     # 出金金额 Withdraw
    #     self.__dict_panel_show_account['Withdraw'] = self.__QryTradingAccount['Withdraw']
    #     # 动态权益=静态权益+入金金额-出金金额+平仓盈亏+持仓盈亏-手续费
    #     # self.__dict_panel_show_account['Capital'] = self.__QryTradingAccount['PreBalance'] + self.__QryTradingAccount['Deposit'] - self.__QryTradingAccount['Withdraw'] + self.__QryTradingAccount['CloseProfit'] + self.__QryTradingAccount['PositionProfit'] - self.__QryTradingAccount['Commission']
    #     # 遍历self.__list_strategy
    #     for i in self.__list_strategy:
    #         self.__current_margin += i.get_current_margin()  # 期货账户占用保证金
    #         self.__commission += i.get_commission()  # 期货账户手续费
    #         self.__profit_position += i.get_profit_position()  # 期货账户持仓盈亏
    #         self.__profit_close += i.get_profit_close()  # 期货账户平仓盈亏
    #     self.__dict_panel_show_account['CurrMargin'] = self.__current_margin  # 期货账户占用保证金
    #     self.__dict_panel_show_account['Commission'] = self.__commission  # 期货账户手续费
    #     self.__dict_panel_show_account['profit_position'] = self.__profit_position  # 期货账户持仓盈亏
    #     self.__dict_panel_show_account['profit_close'] = self.__profit_close  # 期货账户平仓盈亏
    #     # 期货账户动态权益
    #     self.__dict_panel_show_account['Capital'] = self.__QryTradingAccount['PreBalance'] + self.__QryTradingAccount['Deposit'] - self.__QryTradingAccount['Withdraw'] + self.__profit_close + self.__profit_position - self.__commission
    #     # 期货账户可用资金
    #     self.__dict_panel_show_account['Available'] = self.__dict_panel_show_account['Capital'] - self.__current_margin
    #     # 期货账户风险度
    #     self.__dict_panel_show_account['Risk'] = 1-(self.__dict_panel_show_account['Available'] / self.__dict_panel_show_account['Capital'])
    #
    #     # 更新界面显示
    #     self.signal_update_panel_show_account.emit(self.__dict_panel_show_account)

    # 获取期货账户资金统计信息
    def get_panel_show_account(self):
        return self.__dict_panel_show_account

    # 窗口显示账户资金初始化信息
    # def init_panel_show_account(self):
    #     # 动态权益=静态权益+入金金额-出金金额+平仓盈亏+持仓盈亏-手续费
    #     Capital = self.__QryTradingAccount['PreBalance'] + self.__QryTradingAccount['Deposit'] - \
    #               self.__QryTradingAccount['Withdraw'] + self.__QryTradingAccount['CloseProfit'] + \
    #               self.__QryTradingAccount['PositionProfit'] - self.__QryTradingAccount['Commission']
    #     self.__dict_panel_show_account = {
    #         'Capital': Capital,
    #         'PreBalance': self.__QryTradingAccount['PreBalance'],  # 静态权益
    #         'PositionProfit': self.__QryTradingAccount['PositionProfit'],  # 持仓盈亏
    #         'CloseProfit': self.__QryTradingAccount['CloseProfit'],  # 平仓盈亏
    #         'Commission': self.__QryTradingAccount['Commission'],  # 手续费
    #         'Available': self.__QryTradingAccount['Available'],  # 可用资金
    #         'CurrMargin': self.__QryTradingAccount['CurrMargin'],  # 占用保证金
    #         'FrozenMargin': self.__QryTradingAccount['FrozenMargin'],  # 下单冻结
    #         'Risk': self.__QryTradingAccount['CurrMargin'] / Capital,  # 风险度
    #         'Deposit': self.__QryTradingAccount['Deposit'],  # 今日入金
    #         'Withdraw': self.__QryTradingAccount['Withdraw']  # 今日出金
    #         }
    #     self.signal_update_panel_show_account.emit(self.__dict_panel_show_account)

    # 保存日志，形参：时间、标题、函数名称、消息主题
    def write_log(self, str_time, str_title, str_function_name, str_msg):
        index_list = ['time', 'str_title', 'function', 'msg']
        s = Series([str_time, str_function_name, str_title, str_msg], index=index_list)
        self.__df_log = DataFrame.append(self.__df_log, other=s, ignore_index=True)

    # 统计User为单位的指标：以合约为单位的开仓手数、撤单次数
    def statistics(self, order=None, trade=None):
        # 根据order统计：撤单次数
        if isinstance(order, dict):
            if len(order['OrderSysID']) == 12 and order['OrderStatus'] == '5':  # 值为5：撤单
                if order['InstrumentID'] in self.__dict_action_counter:  # 字典中已经存在合约代码，值累加1
                    self.__dict_action_counter[order['InstrumentID']] += 1
                else:
                    self.__dict_action_counter[order['InstrumentID']] = 1  # 不存在的合约，撤单次数设置为1
                # 撤单次数赋值到策略对象的合约撤单次数
                for i_strategy in self.__list_strategy:
                    if i_strategy.get_a_instrument_id() == order['InstrumentID']:
                        i_strategy.set_a_action_count(self.__dict_action_counter[order['InstrumentID']])
                    elif i_strategy.get_b_instrument_id() == order['InstrumentID']:
                        i_strategy.set_b_action_count(self.__dict_action_counter[order['InstrumentID']])
        # 根据trade统计：开仓手数
        if isinstance(trade, dict):
            if trade['InstrumentID'] in self.__dict_open_counter:  # 字典中已经存在合约代码，值累加‘Volume’
                self.__dict_open_counter[order['InstrumentID']] += trade['Volume']
            else:
                self.__dict_open_counter[order['InstrumentID']] = trade['Volume']  # 字典中不存在合约代码，创建命名和键值

    # 统计order
    def statistics_for_order(self, order):
        if len(order['OrderSysID']) == 12 and order['OrderStatus'] == '5':  # 值为5：撤单
            instrument_id = order['InstrumentID']
            if instrument_id in self.__dict_instrument_statistics:  # 字典中存在合约代码键名
                self.__dict_instrument_statistics[instrument_id]['action_count'] += 1  # 撤单次数加一
            else:  # 字典中不存在合约代码键名
                self.__dict_instrument_statistics[instrument_id] = {
                    'action_count': 1,  # 不存在的合约，撤单次数设置为1
                    'open_count': 0  # 不存在的合约，开仓数量设置为0
                }
                # self.__dict_instrument_statistics[instrument_id]['action_count'] = 1  # 不存在的合约，撤单次数设置为1
                # self.__dict_instrument_statistics[instrument_id]['open_count'] = 0  # 不存在的合约，开仓数量设置为0

            # 撤单次数赋值到策略对象的合约撤单次数
            action_count = self.__dict_instrument_statistics[instrument_id]['action_count']
            for strategy_id in self.__dict_strategy:
                if self.__dict_strategy[strategy_id].get_a_instrument_id() == instrument_id:
                    self.__dict_strategy[strategy_id].set_a_action_count(action_count)
                elif self.__dict_strategy[strategy_id].get_b_instrument_id() == instrument_id:
                    self.__dict_strategy[strategy_id].set_b_action_count(action_count)

    # 统计trade
    def statistics_for_trade(self, trade):
        instrument_id = trade['InstrumentID']
        # 统计合约开仓手数
        if instrument_id in self.__dict_instrument_statistics:  # 字典中存在合约代码键名
            self.__dict_instrument_statistics[instrument_id]['open_count'] += trade['Volume']  # 开仓数量累加
        else:  # 字典中不存在合约代码键名
            self.__dict_instrument_statistics[instrument_id] = {
                'action_count': 0,  # 不存在的合约，撤单次数设置为0
                'open_count': trade['Volume']  # 不存在的合约，开仓数量设置为本次值
            }
            # self.__dict_instrument_statistics[instrument_id]['action_count'] = 0  # 不存在的合约，撤单次数设置为0
            # self.__dict_instrument_statistics[instrument_id]['open_count'] = trade['Volume']  # 不存在的合约，开仓数量设置为0

        # 统计合约开仓
        # 撤单次数赋值到策略对象的合约撤单次数
        open_count = self.__dict_instrument_statistics[instrument_id]['open_count']
        for strategy_id in self.__dict_strategy:
            if self.__dict_strategy[strategy_id].get_a_instrument_id() == instrument_id:
                self.__dict_strategy[strategy_id].set_a_open_count(open_count)
            elif self.__dict_strategy[strategy_id].get_b_instrument_id() == instrument_id:
                self.__dict_strategy[strategy_id].set_b_open_count(open_count)

    # 根据持仓明细规则将平仓标志位OffsetFlag的值由1转换为3或4
    def process_trade_offset_flag(self, trade):
        if trade['OffsetFlag'] == '1':  # 平仓标志位为1，需要转换
            for i in self.__qry_investor_position_detail:
                if i['InstrumentID'] == trade['InstrumentID'] and i['Direction'] != trade['Direction']:
                    if i['TradingDay'] != self.__TradingDay:
                        trade['OffsetFlag'] = '4'  # 修改平仓标志位
                        print(">>>User.process_trade_offset_flag() user_id =", self.__user_id, "将平仓标志位由1修改为4，trade=", trade)
                    elif i['TradingDay'] == self.__TradingDay:
                        trade['OffsetFlag'] = '3'  # 修改平仓标志位
                        print(">>>User.process_trade_offset_flag() user_id =", self.__user_id, "将平仓标志位由1修改为3，trade=", trade)
                    break

if __name__ == '__main__':
    print("User.py, if __name__ == '__main__':")
        


