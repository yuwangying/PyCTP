# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""

import time
import datetime
from pymongo import MongoClient
from PyCTP_Trade import PyCTP_Trader_API
import Utils
from pandas import DataFrame, Series
from PyQt4 import QtCore


class User(QtCore.QObject):
    signal_update_pushButton_start_strategy = QtCore.pyqtSignal()  # 定义信号：内核设置期货账户交易开关 -> 更新窗口“开始策略”按钮状态
    signal_label_login_error_text = QtCore.pyqtSignal(str)  # 定义信号：->更新登录窗口文本

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

        self.__list_OnRtnOrder = []  # 保存单账户所有的OnRtnOrder回调数据
        self.__list_OnRtnTrade = []  # 保存单账户所有的OnRtnTrade回调数据
        self.__list_SendOrder = []  # 保存单账户所有调用OrderInsert的记录
        self.__list_strategy = []  # 期货账户下面的所有交易策略实例列表
        # self.__list_InstrumentId = []  # 合约列表，记录撤单次数，在创建策略的时候添加合约，
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
        time.sleep(1.0)

        """查询资金账户"""
        self.__QryTradingAccount = self.__trader_api.QryTradingAccount()
        if isinstance(self.__QryTradingAccount, list):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTradingAccount'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询资金账户成功',
                  Utils.code_transform(self.__QryTradingAccount))
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTradingAccount'] = self.__QryTradingAccount
            print("User.__init__() user_id=", self.__user_id.decode(), '查询资金账户失败',
                  Utils.code_transform(self.__QryTradingAccount))
        time.sleep(1.0)

        """查询投资者持仓"""
        self.__QryInvestorPosition = self.__trader_api.QryInvestorPosition()
        if isinstance(self.__QryInvestorPosition, list):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryInvestorPosition'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询投资者持仓成功',
                  Utils.code_transform(self.__QryInvestorPosition))
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryInvestorPosition'] = self.__QryInvestorPosition
            print("User.__init__() user_id=", self.__user_id.decode(), '查询投资者持仓失败',
                  Utils.code_transform(self.__QryInvestorPosition))
        time.sleep(1.0)

        """查询成交记录"""
        self.__dfQryTrade = self.QryTrade()  # 保存查询当天的Trade和Order记录，正常值格式为DataFrame，异常值为None
        # QryTrade查询结果的状态记录到CTPManager的user状态字典，成功为0
        if isinstance(self.__dfQryTrade, DataFrame):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTrade'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询成交记录成功')
        else:
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryTrade'] = 1
            print("User.__init__() user_id=", self.__user_id.decode(), '查询成交记录失败')
        # self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['login_trade_account'] = login_trade_account
        time.sleep(1.0)

        """查询报单记录"""
        self.__dfQryOrder = self.QryOrder()
        # QryOrder查询结果的状态记录到CTPManager的user状态字典，成功为0
        if isinstance(self.__dfQryOrder, DataFrame):
            self.__ctp_manager.get_dict_user()[self.__user_id.decode()]['QryOrder'] = 0
            print("User.__init__() user_id=", self.__user_id.decode(), '查询报单记录成功')
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

    # 设置合约信息
    def set_InstrumentInfo(self, list_InstrumentInfo):
        self.__instrument_info = list_InstrumentInfo

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

    # time.sleep(1.0)
    # print("User.__init__.self.__instrument_info=", self.__instrument_info)

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

    # 获取报单引用part2
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
        t = datetime.datetime.now()
        Trade['OperatorID'] = self.__trader_id  # 客户端账号（也能区分用户身份或交易员身份）:OperatorID
        Trade['StrategyID'] = Trade['OrderRef'][-2:]  # 报单引用末两位是策略编号
        Trade['RecTradeTime'] = t.strftime("%Y-%m-%d %H:%M:%S")  # 收到成交回报的时间
        Trade['RecTradeMicrosecond'] = t.strftime("%f")  # 收到成交回报中的时间毫秒
        # self.__DBManager.insert_trade(Trade)  # 记录插入到数据库
        # if self.__mongo_client is not None:
        #     self.__mongo_client.CTP.get_collection(self.__user_id.decode()+'_Trade').insert_one(Trade)  # 记录插入到数据库
        # else:
        #     print("User.OnRtnTrade() self.__mongo_client is None")

    # 转PyCTP_Market_API类中回调函数OnRtnOrder
    def OnRtnOrder(self, Order):
        # print("User.OnRtnOrder()", 'OrderRef:', Order['OrderRef'], 'Order:', Order)
        self.action_counter(Order)  # 更新撤单计数字典
        # for i in self.__list_strategy:  # 转到strategy回调函数
        #     i.update_action_count()  # 更新策略内合约撤单计数变量
        #     if Order['OrderRef'][-2:] == i.get_strategy_id():  # 后两位数为策略id，找到对应的
        #         i.OnRtnOrder(Order)

        # 行情数据存档
        t = datetime.datetime.now()
        Order['OperatorID'] = self.__trader_id  # 客户端账号（也能区分用户身份或交易员身份）:OperatorID
        Order['StrategyID'] = Order['OrderRef'][-2:]  # 报单引用末两位是策略编号
        Order['RecOrderTime'] = t.strftime("%Y-%m-%d %H:%M:%S")  # 收到成交回报的时间
        Order['RecOrderMicrosecond'] = t.strftime("%f")  # 收到成交回报中的时间毫秒
        # self.__DBManager.insert_trade(Order)  # 记录插入到数据库
        # self.__mongo_client.CTP.get_collection(self.__user_id.decode()+'_Order').insert_one(Order)  # 记录插入到数据库

    # 转PyCTP_Market_API类中回调函数QryTrade
    def QryTrade(self):
        dfQryTrade = DataFrame()
        self.__listQryTrade = self.__trader_api.QryTrade()  # 返回正常值格式为list，错误值为int
        if isinstance(self.__listQryTrade, list):
            if len(self.__listQryTrade) > 0:
                for i in self.__listQryTrade:
                    # 将记录格式有list变为DataFrame
                    dfQryTrade = DataFrame.append(dfQryTrade, other=Utils.code_transform(i), ignore_index=True)
                # 添加列StrategyID：截取OrderRef后两位数为StrategyID
                dfQryTrade['StrategyID'] = dfQryTrade['OrderRef'].astype(str).str[-2:].astype(int)
        return dfQryTrade
        # print(">>> User.QryTrade() self.__listQryTrade=", self.__listQryTrade, type(self.__listQryTrade), len(self.__listQryTrade))
        # print("User.QryTrade() list_QryTrade =", self.__user_id, self.__listQryTrade)
        # if type(self.__listQryTrade) is int:
        #     return
        # if len(self.__listQryTrade) == 0:
        #     return
        # for i in self.__listQryTrade:
        #     self.__dfQryTrade = DataFrame.append(self.__dfQryTrade,
        #                                          other=Utils.code_transform(i),
        #                                          ignore_index=True)
        # self.__dfQryTrade['StrategyID'] = self.__dfQryTrade['OrderRef'].astype(str).str[-2:].astype(int)  # 截取OrderRef后两位数为StrategyID
        # # self.__dfQryTrade.to_csv("data/"+self.__user_id.decode()+"_dfQryTrade.csv")  # 保存数据到本地
        # return self.__dfQryTrade

    # 转PyCTP_Market_API类中回调函数QryOrder
    def QryOrder(self):
        dfQryOrder = DataFrame()
        self.__listQryOrder = self.__trader_api.QryOrder()
        if isinstance(self.__listQryOrder, list):
            if len(self.__listQryOrder) > 0:
                for i in self.__listQryOrder:
                    # 将记录格式有list变为DataFrame
                    dfQryOrder = DataFrame.append(dfQryOrder, other=Utils.code_transform(i), ignore_index=True)
                # 添加列StrategyID：截取OrderRef后两位数为StrategyID
                dfQryOrder['StrategyID'] = dfQryOrder['OrderRef'].astype(str).str[-2:].astype(int)
        return dfQryOrder
        # if len(self.__listQryOrder) == 0:
        #     return None
        # for i in self.__listQryOrder:
        #     dfQryOrder = DataFrame.append(dfQryOrder, other=Utils.code_transform(i), ignore_index=True)
        # dfQryOrder['StrategyID'] = dfQryOrder['OrderRef'].astype(str).str[-1:].astype(int)  # 截取OrderRef后两位数为StrategyID
        # # dfQryOrder.to_csv("data/" + self.__user_id.decode() + "_dfQryOrder.csv")  # 保存数据到本地
        # return dfQryOrder

    # 获取listQryOrder
    def get_listQryOrder(self):
        return self.__listQryOrder

    # 获取listQryTrade
    def get_listQryTrade(self):
        return self.__listQryTrade

    # 获取dfQryOrder
    def get_dfQryOrder(self):
        return self.__dfQryOrder

    # 获取dfQryTrade
    def get_dfQryTrade(self):
        return self.__dfQryTrade


if __name__ == '__main__':
    print("User.py, if __name__ == '__main__':")
        


