# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""

import time
import datetime
import copy
from pymongo import MongoClient
from PyCTP_Trade import PyCTP_Trader_API
import Utils
from pandas import DataFrame, Series
from PyQt4 import QtCore


class User(QtCore.QObject):
    signal_update_pushButton_start_strategy = QtCore.pyqtSignal()  # 定义信号：内核设置期货账户交易开关 -> 更新窗口“开始策略”按钮状态
    signal_label_login_error_text = QtCore.pyqtSignal(str)  # 定义信号：->更新登录窗口文本
    signal_update_panel_show_account = QtCore.pyqtSignal(dict)  # 定义信号：更新界面账户资金信息

    # 初始化参数BrokerID\UserID\Password\frontaddress，参数格式为二进制字符串
    def __init__(self, dict_arguments, parent=None, ctp_manager=None):
        print('User.__init__() 创建User对象参数', dict_arguments)
        super(User, self).__init__(parent)  # 显示调用父类初始化方法，使用其信号槽机制
        self.__ctp_manager = ctp_manager
        # 连接信号槽：-> 更新QLoginForm文本框内容
        self.signal_label_login_error_text.connect(self.__ctp_manager.get_QLoginForm().label_login_error.setText)
        self.__trader_id = dict_arguments['traderid'].encode()
        self.__user_id = dict_arguments['userid'].encode()
        self.__BrokerID = dict_arguments['brokerid'].encode()
        self.__Password = dict_arguments['password'].encode()
        self.__FrontAddress = dict_arguments['frontaddress'].encode()
        self.__list_sessionid = list()  # 当前交易日，期货账户所有会话id，服务端的
        self.__list_position_detail = list()  # 期货账户持仓明细，内部元素结构为order
        self.__list_position_detail_trade = list()  # 期货账户持仓明细，内部元素结构为trade
        self.__list_order_process = list()  # 挂单列表，未成交、部分成交还在队列中
        self.__list_OnRtnOrder = []  # 保存单账户所有的OnRtnOrder回调数据
        self.__list_OnRtnTrade = []  # 保存单账户所有的OnRtnTrade回调数据
        self.__list_SendOrder = []  # 保存单账户所有调用OrderInsert的记录
        self.__list_strategy = []  # 期货账户下面的所有交易策略实例列表
        self.__dict_commission = dict()  # 保存手续费的字典，字典内元素格式为{'cu':{'OpenRatioByVolume': 0.0, 'OpenRatioByMoney': 2.5e-05, 'CloseTodayRatioByVolume': 0.0, 'CloseTodayRatioByMoney': 0.0, 'CloseRatioByVolume': 0.0, 'CloseRatioByMoney': 2.5e-05, 'InstrumentID': 'cu',  'InvestorRange': '1'}}
        # self.__list_InstrumentId = []  # 合约列表，记录撤单次数，在创建策略的时候添加合约，
        self.__last_qry_time = time.time()  # 类型浮点数，最后一次查询Trade_Api的时间
        self.__dict_action_counter = dict()  # 记录合约撤单次数的字典,撤单操作时添加次数，交易日换日时初始化值
        self.__order_ref_part2 = 0  # 所有策略共用报单引用编号，报单引用后两位为策略编号，前十位递增一
        self.__init_finished = False  # 初始化完成
        self.__init_finished_succeed = True  # user初始化成功，初始化过程中遇到任何异常就设置为False

        # 联机登录：创建user时清空本地数据库中的集合：col_strategy、col_position、col_position_detail、col_trade、col_order，
        # 脱机登录：创建user时清空本地数据库中的集合：col_strategy、col_position、col_position_detail、col_trade、col_order，
        # 其中trade和order记录只清空当天的
        # self.__mongo_client = MongoClient('localhost', 27017)  # 创建数据库连接实例
        # col_strategy = self.__user_id.decode() + 'strategy'  # 策略集合名
        # col_position = self.__user_id.decode() + 'position'  # 持仓汇总集合名
        # col_position_detail = self.__user_id.decode() + 'position_detail'  # 持仓明细集合名
        # col_trade = self.__user_id.decode() + 'trade'  # trade回调记录集合名
        # col_order = self.__user_id.decode() + 'order'  # order回调记录集合名
        # for i in [col_strategy, col_position, col_position_detail]:  # 初始化user时清空集合
        #     try:
        #         self.__mongo_client.CTP.drop_collection(i)
        #     except:
        #         print("User.__init__() 删除数据库集合失败，集合名=", i)
        # for i in [col_trade, col_order]:  # 初始化user时清空当天Trade、Order集合
        #     try:
        #         self.__mongo_client.CTP.get_collection(i).delete_many({'TradingDay': self.__TradingDay})
        #     except:
        #         print("User.__init__() 删除当天的trade或order记录失败")

        # 为每个user创建独立的流文件夹
        s_path = b'conn/td/' + self.__user_id + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__trader_api = PyCTP_Trader_API.CreateFtdcTraderApi(s_path)
        self.__trader_api.set_user(self)  # 将该类设置为trade的属性

        """连接交易前置"""
        # 0：发送成功；-1：因网络原因发送失败；-2：未处理请求队列总数量超限；-3：每秒发送请求数量超限
        connect_trade_front = self.__trader_api.Connect(self.__FrontAddress)
        # 连接前置地址状态记录到CTPManager的user状态字典，成功为0
        self.__ctp_manager.get_dict_user()[self.__user_id.decode()] = {'connect_trade_front': connect_trade_front}
        # self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['connect_trade_front'] = connect_trade_front
        if connect_trade_front == -1:
            self.signal_label_login_error_text.emit("期货账户"+self.__user_id.decode()+"因网络原因发送失败")
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['connect_trade_front'] = "因网络原因发送失败"
        elif connect_trade_front == -2:
            self.signal_label_login_error_text.emit("期货账户"+self.__user_id.decode()+"未处理请求队列总数量超限")
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['connect_trade_front'] = "未处理请求队列总数量超限"
        elif connect_trade_front == -3:
            self.signal_label_login_error_text.emit("期货账户"+self.__user_id.decode()+"每秒发送请求数量超限")
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['connect_trade_front'] = "每秒发送请求数量超限"
        elif connect_trade_front == -4:
            self.signal_label_login_error_text.emit("期货账户"+self.__user_id.decode()+"连接交易前置异常")
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['connect_trade_front'] = "连接交易前置异常"
        if connect_trade_front != 0:
            self.__init_finished_succeed = False  # 初始化失败
            print("User.__init__() user_id=", self.__user_id.decode(), '连接交易前置失败', Utils.code_transform(connect_trade_front))
            return
        print("User.__init__() user_id=", self.__user_id.decode(), '连接交易前置成功', Utils.code_transform(connect_trade_front))

        """登录期货账号"""
        login_trade_account = self.__trader_api.Login(self.__BrokerID, self.__user_id, self.__Password)
        # 登录期货账号状态记录到CTPManager的user状态字典，成功为0
        self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['login_trade_account'] = login_trade_account
        if login_trade_account != 0:
            self.__init_finished_succeed = False  # 初始化失败
            print("User.__init__() user_id=", self.__user_id.decode(), '登录期货账号失败', Utils.code_transform(login_trade_account))
            return
        self.__front_id = self.__trader_api.get_front_id()  # 获取前置编号
        self.__session_id = self.__trader_api.get_session_id()  # 获取会话编号
        self.__TradingDay = self.__trader_api.GetTradingDay().decode()  # 获取交易日
        print("User.__init__() user_id=", self.__user_id.decode(), '登录期货账号成功', Utils.code_transform(login_trade_account))

        """设置user的所有sessions属性"""
        for i in self.__ctp_manager.get_SocketManager().get_list_sessions_info():
            if i['userid'] == self.__user_id.decode():
                self.__list_sessionid.append(i['sessionid'])

        """查询资金账户"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        self.__QryTradingAccount = self.__trader_api.QryTradingAccount()[0]
        if isinstance(self.__QryTradingAccount, dict):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTradingAccount'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询资金账户成功',
                  Utils.code_transform(self.__QryTradingAccount))
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTradingAccount'] = self.__QryTradingAccount
            print("User.__init__() user_id=", self.__user_id.decode(), '查询资金账户失败',
                  Utils.code_transform(self.__QryTradingAccount))

        """查询投资者持仓"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        self.__QryInvestorPosition = self.__trader_api.QryInvestorPosition()
        if isinstance(self.__QryInvestorPosition, list):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryInvestorPosition'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询投资者持仓成功',
                  Utils.code_transform(self.__QryInvestorPosition))
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryInvestorPosition'] = self.__QryInvestorPosition
            print("User.__init__() user_id=", self.__user_id.decode(), '查询投资者持仓失败',
                  Utils.code_transform(self.__QryInvestorPosition))

        """查询投资者持仓明细"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        self.__QryInvestorPositionDetail = self.__trader_api.QryInvestorPositionDetail()
        if isinstance(self.__QryInvestorPositionDetail, list):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryInvestorPositionDetail'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询投资者持仓明细成功',
                  Utils.code_transform(self.__QryInvestorPositionDetail))
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()][
                'QryInvestorPositionDetail'] = self.__QryInvestorPositionDetail
            print("User.__init__() user_id=", self.__user_id.decode(), '查询投资者持仓明细失败',
                  Utils.code_transform(self.__QryInvestorPositionDetail))

        """查询成交记录"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        self.__list_QryTrade = self.QryTrade()  # 保存查询当天的Trade和Order记录，正常值格式为DataFrame，异常值为None
        # QryTrade查询结果的状态记录到CTPManager的user状态字典，成功为0
        if isinstance(self.__list_QryTrade, list):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTrade'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询成交记录成功，self.__list_QryTrade=', self.__list_QryTrade)
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTrade'] = 1
            print("User.__init__() user_id=", self.__user_id.decode(), '查询成交记录失败，self.__list_QryOrder=', self.__list_QryOrder)
        # self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['login_trade_account'] = login_trade_account

        """查询报单记录"""
        # time.sleep(1.0)
        self.qry_api_interval_manager()  # API查询时间间隔管理
        self.__list_QryOrder = self.QryOrder()
        # QryOrder查询结果的状态记录到CTPManager的user状态字典，成功为0
        if isinstance(self.__list_QryOrder, list):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryOrder'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询报单记录成功，self.__list_QryOrder=', self.__list_QryOrder)
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryOrder'] = 1
            print("User.__init__() user_id=", self.__user_id.decode(), '查询报单记录失败')

        """设置期货账户交易开关"""
        for i_user_info in self.__ctp_manager.get_list_user_info():
            if i_user_info['userid'] == self.__user_id.decode():
                self.__on_off = i_user_info['on_off']  # user的交易开关，初始值为关
                break
                # self.__only_close = 0  # user的只平，初始值为关，已删除此功能

        print("User.__init__() user_id=", self.__user_id.decode(), "CTPManager记录User初始化信息 ",
              {self.__user_id.decode(): self.__ctp_manager.get_dict_user()[self.__user_id.decode()]})

        """查询user的持仓明细"""
        for i in self.__ctp_manager.get_SocketManager().get_list_position_detail_info():
            if i['userid'] == self.__user_id.decode():
                self.__list_position_detail.append(i)

        """初始化策略持仓明细列表"""
        # if self.init_list_position_detail() is not True:
        #     print("Strategy.__init__() 策略初始化错误：初始化策略持仓明细列表出错")
        #     self.__init_finished = False  # 策略初始化失败
        #     return

    # 设置合约信息
    def set_InstrumentInfo(self, list_InstrumentInfo):
        self.__instrument_info = list_InstrumentInfo

    # API查询操作管理，记录最后一次查询时间，且与上一次查询时间至少间隔一秒，该方法放置位置在对api查询之前
    def qry_api_interval_manager(self):
        time_interval = time.time() - self.__last_qry_time
        if time_interval < 1.0:
            time.sleep(1-time_interval)
        self.__last_qry_time = time.time()

    # 查询合约信息
    def qry_instrument_info(self):
        if self.__ctp_manager.get_got_list_instrument_info() is False:
            self.__instrument_info = Utils.code_transform(self.__trader_api.QryInstrument())  # 查询合约，所有交易所的所有合约
            if isinstance(self.__instrument_info, list):
                print("User.qry_instrument_info() user_id=", self.__user_id, "查询合约信息成功", self.__instrument_info)
                if len(self.__instrument_info) > 0:
                    self.__ctp_manager.set_got_list_instrument_info(True)  # 将获取合约信息的状态设置为真，获取成功
                    self.__ctp_manager.set_instrument_info(self.__instrument_info)  # 将查询到的合约信息传递给CTPManager
            else:
                print("User.qry_instrument_info() user_id=", self.__user_id, "查询合约信息失败", self.__instrument_info)

    # 将CTPManager类设置为user的属性
    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager

    # 获取CTPManager属性
    def get_CTPManager(self):
        return self.__ctp_manager

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

    # 获取期货账号
    def get_user_id(self):
        return self.__user_id

    # 获取交易员id
    def get_trader_id(self):
        return self.__trader_id

    # 获取trade实例(TD)
    def get_trade(self):
        return self.__trader_api

    # 获取self.__instrument_info
    def get_instrument_info(self):
        return self.__instrument_info

    # 设置user的交易开关，0关、1开
    def set_on_off(self, int_on_off):
        print(">>>User.set_on_off() user_id=", self.__user_id, int_on_off)
        self.__on_off = int_on_off
        self.signal_update_pushButton_start_strategy.emit()  # 触发信号：内核设置期货账户交易开关 -> 更新窗口“开始策略”按钮状态

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

    # 获取user初始化状态
    def get_init_finished(self):
        return self.__init_finished

    # 获取交易日
    def GetTradingDay(self):
        return self.__TradingDay

    # 获取报单引用，自增1，位置处于第1到第10位，共9位阿拉伯数字，user的所有策略共用
    def add_order_ref_part2(self):
        self.__order_ref_part2 += 1
        return self.__order_ref_part2

    # 添加交易策略实例，到self.__list_strategy
    def add_strategy(self, obj_strategy):
        self.__list_strategy.append(obj_strategy)  # 将交易策略实例添加到本类的交易策略列表
        self.__trader_api.set_list_strategy(self.__list_strategy)  # 将本类的交易策略列表转发给trade
        obj_strategy.set_user(self)  # 将user设置为strategy属性

    # 添加合约代码到user类的self.__dict_action_counter
    # def add_instrument_id_action_counter(self, list_instrument_id):
    #     for i in list_instrument_id:
    #         if i not in self.__dict_action_counter:
    #             self.__dict_action_counter[i] = 0

    # 撤单计数
    def action_counter(self, Order):
        if len(Order['OrderSysID']) == 0:  # 只统计有交易所编码的order
            return
        if Order['OrderStatus'] != '5':  # 值为5：撤单
            return
        if Order['InstrumentID'] in self.__dict_action_counter:  # 已经存在的合约，撤单次数加+1
            self.__dict_action_counter[Order['InstrumentID']] += 1
        else:
            self.__dict_action_counter[Order['InstrumentID']] = 1  # 不存在的合约，撤单次数设置为1

        # 撤单次数赋值到策略对象的合约撤单次数
        for i_strategy in self.__list_strategy:
            if i_strategy.get_a_instrument_id() == Order['InstrumentID']:
                i_strategy.set_a_action_count(self.__dict_action_counter[Order['InstrumentID']])
            elif i_strategy.get_b_instrument_id() == Order['InstrumentID']:
                i_strategy.set_b_action_count(self.__dict_action_counter[Order['InstrumentID']])

    # 删除交易策略实例，从self.__list_strategy
    def del_strategy(self, strategy_id):
        for i in self.__list_strategy:
            if i.get_strategy_id() == strategy_id:
                self.__list_strategy.remove(i)

    # 获取list_strategy
    def get_list_strategy(self):
        return self.__list_strategy

    # 获取合约撤单次数的字典
    def get_dict_action(self):
        return self.__dict_action_counter

    # 查询行情
    def qry_depth_market_data(self, instrument_id):
        return self.__trader_api.QryDepthMarketData(instrument_id)

    # 查询合约
    # def qry_instrument(self):
    #     return self.__trader_api.QryInstrument()

    # 转PyCTP_Market_API类中回调函数OnRtnOrder
    def OnRtnTrade(self, Trade):
        # print("User.OnRtnTrade()", 'OrderRef:', Trade['OrderRef'], 'Trade:', Trade)

        # 根据字段‘OrderRef’筛选出本套利系统的Trade，OrderRef规则：第1位为‘1’，第2位至第10位为递增数，第11位至第12位为StrategyID
        if len(Trade['OrderRef']) != 12 or Trade['OrderRef'][:1] != '1':
            return

        # Trade新增字段
        t = datetime.datetime.now()
        Trade['OperatorID'] = self.__trader_id  # 客户端账号（也能区分用户身份或交易员身份）:OperatorID
        Trade['StrategyID'] = Trade['OrderRef'][-2:]  # 报单引用末两位是策略编号
        Trade['RecTradeTime'] = t.strftime("%Y-%m-%d %H:%M:%S")  # 收到成交回报的时间
        Trade['RecTradeMicrosecond'] = t.strftime("%f")  # 收到成交回报中的时间毫秒

        # 转到Strategy行情回调函数OnRtnOrder
        for i in self.__list_strategy:  # 转到strategy回调函数
            if Trade['OrderRef'][-2:] == i.get_strategy_id():
                i.OnRtnTrade(Trade)

        # 记录存到数据库
        # self.__DBManager.insert_trade(Trade)
        # if self.__mongo_client is not None:
        #     self.__mongo_client.CTP.get_collection(self.__user_id.decode()+'_Trade').insert_one(Trade)  # 记录插入到数据库
        # else:
        #     print("User.OnRtnTrade() self.__mongo_client is None")

    # 转PyCTP_Market_API类中回调函数OnRtnOrder
    def OnRtnOrder(self, Order):
        # print("User.OnRtnOrder()", 'OrderRef:', Order['OrderRef'], 'Order:', Order)
        self.action_counter(Order)  # 无任何过滤条件，所有order加入到撤单计数

        # 根据字段‘SessionID’筛选出本套利系统的Trade，
        # if Order['SessionID'] not in self.__list_sessionid:
        #     return

        # 根据字段‘OrderRef’筛选出本套利系统的Trade，OrderRef规则：第1位为‘1’，第2位至第10位为递增数，第11位至第12位为StrategyID
        if len(Order['OrderRef']) != 12 or Order['OrderRef'][:1] != '1':
            return

        # Order新增字段
        order_new = self.add_VolumeTradedBatch(Order)  # 添加字段，本次成交量'VolumeTradedBatch'
        self.update_list_order_process(order_new)  # 更新挂单列表
        self.update_list_position_detail(order_new)  # 更新持仓明细列表
        t = datetime.datetime.now()
        Order['OperatorID'] = self.__trader_id  # 客户端账号（也能区分用户身份或交易员身份）:OperatorID
        Order['StrategyID'] = Order['OrderRef'][-2:]  # 报单引用末两位是策略编号
        Order['RecOrderTime'] = t.strftime("%Y-%m-%d %H:%M:%S")  # 收到成交回报的时间
        Order['RecOrderMicrosecond'] = t.strftime("%f")  # 收到成交回报中的时间毫秒

        # 转到Strategy行情回调函数OnRtnOrder
        for i in self.__list_strategy:  # 转到strategy回调函数
            if Order['OrderRef'][-2:] == i.get_strategy_id():
                i.OnRtnOrder(Order)

        # 记录存到数据库
        # self.__DBManager.insert_trade(Order)
        # self.__mongo_client.CTP.get_collection(self.__user_id.decode()+'_Order').insert_one(Order)  # 记录插入到数据库

    # 转PyCTP_Market_API类中回调函数QryTrade
    # def QryTrade(self):
    #     dfQryTrade = DataFrame()
    #     self.__listQryTrade = self.__trader_api.QryTrade()  # 返回正常值格式为list，错误值为int
    #     if isinstance(self.__listQryTrade, list):
    #         if len(self.__listQryTrade) > 0:
    #             for i in self.__listQryTrade:
    #                 # 将记录格式有list变为DataFrame
    #                 dfQryTrade = DataFrame.append(dfQryTrade, other=Utils.code_transform(i), ignore_index=True)
    #             # 添加列StrategyID：截取OrderRef后两位数为StrategyID
    #             dfQryTrade['StrategyID'] = dfQryTrade['OrderRef'].astype(str).str[-2:].astype(int)
    #     return dfQryTrade

    # 转PyCTP_Market_API类中回调函数QryTrade
    def QryTrade(self):
        self.__list_QryTrade = self.__trader_api.QryTrade()  # 正确返回值为list类型，否则为异常
        print(">>> User.QryTrade() self.__list_QryTrade=", self.__list_QryTrade)
        # 筛选条件：OrderRef第一位为1，长度为12
        for i in self.__list_QryTrade:
            if len(i['OrderRef']) == 12 and i['OrderRef'][:1] == '1':
                pass
            else:
                self.__list_QryTrade.remove(i)
        for i in self.__list_QryTrade:
            i['StrategyID'] = i['OrderRef'][-2:]  # 增加字段：策略编号"StrategyID"
        return self.__list_QryTrade

    # 转PyCTP_Market_API类中回调函数QryOrder
    def QryOrder(self):
        self.__list_QryOrder = self.__trader_api.QryOrder()  # 正确返回值为list类型，否则为异常
        for i in self.__list_QryOrder:
            self.action_counter(i)  # 撤单计数

        # 筛选条件：OrderRef第一位为1，长度为12
        for i in self.__list_QryOrder:
            if len(i['OrderRef']) == 12 and i['OrderRef'][:1] == '1':
                pass
            else:
                self.__list_QryOrder.remove(i)
        for i in self.__list_QryOrder:
            i['StrategyID'] = i['OrderRef'][-2:]  # 增加字段：策略编号"StrategyID"
        return self.__list_QryOrder

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
        if exchange_id in ['SHFE', 'CFFEX', 'DZCE']:
            commodity_id = instrument_id[:2]
        elif exchange_id in ['DCE']:
            commodity_id = instrument_id[:1]
        if commodity_id not in self.__dict_commission:
            # 通过API查询单个品种的手续费率dict
            self.qry_api_interval_manager()  # API查询时间间隔管理
            dict_commission = Utils.code_transform(self.__trader_api.QryInstrumentCommissionRate(instrument_id.encode())[0])
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

    # 初始化持仓明细列表
    # def init_list_position_detail(self):
    #     # 筛选出期货账户的持仓明细
    #     for i in self.__ctp_manager.get_SocketManager().get_list_position_detail_info():
    #         if i['userid'] == self.__user_id:
    #             self.__list_position_detail.append(i)
    #
    #     if len(self.__list_QryOrder) > 0:  # 期货账户的QryOrder有记录
    #         for i in self.__list_QryOrder:  # 遍历期货账户的QryOrder
    #             self.action_counter(i)  # 更新撤单计数
    #             self.update_list_order_process(i)  # 更新挂单列表
    #             order_new = self.add_VolumeTradedBatch(i)  # 增加本次成交量字段VolumeTradedBatch
    #             self.update_list_position_detail(order_new)  # 更新持仓明细列表
    #         return True
    #     elif len(self.__list_QryOrder) == 0:  # 本策略的self.__list_QryOrder无记录
    #         return True

    # 更新挂单列表，重写方法self.update_list_order_pending()
    def update_list_order_process(self, order):
        """
        order中的字段OrderStatus
         0 全部成交
         1 部分成交，订单还在交易所撮合队列中
         3 未成交，订单还在交易所撮合队列中
         5 已撤销
         a 未知 - 订单已提交交易所，未从交易所收到确认信息
        """
        if order['OrderStatus'] == '0':
            for i in self.__list_order_process:
                if i['OrderRef'] == order['OrderRef']:  # 在列表中找到相同的OrderRef记录
                    self.__list_order_process.remove(i)  # 删除找到的order记录
                    break
        elif order['OrderStatus'] == '1':
            for i in self.__list_order_process:
                if i['OrderRef'] == order['OrderRef']:  # 在列表中找到相同的OrderRef记录
                    self.__list_order_process.remove(i)  # 删除找到的order记录
                    self.__list_order_process.append(order)  # 添加最新的order记录
                    break
        elif order['OrderStatus'] == '3':
            self.__list_order_process.append(order)
        elif order['OrderStatus'] == '5':
            for i in self.__list_order_process:
                if i['OrderRef'] == order['OrderRef']:  # 在列表中找到相同的OrderRef记录
                    self.__list_order_process.remove(i)  # 删除找到的order记录
                    break
        elif order['OrderStatus'] == 'a':
            pass  # 不需要处理

    # 更新持仓明细列表，形参为order
    def update_list_position_detail(self, input_order):
        """
        order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        0：开仓
        1：平仓
        3：平今
        4：平昨
        """
        # 跳过无成交的order记录
        if input_order['VolumeTraded'] == 0:
            return
        order_new = copy.deepcopy(input_order)  # 形参深度拷贝到方法局部变量，目的是修改局部变量值不会影响到形参
        # order_new中"CombOffsetFlag"值="0"为开仓，不用考虑全部成交还是部分成交，开仓order直接添加到持仓明细列表里
        if order_new['CombOffsetFlag'] == '0':
            self.__list_position_detail.append(order_new)
        # order_new中"CombOffsetFlag"值="3"为平今
        if order_new['CombOffsetFlag'] == '3':
            for i in self.__list_position_detail:  # i为order结构体，类型为dict
                # 持仓明细中order与order_new比较：交易日相同、合约代码相同、投保标志相同
                if i['TradingDay'] == order_new['TradingDay'] \
                        and i['InstrumentID'] == order_new['InstrumentID'] \
                        and i['CombHedgeFlag'] == order_new['CombHedgeFlag']:
                    # order_new的VolumeTradedBatch等于持仓列表首个满足条件的order的VolumeTradedBatch
                    if order_new['VolumeTradedBatch'] == i['VolumeTradedBatch']:
                        self.__list_position_detail.remove(i)
                        break
                    # order_new的VolumeTradedBatch小于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order_new['VolumeTradedBatch'] < i['VolumeTradedBatch']:
                        i['VolumeTradedBatch'] -= order_new['VolumeTradedBatch']
                        break
                    # order_new的VolumeTradedBatch大于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order_new['VolumeTradedBatch'] > i['VolumeTradedBatch']:
                        order_new['VolumeTradedBatch'] -= i['VolumeTradedBatch']
                        self.__list_position_detail.remove(i)
        # order_new中"CombOffsetFlag"值="4"为平昨
        elif order_new['CombOffsetFlag'] == '4':
            for i in self.__list_position_detail:  # i为order结构体，类型为dict
                # 持仓明细中order与order_new比较：交易日不相同、合约代码相同、投保标志相同
                if i['TradingDay'] != order_new['TradingDay'] \
                        and i['InstrumentID'] == order_new['InstrumentID'] \
                        and i['CombHedgeFlag'] == order_new['CombHedgeFlag']:
                    # order_new的VolumeTradedBatch等于持仓列表首个满足条件的order的VolumeTradedBatch
                    if order_new['VolumeTradedBatch'] == i['VolumeTradedBatch']:
                        self.__list_position_detail.remove(i)
                        break
                    # order_new的VolumeTradedBatch小于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order_new['VolumeTradedBatch'] < i['VolumeTradedBatch']:
                        i['VolumeTradedBatch'] -= order_new['VolumeTradedBatch']
                        break
                    # order_new的VolumeTradedBatch大于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order_new['VolumeTradedBatch'] > i['VolumeTradedBatch']:
                        order_new['VolumeTradedBatch'] -= i['VolumeTradedBatch']
                        self.__list_position_detail.remove(i)

    # 更新持仓明细列表，形参为order，统计持仓盈亏、平仓盈亏等指标需要，初始化过程和OnRtnTrade中被调用
    # 待续，2017年1月24日15:53:03
    def update_list_position_detail_trade(self, input_trade):
        """
        order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        0：开仓
        1：平仓
        3：平今
        4：平昨
        """
        trade_new = copy.deepcopy(input_trade)  # 形参深度拷贝到方法局部变量，目的是修改局部变量值不会影响到形参
        # trade_new中"OffsetFlag"值="0"为开仓，不用考虑全部成交还是部分成交，开仓order直接添加到持仓明细列表里
        if trade_new['OffsetFlag'] == '0':
            self.__list_position_detail_trade.append(trade_new)
        # order_new中"OffsetFlag"值="3"为平今
        if trade_new['OffsetFlag'] == '3':
            for i in self.__list_position_detail_trade:  # i为order结构体，类型为dict
                # 持仓明细中order与order_new比较：交易日相同、合约代码相同、投保标志相同
                if i['TradingDay'] == trade_new['TradingDay'] \
                        and i['InstrumentID'] == trade_new['InstrumentID'] \
                        and i['CombHedgeFlag'] == trade_new['CombHedgeFlag']:
                    # order_new的VolumeTradedBatch等于持仓列表首个满足条件的order的VolumeTradedBatch
                    if trade_new['VolumeTradedBatch'] == i['VolumeTradedBatch']:
                        self.__list_position_detail_trade.remove(i)
                        break
                    # order_new的VolumeTradedBatch小于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif trade_new['VolumeTradedBatch'] < i['VolumeTradedBatch']:
                        i['VolumeTradedBatch'] -= trade_new['VolumeTradedBatch']
                        break
                    # order_new的VolumeTradedBatch大于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif trade_new['VolumeTradedBatch'] > i['VolumeTradedBatch']:
                        trade_new['VolumeTradedBatch'] -= i['VolumeTradedBatch']
                        self.__list_position_detail_trade.remove(i)
        # order_new中"OffsetFlag"值="4"为平昨
        elif trade_new['OffsetFlag'] == '4':
            for i in self.__list_position_detail_trade:  # i为order结构体，类型为dict
                # 持仓明细中order与order_new比较：交易日不相同、合约代码相同、投保标志相同
                if i['TradingDay'] != trade_new['TradingDay'] \
                        and i['InstrumentID'] == trade_new['InstrumentID'] \
                        and i['CombHedgeFlag'] == trade_new['CombHedgeFlag']:
                    # order_new的VolumeTradedBatch等于持仓列表首个满足条件的order的VolumeTradedBatch
                    if trade_new['VolumeTradedBatch'] == i['VolumeTradedBatch']:
                        self.__list_position_detail_trade.remove(i)
                        break
                    # order_new的VolumeTradedBatch小于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif trade_new['VolumeTradedBatch'] < i['VolumeTradedBatch']:
                        i['VolumeTradedBatch'] -= trade_new['VolumeTradedBatch']
                        break
                    # order_new的VolumeTradedBatch大于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif trade_new['VolumeTradedBatch'] > i['VolumeTradedBatch']:
                        trade_new['VolumeTradedBatch'] -= i['VolumeTradedBatch']
                        self.__list_position_detail_trade.remove(i)

    # 更新界面期货账户数据
    def update_panel_show_account(self):
        dict_args = dict()
        # 静态权益 PreBalance
        dict_args['PreBalance'] = self.__QryTradingAccount['PreBalance']
        # 入金金额 Deposit
        dict_args['Deposit'] = self.__QryTradingAccount['Deposit']
        # 出金金额 Withdraw
        dict_args['Withdraw'] = self.__QryTradingAccount['Withdraw']
        # 动态权益=静态权益+入金金额-出金金额+平仓盈亏+持仓盈亏-手续费
        dict_args['Capital'] = self.__QryTradingAccount['PreBalance'] + self.__QryTradingAccount['Deposit'] - self.__QryTradingAccount['Withdraw'] + self.__QryTradingAccount['CloseProfit'] + self.__QryTradingAccount['PositionProfit'] - self.__QryTradingAccount['Commission']
        self.signal_update_panel_show_account.emit(dict_args)

    # 窗口显示账户资金初始化信息
    def init_panel_show_account(self):
        # 动态权益=静态权益+入金金额-出金金额+平仓盈亏+持仓盈亏-手续费
        Capital = self.__QryTradingAccount['PreBalance'] + self.__QryTradingAccount['Deposit'] - \
                  self.__QryTradingAccount['Withdraw'] + self.__QryTradingAccount['CloseProfit'] + \
                  self.__QryTradingAccount['PositionProfit'] - self.__QryTradingAccount['Commission']
        self.__dict_panel_show_account = {
            'Capital': Capital,
            'PreBalance': self.__QryTradingAccount['PreBalance'],  # 静态权益
            'PositionProfit': self.__QryTradingAccount['PositionProfit'],  # 持仓盈亏
            'CloseProfit': self.__QryTradingAccount['CloseProfit'],  # 平仓盈亏
            'Commission': self.__QryTradingAccount['Commission'],  # 手续费
            'Available': self.__QryTradingAccount['Available'],  # 可用资金
            'CurrMargin': self.__QryTradingAccount['CurrMargin'],  # 占用保证金
            'FrozenMargin': self.__QryTradingAccount['FrozenMargin'],  # 下单冻结
            'Risk': self.__QryTradingAccount['CurrMargin'] / Capital,  # 风险度
            'Deposit': self.__QryTradingAccount['Deposit'],  # 今日入金
            'Withdraw': self.__QryTradingAccount['Withdraw']  # 今日出金
            }
        self.signal_update_panel_show_account.emit(self.__dict_panel_show_account)

        """
        # QryOrder无记录，从QryTradingAccount取数据
        if len(self.__list_QryOrder) == 0:
            # 动态权益=静态权益+入金金额-出金金额+平仓盈亏+持仓盈亏-手续费
            Capital = self.__QryTradingAccount['PreBalance'] + self.__QryTradingAccount['Deposit'] - self.__QryTradingAccount['Withdraw'] + self.__QryTradingAccount['CloseProfit'] + self.__QryTradingAccount['PositionProfit'] - self.__QryTradingAccount['Commission']
            self.__dict_panel_show_account = {
                'Capital': Capital,
                'PreBalance': self.__QryTradingAccount['PreBalance'],  # 静态权益
                'PositionProfit': self.__QryTradingAccount['PositionProfit'],  # 持仓盈亏
                'CloseProfit': self.__QryTradingAccount['CloseProfit'],  # 平仓盈亏
                'Commission': self.__QryTradingAccount['Commission'],  # 手续费
                'Available': self.__QryTradingAccount['Available'],  # 可用资金
                'CurrMargin': self.__QryTradingAccount['CurrMargin'],  # 占用保证金
                'FrozenMargin': self.__QryTradingAccount['FrozenMargin'],  # 下单冻结
                'Risk': self.__QryTradingAccount['CurrMargin'] / Capital,  # 风险度
                'Deposit': self.__QryTradingAccount['Deposit'],  # 今日入金
                'Withdraw': self.__QryTradingAccount['Withdraw']  # 今日出金
            }
        # QryOrder中有记录，遍历QryOrder计算账户资金数据
        elif len(self.__list_QryOrder) > 0:
            self.__dict_panel_show_account = {
                # 'Capital': Capital,
                'PreBalance': self.__QryTradingAccount['PreBalance'],  # 静态权益
                # 'PositionProfit': self.__QryTradingAccount['PositionProfit'],  # 持仓盈亏
                # 'CloseProfit': self.__QryTradingAccount['CloseProfit'],  # 平仓盈亏
                # 'Commission': self.__QryTradingAccount['Commission'],  # 手续费
                # 'Available': self.__QryTradingAccount['Available'],  # 可用资金
                # 'CurrMargin': self.__QryTradingAccount['CurrMargin'],  # 占用保证金
                # 'FrozenMargin': self.__QryTradingAccount['FrozenMargin'],  # 下单冻结
                # 'Risk': self.__QryTradingAccount['CurrMargin'] / Capital,  # 风险度
                'Deposit': self.__QryTradingAccount['Deposit'],  # 今日入金
                'Withdraw': self.__QryTradingAccount['Withdraw']  # 今日出金
            }
            for i in self.__list_QryOrder:
                # 平仓盈亏

                pass

        self.signal_update_panel_show_account.emit(self.__dict_panel_show_account)
        """

if __name__ == '__main__':
    print("User.py, if __name__ == '__main__':")
        


