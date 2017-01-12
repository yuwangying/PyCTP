# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


import copy
import json
from PyCTP_Trade import PyCTP_Trader_API
from PyCTP_Market import PyCTP_Market_API
from OrderAlgorithm import OrderAlgorithm
import PyCTP
import time
import Utils
from pandas import DataFrame, Series
import pandas as pd
from PyQt4 import QtCore


class Strategy(QtCore.QObject):
    # 定义信号，必须放到__init__之前
    signal_UI_spread_short = QtCore.pyqtSignal(str)  # 定义信号，设置单账户窗口空头价差值
    signal_UI_spread_long = QtCore.pyqtSignal(str)
    signal_UI_spread_short_total = QtCore.pyqtSignal(str)
    signal_UI_spread_long_total = QtCore.pyqtSignal(str)
    signal_UI_spread_short_change_color = QtCore.pyqtSignal(str)  # 定义信号，设置单账户窗口空头价差颜色
    signal_UI_spread_long_change_color = QtCore.pyqtSignal(str)
    signal_UI_spread_short_total_change_color = QtCore.pyqtSignal(str)
    signal_UI_spread_long_total_change_color = QtCore.pyqtSignal(str)
    signal_UI_change_color = QtCore.pyqtSignal(str)  # 定义信号，改变颜色
    signal_UI_update_strategy = QtCore.pyqtSignal(object)  # 改写，所有策略对象的信号signal_UI_update_strategy分别连接到所有QAccountWidget对象的槽update_strategy
    signal_update_spread_signal = QtCore.pyqtSignal(dict)  # 改写：将策略对象信号signal_UI_update_spread_signal连接到策略所属的单账户窗口
    signal_update_spread_total = QtCore.pyqtSignal(dict)  # 改写：将策略对象信号signal_UI_update_spread_total连接到总账户窗口和所属的单账户窗口

    # 信号槽连接：策略对象修改策略 -> 界面刷新策略（Strategy.signal_update_strategy -> QAccountWidget.slot_update_strategy()）
    signal_update_strategy = QtCore.pyqtSignal(object)  # 形参为Strategy对象
    # 定义信号：策略发送信号 -> 修改持仓按钮设置为可用，并修改文本“发送持仓”改为“设置持仓”
    signal_pushButton_set_position_setEnabled = QtCore.pyqtSignal()

    # class Strategy功能:接收行情，接收Json数据，触发交易信号，将交易任务交给OrderAlgorithm
    def __init__(self, dict_args, obj_user, parent=None):
        super(Strategy, self).__init__(parent)  # 初始化父类
        print('Strategy.__init__() 创建交易策略，user_id=', dict_args['user_id'], 'strategy_id=', dict_args['strategy_id'])
        self.__user = obj_user  # user实例
        self.__ctp_manager = obj_user.get_CTPManager()  # 将user的CTPManager属性设置为strategy的属性
        self.__dict_args = dict_args  # 转存形参到类的私有变量
        self.__TradingDay = self.__user.GetTradingDay()  # 获取交易日
        self.__init_finished = False  # strategy初始化状态
        self.__trade_tasking = False  # 交易任务进行中
        self.__a_order_insert_args = dict()  # a合约报单参数
        self.__b_order_insert_args = dict()  # b合约报单参数
        self.__list_position_detail = list()  # 持仓明细列表
        self.__list_order_process = list()  # 未完成的order列表，未全部成交且未撤单
        self.__list_order_pending = list()  # 挂单列表，报单、成交、撤单回报
        self.__instrument_a_tick = None  # A合约tick（第一腿）
        self.__instrument_b_tick = None  # B合约tick（第二腿）
        self.__spread_long = None  # 市场多头价差：A合约买一价 - B合约买一价
        self.__spread_long_volume = None  # 市场多头价差盘口挂单量min(A合约买一量 - B合约买一量)
        self.__spread_short = None  # 市场空头价差：A合约卖一价 - B合约卖一价
        self.__spread_short_volume = None  # 市场空头价差盘口挂单量：min(A合约买一量 - B合约买一量)
        self.__spread = None  # 市场最新价价差
        self.__order_ref_a = None  # A合约报单引用
        self.__order_ref_b = None  # B合约报单引用
        self.__order_ref_last = None  # 最后一次实际使用的报单引用
        self.__dict_yesterday_position = dict()  # 本策略昨仓
        self.__position_a_buy = 0  # 策略持仓初始值为0
        self.__position_a_buy_today = 0
        self.__position_a_buy_yesterday = 0
        self.__position_a_sell = 0
        self.__position_a_sell_today = 0
        self.__position_a_sell_yesterday = 0
        self.__position_b_buy = 0
        self.__position_b_buy_today = 0
        self.__position_b_buy_yesterday = 0
        self.__position_b_sell = 0
        self.__position_b_sell_today = 0
        self.__position_b_sell_yesterday = 0
        self.__clicked_total = False  # 策略在主窗口中被选中的标志
        self.__clicked_signal = False  # 策略在单账户窗口中被选中的标志
        self.__dfQryTrade_Strategy = DataFrame()  # 本策略的查询当天交易记录
        self.__dfQryOrderStrategy = DataFrame()  # 本策略的查询当天委托记录
        self.__last_to_ui_spread_short = None  # 最后价差值初始值
        self.__last_to_ui_spread_long = None  # 最后价差值初始值
        # self.__short_color_black_times = 0
        # self.__long_color_black_times = 0
        # self.__short_total_color_black_times = 0
        # self.__long_total_color_black_times = 0
        self.__a_action_count = 0  # 撤单次数
        self.__b_action_count = 0

        self.set_arguments(dict_args)  # 设置策略参数
        # self.__user.add_instrument_id_action_counter(dict_args['list_instrument_id'])  # 将合约代码添加到user类的合约列表
        self.__a_price_tick = self.get_price_tick(self.__list_instrument_id[0])  # A合约最小跳价
        self.__b_price_tick = self.get_price_tick(self.__list_instrument_id[1])  # B合约最小跳价
        # 窗口初始化完成、程序运行中创建的策略，将显示前端窗口名称设置为其属性
        if self.__user.get_CTPManager().get_ClientMain().get_init_UI_finished():
            self.set_show_widget_name(self.__user.get_CTPManager().get_ClientMain().get_show_widget_name())
            self.__user.get_CTPManager().get_ClientMain().set_obj_new_strategy(self)  # 新建策略设置为ClientMain属性
        self.init_yesterday_position()  # 初始化策略昨仓
        # self.init_today_position()  # 初始化策略持仓
        # self.init_statistics()  # 初始化统计指标

    # 设置参数
    def set_arguments(self, dict_args):
        # print(">>> Strategy.set_arguments() user_id=", dict_args['user_id'], "strategy_id=", dict_args['strategy_id'])
        self.__dict_args = dict_args  # 将形参转存为私有变量
        # self.__DBManager.update_strategy(dict_args)  # 更新数据库

        self.__trader_id = dict_args['trader_id']
        self.__user_id = dict_args['user_id']
        self.__strategy_id = dict_args['strategy_id']
        self.__list_instrument_id = dict_args['list_instrument_id']  # 合约列表
        self.__a_instrument_id = self.__list_instrument_id[0]  # A合约代码
        self.__b_instrument_id = self.__list_instrument_id[1]  # B合约代码
        self.__trade_model = dict_args['trade_model']  # 交易模型
        self.__order_algorithm = dict_args['order_algorithm']  # 下单算法选择标志位
        self.__buy_open = dict_args['buy_open']  # 触发买开（开多单）
        self.__sell_close = dict_args['sell_close']  # 触发卖平（平多单）
        self.__sell_open = dict_args['sell_open']  # 触发卖开（开空单）
        self.__buy_close = dict_args['buy_close']  # 触发买平（平空单）
        self.__spread_shift = dict_args['spread_shift']  # 价差让价（超价触发）
        self.__a_wait_price_tick = dict_args['a_wait_price_tick']  # A合约挂单等待最小跳数
        self.__b_wait_price_tick = dict_args['b_wait_price_tick']  # B合约挂单等待最小跳数
        self.__stop_loss = dict_args['stop_loss']  # 止损，单位为最小跳数
        self.__lots = dict_args['lots']  # 总手
        self.__lots_batch = dict_args['lots_batch']  # 每批下单手数
        self.__a_order_action_limit = dict_args['a_order_action_limit']  # A合约撤单次数限制
        self.__b_order_action_limit = dict_args['b_order_action_limit']  # B合约撤单次数限制
        self.__on_off = dict_args['strategy_on_off']  # 策略开关，0关、1开
        self.__only_close = dict_args['only_close']  # 只平，0关、1开
        self.__sell_open_on_off = dict_args['sell_open_on_off']    # 价差卖开，开关，初始值为1，状态开
        self.__buy_close_on_off = dict_args['buy_close_on_off']    # 价差买平，开关，初始值为1，状态开
        self.__sell_close_on_off = dict_args['sell_close_on_off']  # 价差卖平，开关，初始值为1，状态开
        self.__buy_open_on_off = dict_args['buy_open_on_off']     # 价差买开，开关，初始值为1，状态开
        # print(">>> Strategy.set_arguments() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "dict_args=", dict_args)
        # 如果界面初始化完成、程序运行当中，每次调用该方法都触发界面类的槽函数update_strategy
        if self.__user.get_CTPManager().get_init_finished():
            print(">>> Strategy.set_arguments() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "修改策略参数，内核刷新界面")
            self.signal_update_strategy.emit(self)  # 信号槽连接：策略对象修改策略 -> 界面刷新策略

    # 获取参数
    def get_arguments(self):
        self.__dict_args = {
            'trader_id': self.__trader_id,
            'user_id': self.__user_id,
            'strategy_id': self.__strategy_id,
            'list_instrument_id': self.__list_instrument_id,
            'trade_model': self.__trade_model,
            'order_algorithm': self.__order_algorithm,
            'buy_open': self.__buy_open,
            'sell_close': self.__sell_close,
            'sell_open': self.__sell_open,
            'buy_close': self.__buy_close,
            'spread_shift': self.__spread_shift,
            'a_wait_price_tick': self.__a_wait_price_tick,
            'b_wait_price_tick': self.__b_wait_price_tick,
            'stop_loss': self.__stop_loss,
            'lots': self.__lots,
            'lots_batch': self.__lots_batch,
            'a_order_action_limit': self.__a_order_action_limit,
            'b_order_action_limit': self.__b_order_action_limit,
            'strategy_on_off': self.__on_off,
            'only_close': self.__only_close,
            'sell_open_on_off': self.__sell_open_on_off,
            'buy_close_on_off': self.__buy_close_on_off,
            'sell_close_on_off': self.__sell_close_on_off,
            'buy_open_on_off': self.__buy_open_on_off
        }
        # print(">>> Strategy.get_arguments() self.sender()=", self.sender(), " user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "self.__dict_args=", self.__dict_args)
        return self.__dict_args

    # 设置持仓
    def set_position(self, dict_args):
        # self.__DBManager.update_strategy(dict_args)  # 更新数据库
        self.__position_a_buy = dict_args['position_a_buy']
        self.__position_a_buy_today = dict_args['position_a_buy_today']
        self.__position_a_buy_yesterday = dict_args['position_a_buy_yesterday']
        self.__position_a_sell = dict_args['position_a_sell']
        self.__position_a_sell_today = dict_args['position_a_sell_today']
        self.__position_a_sell_yesterday = dict_args['position_a_sell_yesterday']
        self.__position_b_buy = dict_args['position_b_buy']
        self.__position_b_buy_today = dict_args['position_b_buy_today']
        self.__position_b_buy_yesterday = dict_args['position_b_buy_yesterday']
        self.__position_b_sell = dict_args['position_b_sell']
        self.__position_b_sell_today = dict_args['position_b_sell_today']
        self.__position_b_sell_yesterday = dict_args['position_b_sell_yesterday']
        print(">>> Strategy.set_position() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "dict_args=", dict_args)
        # 如果界面初始化完成、程序运行当中，每次调用该方法都触发界面类的槽函数update_strategy
        if self.__user.get_CTPManager().get_init_finished():
            print(">>> Strategy.set_arguments() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "修改策略参数，内核刷新界面")
            self.signal_pushButton_set_position_setEnabled.emit()
            self.signal_update_strategy.emit(self)  # 信号槽连接：策略对象修改策略 -> 界面刷新策略

    # 程序运行中查询策略信息，收到服务端消息之后设置策略实例参数
    def set_arguments_query_strategy_info(self, dict_args):
        print(">>> Strategy.set_arguments_query_strategy_info() user_id=", self.__user_id, "strategy_id=", self.__strategy_id)
        self.__dict_args = dict_args  # 将形参转存为私有变量
        # self.__DBManager.update_strategy(dict_args)  # 更新数据库

        self.__trader_id = dict_args['trader_id']
        self.__user_id = dict_args['user_id']
        self.__strategy_id = dict_args['strategy_id']
        self.__trade_model = dict_args['trade_model']  # 交易模型
        self.__order_algorithm = dict_args['order_algorithm']  # 下单算法选择标志位
        self.__list_instrument_id = dict_args['list_instrument_id']  # 合约列表
        self.__buy_open = dict_args['buy_open']  # 触发买开（开多单）
        self.__sell_close = dict_args['sell_close']  # 触发卖平（平多单）
        self.__sell_open = dict_args['sell_open']  # 触发卖开（开空单）
        self.__buy_close = dict_args['buy_close']  # 触发买平（平空单）
        self.__spread_shift = dict_args['spread_shift']  # 价差让价（超价触发）
        self.__a_wait_price_tick = dict_args['a_wait_price_tick']  # A合约挂单等待最小跳数
        self.__b_wait_price_tick = dict_args['b_wait_price_tick']  # B合约挂单等待最小跳数
        self.__stop_loss = dict_args['stop_loss']  # 止损，单位为最小跳数
        self.__lots = dict_args['lots']  # 总手
        self.__lots_batch = dict_args['lots_batch']  # 每批下单手数
        self.__a_order_action_limit = dict_args['a_order_action_limit']  # A合约撤单次数限制
        self.__a_order_action_limit = dict_args['b_order_action_limit']  # B合约撤单次数限制
        self.__on_off = dict_args['strategy_on_off']  # 策略开关，0关、1开
        self.__only_close = dict_args['only_close']  # 只平，0关、1开

    # 查询策略昨仓
    def QryStrategyYesterdayPosition(self):
        dict_QryStrategyYesterdayPosition = {'MsgRef': self.__user.get_CTPManager().get_ClientMain().get_SocketManager().msg_ref_add(),
                                             'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                             'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                             'MsgType': 10,  # 查询策略昨仓
                                             'TraderID': self.__trader_id,
                                             'UserID': self.__user_id,
                                             'StrategyID': self.__strategy_id
                                             }
        json_QryStrategyYesterdayPosition = json.dumps(dict_QryStrategyYesterdayPosition)
        self.__user.get_CTPManager().get_ClientMain().get_SocketManager().send_msg(json_QryStrategyYesterdayPosition)

    # 查询策略昨仓响应
    def OnRspQryStrategyYesterdayPosition(self, dict_StrategyYesterdayPosition):
        self.__dict_StrategyYesterdayPosition = copy.deepcopy(dict_StrategyYesterdayPosition)
        # print(">>> Strategy.OnRspQryStrategyYesterdayPosition() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "self.__dict_StrategyYesterdayPosition=\n\t", self.__dict_StrategyYesterdayPosition)

    # 初始化昨仓，从服务端获得数据计算
    def init_yesterday_position(self):
        # 所有策略昨仓的list中无数据
        list_yesterday_position = self.__ctp_manager.get_SocketManager().get_list_yesterday_position()
        if len(list_yesterday_position) > 0:
            for i in list_yesterday_position:
                if i['user_id'] == self.__user_id and i['strategy_id'] == self.__strategy_id:
                    self.__dict_yesterday_position = copy.deepcopy(i)
                    self.__position_a_buy = self.__dict_yesterday_position['position_a_buy']
                    self.__position_a_buy_today = 0
                    self.__position_a_buy_yesterday = self.__dict_yesterday_position['position_a_buy']
                    self.__position_a_sell = self.__dict_yesterday_position['position_a_sell']
                    self.__position_a_sell_today = 0
                    self.__position_a_sell_yesterday = self.__dict_yesterday_position['position_a_sell']
                    self.__position_b_buy = self.__dict_yesterday_position['position_b_buy']
                    self.__position_b_buy_today = 0
                    self.__position_b_buy_yesterday = self.__dict_yesterday_position['position_b_buy']
                    self.__position_b_sell = self.__dict_yesterday_position['position_b_sell']
                    self.__position_b_sell_today = 0
                    self.__position_b_sell_yesterday = self.__dict_yesterday_position['position_b_sell']
        d1 = self.get_position()
        self.init_today_position()  # 昨仓初始化完成，调用初始化今仓

    # 初始化今仓，从当天成交回报数据计算
    def init_today_position(self):
        # 待续，2017年1月6日22:28:44，待修复更新仓位持仓变量全部为int
        # print("Strategy.init_today_position() user_id=", self.__user_id, "strategy_id=", self.__strategy_id)

        # print(">>> self.get_position()['position_a_sell_today']=", self.get_position()['position_a_sell_today'], type(self.get_position()['position_a_sell_today']))
        if len(self.__user.get_dfQryTrade()) > 0:  # user的交易记录为0跳过
            self.__dfQryTrade = self.__user.get_dfQryTrade()  # 获得user的交易记录
            # 从user的Trade中筛选出该策略的记录
            self.__dfQryTrade_Strategy = self.__dfQryTrade[self.__dfQryTrade.StrategyID == int(self.__strategy_id)]
        if len(self.__dfQryTrade_Strategy) > 0:  # strategy的交易记录为0跳过
            # 遍历本策略的trade记录，更新今仓
            for i in self.__dfQryTrade_Strategy.index:
                # print(">>> self.__dfQryTrade_Strategy['Volume'][i]", self.__dfQryTrade_Strategy['Volume'][i], type(self.__dfQryTrade_Strategy['Volume'][i]))
                # A成交
                if self.__dfQryTrade_Strategy['InstrumentID'][i] == self.__list_instrument_id[0]:
                    if self.__dfQryTrade_Strategy['OffsetFlag'][i] == '0':  # A开仓成交回报
                        if self.__dfQryTrade_Strategy['Direction'][i] == '0':  # A买开仓成交回报
                            self.__position_a_buy_today += self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                        elif self.__dfQryTrade_Strategy['Direction'][i] == '1':  # A卖开仓成交回报
                            print(">>> Strategy.init_today_position() self.__dfQryTrade_Strategy['Volume'][i]=", self.__dfQryTrade_Strategy['Volume'][i], type(self.__dfQryTrade_Strategy['Volume'][i]))
                            self.__position_a_sell_today += self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                    elif self.__dfQryTrade_Strategy['OffsetFlag'][i] == '3':  # A平今成交回报
                        if self.__dfQryTrade_Strategy['Direction'][i] == '0':  # A买平今成交回报
                            self.__position_a_sell_today -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                        elif self.__dfQryTrade_Strategy['Direction'][i] == '1':  # A卖平今成交回报
                            self.__position_a_buy_today -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                    elif self.__dfQryTrade_Strategy['OffsetFlag'][i] == '4':  # A平昨成交回报
                        if self.__dfQryTrade_Strategy['Direction'][i] == '0':  # A买平昨成交回报
                            self.__position_a_sell_yesterday -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                        elif self.__dfQryTrade_Strategy['Direction'][i] == '1':  # A卖平昨成交回报
                            self.__position_a_buy_yesterday -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                    self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
                    self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
                # B成交
                elif self.__dfQryTrade_Strategy['InstrumentID'][i] == self.__list_instrument_id[1]:
                    if self.__dfQryTrade_Strategy['OffsetFlag'][i] == '0':  # B开仓成交回报
                        if self.__dfQryTrade_Strategy['Direction'][i] == '0':  # B买开仓成交回报
                            self.__position_b_buy_today += self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                        elif self.__dfQryTrade_Strategy['Direction'][i] == '1':  # B卖开仓成交回报
                            self.__position_b_sell_today += self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                    elif self.__dfQryTrade_Strategy['OffsetFlag'][i] == '3':  # B平今成交回报
                        if self.__dfQryTrade_Strategy['Direction'][i] == '0':  # B买平今成交回报
                            self.__position_b_sell_today -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                        elif self.__dfQryTrade_Strategy['Direction'][i] == '1':  # B卖平今成交回报
                            self.__position_b_buy_today -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                    elif self.__dfQryTrade_Strategy['OffsetFlag'][i] == '4':  # B平昨成交回报
                        if self.__dfQryTrade_Strategy['Direction'][i] == '0':  # B买平昨成交回报
                            self.__position_b_sell_yesterday -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                        elif self.__dfQryTrade_Strategy['Direction'][i] == '1':  # B卖平昨成交回报
                            self.__position_b_buy_yesterday -= self.__dfQryTrade_Strategy['Volume'][i]  # 更新持仓
                    self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
                    self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
                if Utils.Strategy_print:
                    print("Strategy.init_today_position() ", self.__list_instrument_id[0], "买(", self.__position_a_buy, ",", self.__position_a_buy_yesterday, ")", " 卖(", self.__position_a_sell, ",", self.__position_a_sell_yesterday, ")")
                    print("Strategy.init_today_position() ", self.__list_instrument_id[1], "买(", self.__position_b_buy, ",", self.__position_b_buy_yesterday, ")", " 卖(", self.__position_b_sell, ",", self.__position_b_sell_yesterday, ")")
        # print(">>> self.get_position()['position_a_sell_today']=", self.get_position()['position_a_sell_today'], type(self.get_position()['position_a_sell_today']))
        self.__init_finished = True  # 当前策略初始化完成
        d1 = self.get_position()

    # 设置strategy初始化状态
    def set_init_finished(self, bool_input):
        self.__init_finished = bool_input
    
    # 获取strategy初始化状态
    def get_init_finished(self):
        return self.__init_finished

    # 设置数据库连接实例
    def set_DBManager(self, obj_DBManager):
        self.__DBManager = obj_DBManager  # 数据库连接实例

    def get_DBManager(self):
        return self.__DBManager

    # 设置user对象
    def set_user(self, user):
        self.__user = user

    # 获取user对象
    def get_user(self, user):
        return self.__user

    # 获取trader_id
    def get_trader_id(self):
        return self.__trader_id

    # 获取user_id
    def get_user_id(self):
        return self.__user_id

    # 获取strategy_id
    def get_strategy_id(self):
        return self.__strategy_id

    # 获取self.__list_instrument_id
    def get_list_instrument_id(self):
        return self.__list_instrument_id

    def get_a_instrument_id(self):
        return self.__a_instrument_id

    def get_b_instrument_id(self):
        return self.__b_instrument_id

    # 获取指定合约最小跳'PriceTick'
    def get_price_tick(self, instrument_id):
        for i in self.__user.get_CTPManager().get_instrument_info():
            if i['InstrumentID'] == instrument_id:
                return i['PriceTick']
    
    # # 更新撤单次数，在user类中的order回调中调用，第一时间更新撤单计数
    # def update_action_count(self):
    #     self.__a_action_count = self.__user.get_dict_action()[self.__a_instrument_id]
    #     self.__b_action_count = self.__user.get_dict_action()[self.__b_instrument_id]

    def set_a_action_count(self, int_count):
        self.__a_action_count = int_count

    def set_b_action_count(self, int_count):
        self.__b_action_count = int_count

    def get_a_action_count(self):
        return self.__a_action_count

    def get_b_action_count(self):
        return self.__b_action_count

    # 获取策略交易开关
    def get_on_off(self):
        return self.__on_off

    def set_on_off(self, int_input):
        self.__on_off = int_input
        self.signal_update_strategy.emit(self)

    # 获取策略只平开关
    def get_only_close(self):
        return self.__only_close

    def set_only_close(self, int_input):
        self.__only_close = int_input
        self.signal_update_strategy.emit(self)

    def get_spread_short(self):
        return self.__spread_short

    def get_spread_long(self):
        return self.__spread_long

    def set_clicked_status(self, int_input):  # 0：未选中、1：单账户窗口中被选中、2：总账户窗口中被选中
        self.__clicked_status = int_input

    def get_position(self):
        out_dict = {
            'position_a_buy': self.__position_a_buy,
            'position_a_buy_today': self.__position_a_buy_today,
            'position_a_buy_yesterday': self.__position_a_buy_yesterday,
            'position_a_sell': self.__position_a_sell,
            'position_a_sell_today': self.__position_a_sell_today,
            'position_a_sell_yesterday': self.__position_a_sell_yesterday,
            'position_b_buy': self.__position_b_buy,
            'position_b_buy_today': self.__position_b_buy_today,
            'position_b_buy_yesterday': self.__position_b_buy_yesterday,
            'position_b_sell': self.__position_b_sell,
            'position_b_sell_today': self.__position_b_sell_today,
            'position_b_sell_yesterday': self.__position_b_sell_yesterday,
        }
        return out_dict

    # 设置当前策略在单账户窗口被选中的状态，True：被选中，False：未被选中
    def set_clicked_signal(self, bool_input):
        self.__clicked_signal = bool_input
        # print(">>> Strategy.set_clicked_signal() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "self.__clicked_signal=", self.__clicked_signal)

    def get_clicked_signal(self):
        return self.__clicked_signal

    # 设置当前策略在总账户窗口被选中的状态，True：被选中，False：未被选中
    def set_clicked_total(self, bool_input):
        self.__clicked_total = bool_input
        # print(">>> Strategy.set_clicked_total() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "self.__clicked_total=", self.__clicked_total)

    def get_clicked_total(self):
        return self.__clicked_total

    # QAccountWidegt设置为属性
    def set_QAccountWidget_signal(self, obj_QAccountWidget):
        self.__QAccountWidget_signal = obj_QAccountWidget
        # self.signal_UI_spread_long.connect(self.__QAccountWidget_signal.lineEdit_duotoujiacha.setText)  # 信号绑定，刷新单账户窗口多头价差值
        # self.signal_UI_spread_short.connect(self.__QAccountWidget_signal.lineEdit_kongtoujiacha.setText)  # 信号绑定，刷新单账户窗口空头价差值
        # self.signal_UI_spread_long_change_color.connect(self.__QAccountWidget_signal.lineEdit_duotoujiacha.setStyleSheet)  # 信号绑定，刷新单账户窗口空头价差颜色
        # self.signal_UI_spread_short_change_color.connect(self.__QAccountWidget_signal.lineEdit_kongtoujiacha.setStyleSheet)  # 信号绑定，刷新单账户窗口多头价差颜色
        # self.signal_update_spread_signal.connect(self.__QAccountWidget_signal.update_spread)  # 改写

    def get_QAccountWidget(self):
        return self.__QAccountWidget_signal

    # QAccountWidegtTotal设置为属性（总账户的窗口）
    def set_QAccountWidget_total(self, obj_QAccountWidgetTotal):
        self.__QAccountWidget_total = obj_QAccountWidgetTotal
        # self.signal_UI_spread_long_total.connect(self.__QAccountWidget_total.lineEdit_duotoujiacha.setText)  # 信号槽绑定
        # self.signal_UI_spread_short_total.connect(self.__QAccountWidget_total.lineEdit_kongtoujiacha.setText)  # 信号槽绑定
        # self.signal_UI_spread_long_total_change_color.connect(self.__QAccountWidget_total.lineEdit_duotoujiacha.setStyleSheet)
        # self.signal_UI_spread_short_total_change_color.connect(self.__QAccountWidget_total.lineEdit_kongtoujiacha.setStyleSheet)
        # self.signal_update_spread_total.connect(self.__QAccountWidget_total.update_spread)  # 改写

    def get_QAccountWidgetTotal(self):
        return self.__QAccountWidget_total

    # 设置当前界面显示的窗口名称
    def set_show_widget_name(self, str_widget_name):
        self.__show_widget_name = str_widget_name
        # print(">>> Strategy.set_show_widget_name() user_id=", self.__user_id, "strategy_id=", self.__strategy_id , "show_widget_name=", self.__show_widget_name)

    def get_show_widget_name(self):
        return self.__show_widget_name

    # 生成报单引用，前两位是策略编号，后面几位递增1
    def add_order_ref(self):
        return (str(self.__user.add_order_ref_part2()) + self.__strategy_id).encode()

    # 回调函数：行情推送
    def OnRtnDepthMarketData(self, tick):
        """ 行情推送 """
        # print(">>> Strategy.OnRtnDepthMarketData() tick=", tick)
        if tick is None:
            return
        if isinstance(tick['BidPrice1'], float) is False:
            return
        if isinstance(tick['AskPrice1'], float) is False:
            return
        if isinstance(tick['BidVolume1'], int) is False:
            return
        if isinstance(tick['AskVolume1'], int) is False:
            return

        # 策略初始化未完成，跳过
        if self.__init_finished is False:
            # print("Strategy.OnRtnDepthMarketData() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "策略初始化未完成")
            return
        # CTPManager初始化未完成，跳过
        if self.__user.get_CTPManager().get_init_finished() is False:
            return
        # 窗口创建完成
        if self.__user.get_CTPManager().get_ClientMain().get_init_UI_finished() is False:
            return
        # 没有任何一个窗口显示，跳过
        if self.__user.get_CTPManager().get_ClientMain().get_showEvent() is False:
            return

        # 过滤出B合约的tick
        if tick['InstrumentID'] == self.__list_instrument_id[1]:
            self.__instrument_b_tick = copy.deepcopy(tick)
            # print(self.__user_id + self.__strategy_id, "B合约：", self.__instrument_b_tick)
        # 过滤出A合约的tick
        elif tick['InstrumentID'] == self.__list_instrument_id[0]:
            self.__instrument_a_tick = copy.deepcopy(tick)
            # print(self.__user_id + self.__strategy_id, "A合约：", self.__instrument_a_tick)

        # 计算市场盘口价差、量
        if self.__instrument_a_tick is None or self.__instrument_b_tick is None:
            return
        self.__spread_long = self.__instrument_a_tick['BidPrice1'] - self.__instrument_b_tick['AskPrice1']
        self.__spread_long_volume = min(self.__instrument_a_tick['BidVolume1'], self.__instrument_b_tick['AskVolume1'])
        self.__spread_short = self.__instrument_a_tick['AskPrice1'] - self.__instrument_b_tick['BidPrice1']
        self.__spread_short_volume = min(self.__instrument_a_tick['AskVolume1'], self.__instrument_b_tick['BidVolume1'])

        # 没有下单任务执行中，进入选择下单算法
        if not self.__trade_tasking:
            self.select_order_algorithm(self.__order_algorithm)
        # 有下单任务执行中，跟踪交易任务
        elif self.__trade_tasking:
            dict_args = {'flag': 'tick', 'tick': tick}
            self.trade_task(dict_args)

        # 刷新界面价差
        self.spread_to_ui()

    def OnRspOrderInsert(self, InputOrder, RspInfo, RequestID, IsLast):
        """ 报单录入请求响应 """
        # 报单错误时响应
        if Utils.Strategy_print:
            print('Strategy.OnRspOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo, 'RequestID:', RequestID, 'IsLast:', IsLast)
        dict_args = {'flag': 'OnRspOrderInsert',
                     'InputOrder': InputOrder,
                     'RspInfo': RspInfo,
                     'RequestID': RequestID,
                     'IsLast': IsLast}
        self.trade_task(dict_args)  # 转到交易任务处理

    def OnRspOrderAction(self, InputOrderAction, RspInfo, RequestID, IsLast):
        """报单操作请求响应:撤单操作响应"""
        if Utils.Strategy_print:
            print('Strategy.OnRspOrderAction()', 'OrderRef:', InputOrderAction['OrderRef'], 'InputOrderAction:', InputOrderAction, 'RspInfo:', RspInfo, 'RequestID:', RequestID, 'IsLast:', IsLast)
        dict_args = {'flag': 'OnRspOrderAction',
                     'InputOrderAction': InputOrderAction,
                     'RspInfo': RspInfo,
                     'RequestID': RequestID,
                     'IsLast': IsLast}
        self.trade_task(dict_args)  # 转到交易任务处理

    def OnRtnOrder(self, Order):
        """报单回报"""
        from User import User
        if Utils.Strategy_print:
            print('Strategy.OnRtnOrder()', 'OrderRef:', Order['OrderRef'], 'Order', Order)
        self.__user.action_counter(Order)  # 更新撤单计数
        self.update_list_order_process(Order)  # 更新挂单列表
        dict_args = {'flag': 'OnRtnOrder', 'Order': Order}
        self.update_list_order_pending(dict_args)  # 更新挂单list，形参改为Order
        order_new = self.add_VolumeTradedBatch(Order)  # 添加字段，本次成交量
        self.update_list_position_detail(order_new)  # 更新持仓明细list，待续，形参有Trade改为Order
        # self.update_position(Order)  # 更新持仓变量，待续，形参有Trade改为Order
        self.update_task_status()  # 更新交易执行任务状态
        # self.__user.action_counter(dict_args['Order']['InstrumentID'])  # 更新撤单计数
        self.trade_task(dict_args)  # 转到交易任务处理

    def OnRtnTrade(self, Trade):
        """成交回报"""
        if Utils.Strategy_print:
            print('Strategy.OnRtnTrade()', 'OrderRef:', Trade['OrderRef'], 'Trade', Trade)
        # self.update_list_position_detail(Trade)  # 更新持仓明细list
        # self.update_position(Trade)  # 更新持仓量变量
        self.update_task_status()  # 更新任务状态
        dict_args = {'flag': 'OnRtnTrade', 'Trade': Trade}
        self.trade_task(dict_args)  # 转到交易任务处理

    def OnErrRtnOrderAction(self, OrderAction, RspInfo):
        """ 报单操作错误回报 """
        if Utils.Strategy_print:
            print('Strategy.OnErrRtnOrderAction()', 'OrderRef:', OrderAction['OrderRef'], 'OrderAction:', OrderAction, 'RspInfo:', RspInfo)
        dict_args = {'flag': 'OnErrRtnOrderAction', 'OrderAction': OrderAction, 'RspInfo': RspInfo}
        self.trade_task(dict_args)  # 转到交易任务处理

    def OnErrRtnOrderInsert(self, InputOrder, RspInfo):
        """报单录入错误回报"""
        if Utils.Strategy_print:
            print('Strategy.OnErrRtnOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo)
        dict_args = {'flag': 'OnErrRtnOrderInsert',
                     'InputOrder': InputOrder,
                     'RspInfo': RspInfo}
        self.trade_task(dict_args)  # 转到交易任务处理

    # 选择下单算法
    def select_order_algorithm(self, flag):
        # 有挂单
        if len(self.__list_order_pending) > 0:
            return
        # 撇退
        if self.__position_a_sell != self.__position_b_buy or self.__position_a_buy != self.__position_b_sell:
            return
        # 选择执行交易算法
        if flag == '01':
            self.order_algorithm_one()
        elif flag == '02':
            self.order_algorithm_two()
        elif flag == '03':
            self.order_algorithm_three()
        else:
            # print("Strategy.select_order_algorithm() 没有选择下单算法")
            pass

    # 价差显示到界面
    def spread_to_ui(self):
        # print(">>> Strategy.market_spread() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "self.__clicked_signal=", self.__clicked_signal, "self.__clicked_total=", self.__clicked_total)
        if self.__clicked_total:  # 在总账户窗口中被选中，向总账户窗口对象发送刷新价差信号
            # 筛选发送信号
            # 第一个行情
            if self.__last_to_ui_spread_short is None or self.__last_to_ui_spread_long is None:
                self.signal_update_spread_total.emit({'spread_long': self.__spread_long, 'spread_short': self.__spread_short})
            # 最新价差值较前值发生变化则发送刷新界面的信号
            elif self.__last_to_ui_spread_short != self.__spread_short or self.__last_to_ui_spread_long != self.__spread_long:
                self.signal_update_spread_total.emit({'spread_long': self.__spread_long, 'spread_short': self.__spread_short})
        if self.__clicked_signal:  # 在单账户窗口中被选中，向策略所属的单账户窗口对象发送刷新价差信号
            # 筛选发送信号
            # 第一个行情
            if self.__last_to_ui_spread_short is None or self.__last_to_ui_spread_long is None:
                self.signal_update_spread_signal.emit({'spread_long': self.__spread_long, 'spread_short': self.__spread_short})
            # 最新价差值较前值发生变化则发送刷新界面的信号
            elif self.__last_to_ui_spread_short != self.__spread_short or self.__last_to_ui_spread_long != self.__spread_long:
                self.signal_update_spread_signal.emit({'spread_long': self.__spread_long, 'spread_short': self.__spread_short})
        # 最后一次向界面发送的价差值
        self.__last_to_ui_spread_short = self.__spread_short
        self.__last_to_ui_spread_long = self.__spread_long

    # 下单算法1：A合约以对手价发单，B合约以对手价发单
    def order_algorithm_one(self):
        # 有任何一个合约是无效行情则跳过
        if self.__instrument_a_tick is not None or self.__instrument_b_tick is not None:
            return

        # 策略开关为关则直接跳出，不执行开平仓逻辑判断，依次为：策略开关、单个期货账户开关（user）、总开关（trader）
        if self.__on_off == 0 or self.__user.get_on_off() == 0 or self.__user.get_CTPManager().get_on_off() == 0:
            print("Strategy.order_algorithm_one() 策略开关状态", self.__on_off, self.__user.get_on_off(), self.__user.get_CTPManager().get_on_off())
            return

        # 价差卖平
        if self.__spread_long >= self.__sell_close \
                and self.__position_a_sell == self.__position_b_buy \
                and self.__position_a_sell > 0:
            '''
                市场多头价差大于等于策略卖平触发参数
                A、B合约持仓量相等且大于0
            '''
            if Utils.Strategy_print:
                print("Strategy.order_algorithm_one() 策略编号", self.__strategy_id, "交易信号触发", "价差买平")
            # 打印价差
            if Utils.Strategy_print:
                print("Strategy.order_algorithm_one() 策略编号", self.__user_id + self.__strategy_id,
                      self.__list_instrument_id, self.__spread_long, "(", self.__spread_long_volume, ")",
                      self.__spread_short, "(", self.__spread_short_volume, ")")
            # 满足交易任务之前的一个tick
            self.__instrument_a_tick_after_tasking = self.__instrument_a_tick
            self.__instrument_b_tick_after_tasking = self.__instrument_b_tick
            # 优先平昨仓
            # 报单手数：盘口挂单量、每份发单手数、持仓量
            if self.__position_a_sell_yesterday > 0:
                order_volume = min(self.__spread_short_volume,
                                   self.__lots_batch,
                                   self.__position_a_sell_yesterday)
                CombOffsetFlag = b'4'  # 平昨标志
            elif self.__position_a_sell_yesterday == 0 and self.__position_a_sell_today > 0:
                order_volume = min(self.__spread_short_volume,
                                   self.__lots_batch,
                                   self.__position_a_sell_today)
                CombOffsetFlag = b'3'  # 平今标志
            if order_volume <= 0 or not isinstance(order_volume, int):
                if Utils.Strategy_print:
                    print('Strategy.order_algorithm_one() 发单手数错误值', order_volume)
            self.__order_ref_a = self.add_order_ref()  # 报单引用
            self.__order_ref_last = self.__order_ref_a
            # A合约报单参数，全部确定
            self.__a_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          'OrderRef': self.__order_ref_a,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[0].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_a_tick['BidPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_b_tick['AskPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            self.trade_task(self.__a_order_insert_args)  # 执行下单任务
            self.__trade_tasking = True  # 交易任务执行中
        # 价差买平
        elif self.__spread_short <= self.__buy_close\
                and self.__position_a_sell == self.__position_b_buy\
                and self.__position_a_sell > 0:
            '''
                市场空头价差小于等于策略买平触发参数
                A、B合约持仓量相等且大于0
            '''
            if Utils.Strategy_print:
                print("Strategy.order_algorithm_one() 策略编号", self.__strategy_id, "交易信号触发", "价差买平")
            # 打印价差
            if Utils.Strategy_print:
                print("Strategy.order_algorithm_one() 策略编号", self.__user_id + self.__strategy_id, self.__list_instrument_id, self.__spread_long, "(", self.__spread_long_volume, ")", self.__spread_short, "(", self.__spread_short_volume, ")")
            # 满足交易任务之前的一个tick
            self.__instrument_a_tick_after_tasking = self.__instrument_a_tick
            self.__instrument_b_tick_after_tasking = self.__instrument_b_tick
            # 优先平昨仓
            # 报单手数：盘口挂单量、每份发单手数、持仓量
            if self.__position_a_sell_yesterday > 0:
                order_volume = min(self.__spread_short_volume,
                                   self.__lots_batch,
                                   self.__position_a_sell_yesterday)
                CombOffsetFlag = b'4'  # 平昨标志
            elif self.__position_a_sell_yesterday == 0 and self.__position_a_sell_today > 0:
                order_volume = min(self.__spread_short_volume,
                                   self.__lots_batch,
                                   self.__position_a_sell_today)
                CombOffsetFlag = b'3'  # 平今标志
            if order_volume <= 0 or not isinstance(order_volume, int):
                if Utils.Strategy_print:
                    print('Strategy.order_algorithm_one() 发单手数错误值', order_volume)
            self.__order_ref_a = self.add_order_ref()  # 报单引用
            self.__order_ref_last = self.__order_ref_a
            # A合约报单参数，全部确定
            self.__a_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          'OrderRef': self.__order_ref_a,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[0].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_a_tick['AskPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_b_tick['BidPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            self.trade_task(self.__a_order_insert_args)  # 执行下单任务
            self.__trade_tasking = True  # 交易任务执行中
        # 价差卖开
        elif self.__spread_long >= self.__sell_open \
                and self.__position_a_buy + self.__position_a_sell < self.__lots:
            '''
            市场多头价差大于策略卖开触发参数
            策略多头持仓量+策略空头持仓量小于策略参数总手
            '''
            if Utils.Strategy_print:
                print("Strategy.order_algorithm_one() 策略编号", self.__strategy_id, "交易信号触发", "价差卖开")
            # 打印价差
            if Utils.Strategy_print:
                print(self.__user_id + self.__strategy_id, self.__list_instrument_id, self.__spread_long, "(",
                      self.__spread_long_volume, ")", self.__spread_short, "(", self.__spread_short_volume, ")")
            # 满足交易任务之前的一个tick
            self.__instrument_a_tick_after_tasking = self.__instrument_a_tick
            self.__instrument_b_tick_after_tasking = self.__instrument_b_tick
            # 报单手数：盘口挂单量、每份发单手数、剩余可开仓手数中取最小值
            order_volume = min(self.__spread_long_volume,  # 市场对手量
                               self.__lots_batch,  # 每份量
                               self.__lots - (self.__position_a_buy + self.__position_b_buy))  # 剩余可开数量
            if order_volume <= 0 or not isinstance(order_volume, int):
                if Utils.Strategy_print:
                    print('Strategy.order_algorithm_one() 发单手数错误值', order_volume)
            self.__order_ref_a = self.add_order_ref()  # 报单引用
            self.__order_ref_last = self.__order_ref_a
            # A合约报单参数，全部确定
            self.__a_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          'OrderRef': self.__order_ref_a,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[0].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_a_tick['BidPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_b_tick['AskPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            self.trade_task(self.__a_order_insert_args)  # 执行下单任务
            self.__trade_tasking = True  # 交易任务执行中

        # 价差买开
        elif self.__spread_short <= self.__buy_open \
                and self.__position_a_buy + self.__position_a_sell < self.__lots:
            '''
            市场空头价差小于策略买开触发参数
            策略多头持仓量+策略空头持仓量小于策略参数总手
            '''
            if Utils.Strategy_print:
                print("Strategy.order_algorithm_one() 策略编号", self.__strategy_id, "交易信号触发", "价差卖开")
            # 打印价差
            if Utils.Strategy_print:
                print(self.__user_id + self.__strategy_id, self.__list_instrument_id, self.__spread_long, "(",
                      self.__spread_long_volume, ")", self.__spread_short, "(", self.__spread_short_volume, ")")
            # 满足交易任务之前的一个tick
            self.__instrument_a_tick_after_tasking = self.__instrument_a_tick
            self.__instrument_b_tick_after_tasking = self.__instrument_b_tick
            # 报单手数：盘口挂单量、每份发单手数、剩余可开仓手数中取最小值
            order_volume = min(self.__spread_long_volume,  # 市场对手量
                               self.__lots_batch,  # 每份量
                               self.__lots - (self.__position_a_buy + self.__position_b_buy))  # 剩余可开数量
            if order_volume <= 0 or not isinstance(order_volume, int):
                if Utils.Strategy_print:
                    print('Strategy.order_algorithm_one() 发单手数错误值', order_volume)
            self.__order_ref_a = self.add_order_ref()  # 报单引用
            self.__order_ref_last = self.__order_ref_a
            # A合约报单参数，全部确定
            self.__a_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          'OrderRef': self.__order_ref_a,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[0].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_a_tick['AskPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_b_tick['BidPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            self.trade_task(self.__a_order_insert_args)  # 执行下单任务
            self.__trade_tasking = True  # 交易任务执行中

    # 下单算法2：A合约以最新成交价发单，B合约以对手价发单
    def order_algorithm_two(self):
        if Utils.Strategy_print:
            # print("Strategy.order_algorithm_two()")
            pass

    # 下单算法3：A合约以挂单价发单，B合约以对手价发单
    def order_algorithm_three(self):
        if Utils.Strategy_print:
            # print("Strategy.order_algorithm_three()")
            pass

    def trade_task(self, dict_args):
        """"交易任务执行"""
        # 报单
        if dict_args['flag'] == 'OrderInsert':
            """交易任务开始入口"""
            if Utils.Strategy_print:
                print('Strategy.trade_task() A合约报单，OrderRef=', dict_args['OrderRef'], '报单参数：', dict_args)
            self.__user.get_trade().OrderInsert(dict_args)  # A合约报单
        # 报单录入请求响应
        elif dict_args['flag'] == 'OnRspOrderInsert':
            if Utils.Strategy_print:
                print("Strategy.trade_task() 报单录入请求响应")
            pass
        # 报单操作请求响应
        elif dict_args['flag'] == 'OnRspOrderAction':
            if Utils.Strategy_print:
                print("Strategy.trade_task() 报单操作请求响应")
            pass
        # 报单回报
        elif dict_args['flag'] == 'OnRtnOrder':
            # A成交回报，B发送等量的报单(OrderInsert)
            if dict_args['Order']['InstrumentID'] == self.__list_instrument_id[0] \
                    and dict_args['Order']['OrderStatus'] in ['0', '1']:  # OrderStatus全部成交或部分成交
                # 无挂单，当前报单回报中的VolumeTrade就是本次成交量
                if len(self.__list_order_pending) == 0:
                    self.__b_order_insert_args['VolumeTotalOriginal'] = dict_args['Order']['VolumeTraded']
                # 有挂单，从挂单列表中查找是否有相同的OrderRef
                else:
                    b_fined = False  # 是否找到的初始值
                    for i in self.__list_order_pending:
                        # 从挂单列表中找到相同的OrderRef记录，当前回报的VolumeTraded减去上一条回报中VolumeTrade等于本次成交量
                        if i['OrderRef'] == dict_args['Order']['OrderRef']:
                            self.__b_order_insert_args['VolumeTotalOriginal'] = \
                                dict_args['Order']['VolumeTraded'] - i['VolumeTraded']  # B发单量等于本次回报A的成交量
                            b_fined = True  # 找到了，赋值为真
                            break
                    # 未在挂单列表中找到相同的OrderRef记录，当前报单回报中的VolumeTraded就是本次成交量
                    if not b_fined:
                        self.__b_order_insert_args['VolumeTotalOriginal'] = dict_args['Order']['VolumeTraded']

                self.__order_ref_b = self.add_order_ref()  # B报单引用
                self.__order_ref_last = self.__order_ref_b  # 实际最后使用的报单引用
                self.__b_order_insert_args['OrderRef'] = self.__order_ref_b
                if Utils.Strategy_print:
                    print('Strategy.trade_task() B合约报单，OrderRef=', self.__b_order_insert_args['OrderRef'], '报单参数：', self.__b_order_insert_args)
                self.__user.get_trade().OrderInsert(self.__b_order_insert_args)  # B合约报单
            # B成交回报
            elif dict_args['Order']['InstrumentID'] == self.__list_instrument_id[1] \
                    and dict_args['Order']['OrderStatus'] in ['0', '1']:  # OrderStatus全部成交或部分成交
                pass
            # B撤单回报，启动B重新发单一定成交策略
            elif dict_args['Order']['InstrumentID'] == self.__list_instrument_id[1] \
                    and dict_args['Order']['OrderStatus'] == '5' \
                    and len(dict_args['Order']['OrderSysID']) == 12:
                if Utils.Strategy_print:
                    print("Strategy.trade_task() 策略编号：", self.__user_id+self.__strategy_id, "收到B撤单回报，启动B重新发单一定成交策略")
                self.__order_ref_b = self.add_order_ref()  # B报单引用
                self.__order_ref_last = self.__order_ref_b  # 实际最后使用的报单引用
                if dict_args['Order']['Direction'] == '0':
                    LimitPrice = self.__instrument_b_tick['AskPrice1']  # B报单价格，找市场最新对手价
                elif dict_args['Order']['Direction'] == '1':
                    LimitPrice = self.__instrument_b_tick['BidPrice1']
                self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                              'OrderRef': self.__order_ref_b,  # 报单引用
                                              'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                              'LimitPrice': LimitPrice,  # 限价
                                              'VolumeTotalOriginal': dict_args['Order']['VolumeTotal'],  # 撤单回报中的剩余未成交数量
                                              'Direction': dict_args['Order']['Direction'].encode(),  # 买卖，0买,1卖
                                              'CombOffsetFlag': dict_args['Order']['CombOffsetFlag'].encode(),  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                              'CombHedgeFlag': dict_args['Order']['CombHedgeFlag'].encode(),  # 组合投机套保标志:1投机、2套利、3保值
                                              }

                if Utils.Strategy_print:
                    print('Strategy.trade_task() B合约报单，OrderRef=', self.__b_order_insert_args['OrderRef'], '报单参数：', self.__b_order_insert_args)
                self.__user.get_trade().OrderInsert(self.__b_order_insert_args)  # B合约报单
        # 报单录入错误回报
        elif dict_args['flag'] == 'OnErrRtnOrderInsert':
            if Utils.Strategy_print:
                print("Strategy.trade_task() 报单录入错误回报")
            pass
        # 报单操作错误回报
        elif dict_args['flag'] == 'OnErrRtnOrderAction':
            if Utils.Strategy_print:
                print("Strategy.trade_task() 报单操作错误回报")
            pass
        # 行情回调，并且交易任务进行中
        elif dict_args['flag'] == 'tick' and self.__trade_tasking:
            """当交易任务进行中时，判断是否需要撤单"""
            # print("Strategy.trade_task() tick驱动判断是否需要撤单")
            # 遍历挂单列表
            for i in self.__list_order_pending:
                # A有挂单，判断是否需要撤单
                if i['InstrumentID'] == self.__list_instrument_id[0]:
                    # 通过A最新tick判断A合约是否需要撤单
                    if dict_args['tick']['InstrumentID'] == self.__list_instrument_id[0]:
                        # A挂单的买卖方向为买
                        if i['Direction'] == '0':
                            # 挂单价格与盘口买一价比较，如果与盘口价格差距n个最小跳以上，撤单
                            # print("Strategy.trade_task()self.__a_wait_price_tick * self.__a_price_tick", self.__a_wait_price_tick, self.__a_price_tick,type(self.__a_wait_price_tick), type(self.__a_price_tick))
                            if dict_args['tick']['BidPrice1'] > (i['LimitPrice'] + self.__a_wait_price_tick*self.__a_price_tick):
                                if Utils.Strategy_print:
                                    print("Strategy.trade_task() 通过A最新tick判断A合约买挂单符合撤单条件")
                                # A合约撤单
                                order_action_arguments = {'OrderRef': i['OrderRef'].encode(),
                                                          'ExchangeID': i['ExchangeID'].encode(),
                                                          'OrderSysID': i['OrderSysID'].encode()}
                                if Utils.Strategy_print:
                                    print('Strategy.trade_task() A合约撤单，OrderRef=', i['OrderRef'], '撤单参数：', order_action_arguments)
                                self.__user.get_trade().OrderAction(order_action_arguments)
                        # A挂单的买卖方向为卖
                        elif i['Direction'] == '1':
                            # 挂单价格与盘口卖一价比较，如果与盘口价格差距n个最小跳以上，撤单
                            # print("Strategy.trade_task()self.__a_wait_price_tick * self.__a_price_tick", self.__a_wait_price_tick, self.__a_price_tick,type(self.__a_wait_price_tick), type(self.__a_price_tick))
                            if dict_args['tick']['AskPrice1'] <= (i['LimitPrice'] - self.__a_wait_price_tick * self.__a_price_tick):
                                if Utils.Strategy_print:
                                    print("Strategy.trade_task() 通过A最新tick判断A合约卖挂单符合撤单条件")
                                # A合约撤单
                                order_action_arguments = {'OrderRef': i['OrderRef'].encode(),
                                                          'ExchangeID': i['ExchangeID'].encode(),
                                                          'OrderSysID': i['OrderSysID'].encode()}
                                if Utils.Strategy_print:
                                    print('Strategy.trade_task()A合约撤单，OrderRef=', i['OrderRef'], '撤单参数：', order_action_arguments)
                                self.__user.get_trade().OrderAction(order_action_arguments)
                    # 通过B最新tick判断A合约是否需要撤单
                    elif dict_args['tick']['InstrumentID'] == self.__list_instrument_id[1]:
                        # A挂单的买卖方向为买
                        if i['Direction'] == '0':
                            # B最新tick的对手价如果与开仓信号触发时B的tick对手价发生不利变化则A撤单
                            if dict_args['tick']['BidPrice1'] < self.__instrument_b_tick_after_tasking['BidPrice1']:
                                if Utils.Strategy_print:
                                    print("Strategy.trade_task() 通过B最新tick判断A合约买挂单符合撤单条件")
                                # A合约撤单
                                order_action_arguments = {'OrderRef': i['OrderRef'].encode(),
                                                          'ExchangeID': i['ExchangeID'].encode(),
                                                          'OrderSysID': i['OrderSysID'].encode()}
                                if Utils.Strategy_print:
                                    print('Strategy.trade_task() A合约撤单，OrderRef=', i['OrderRef'], '撤单参数：', order_action_arguments)
                                self.__user.get_trade().OrderAction(order_action_arguments)
                        # A挂单的买卖方向为卖
                        elif i['Direction'] == '1':
                            # B最新tick的对手价如果与开仓信号触发时B的tick对手价发生不利变化则A撤单
                            if dict_args['tick']['AskPrice1'] > self.__instrument_b_tick_after_tasking['AskPrice1']:
                                if Utils.Strategy_print:
                                    print("Strategy.trade_task()通过B最新tick判断A合约卖挂单符合撤单条件")
                                # A合约撤单
                                order_action_arguments = {'OrderRef': i['OrderRef'].encode(),
                                                          'ExchangeID': i['ExchangeID'].encode(),
                                                          'OrderSysID': i['OrderSysID'].encode()}
                                if Utils.Strategy_print:
                                    print('Strategy.trade_task() A合约撤单，OrderRef=', i['OrderRef'], '撤单参数：', order_action_arguments)
                                self.__user.get_trade().OrderAction(order_action_arguments)
                # B有挂单，判断是否需要撤单，并启动B合约一定成交策略
                if i['InstrumentID'] == self.__list_instrument_id[1]:
                    # 通过B最新tick判断B合约是否需要撤单
                    if dict_args['tick']['InstrumentID'] == self.__list_instrument_id[1]:
                        # B挂单的买卖方向为买
                        if i['Direction'] == '0':
                            # 挂单价格与盘口买一价比较，如果与盘口价格差距n个最小跳以上，撤单
                            if Utils.Strategy_print:
                                print("Strategy.trade_task() self.__b_wait_price_tick * self.__b_price_tick", self.__b_wait_price_tick, self.__b_price_tick, type(self.__b_wait_price_tick), type(self.__b_price_tick))
                            if dict_args['tick']['BidPrice1'] >= (i['LimitPrice'] + self.__b_wait_price_tick * self.__b_price_tick):
                                if Utils.Strategy_print:
                                    print("Strategy.trade_task() 通过B最新tick判断B合约买挂单符合撤单条件")
                                # B合约撤单
                                order_action_arguments = {'OrderRef': i['OrderRef'].encode(),
                                                          'ExchangeID': i['ExchangeID'].encode(),
                                                          'OrderSysID': i['OrderSysID'].encode()}
                                if Utils.Strategy_print:
                                    print('Strategy.trade_task() B合约撤单，OrderRef=', i['OrderRef'], '撤单参数：', order_action_arguments)
                                self.__user.get_trade().OrderAction(order_action_arguments)
                        # B挂单的买卖方向为卖
                        elif i['Direction'] == '1':
                            # 挂单价格与盘口卖一价比较，如果与盘口价格差距n个最小跳以上，撤单
                            if Utils.Strategy_print:
                                print("Strategy.trade_task() self.__b_wait_price_tick * self.__b_price_tick", self.__b_wait_price_tick, self.__b_price_tick, type(self.__b_wait_price_tick), type(self.__b_price_tick))
                            if dict_args['tick']['AskPrice1'] <= (i['LimitPrice'] - self.__b_wait_price_tick * self.__b_price_tick):
                                if Utils.Strategy_print:
                                    print("Strategy.trade_task() 通过B最新tick判断B合约卖挂单符合撤单条件")
                                # B合约撤单
                                order_action_arguments = {'OrderRef': i['OrderRef'].encode(),
                                                          'ExchangeID': i['ExchangeID'].encode(),
                                                          'OrderSysID': i['OrderSysID'].encode()}
                                if Utils.Strategy_print:
                                    print('Strategy.trade_task() B合约撤单，OrderRef=', i['OrderRef'], '撤单参数：', order_action_arguments)
                                self.__user.get_trade().OrderAction(order_action_arguments)
            # 若无挂单、无撇退，则交易任务已完成
            # if True:
            #     self.__trade_tasking = False

    '''
    typedef char TThostFtdcOrderStatusType
    THOST_FTDC_OST_AllTraded = b'0'  # 全部成交
    THOST_FTDC_OST_PartTradedQueueing = b'1'  # 部分成交还在队列中
    THOST_FTDC_OST_PartTradedNotQueueing = b'2'  # 部分成交不在队列中
    THOST_FTDC_OST_NoTradeQueueing = b'3'  # 未成交还在队列中
    THOST_FTDC_OST_NoTradeNotQueueing = b'4'  # 未成交不在队列中
    THOST_FTDC_OST_Canceled = b'5'  # 撤单
    THOST_FTDC_OST_Unknown = b'a'  # 未知
    THOST_FTDC_OST_NotTouched = b'b'  # 尚未触发
    THOST_FTDC_OST_Touched = b'c'  # 已触发
    '''
    # 更新挂单列表
    def update_list_order_pending(self, dict_args):
        if Utils.Strategy_print:
            print("Strategy.update_list_order_pending() 更新前self.__list_order_pending=", self.__list_order_pending)
        # 交易所返回的报单回报，处理以上九种状态
        if len(dict_args['Order']['OrderSysID']) == 12:
            # 挂单列表为空时直接添加挂单到list中
            if len(self.__list_order_pending) == 0:
                self.__list_order_pending.append(dict_args['Order'])
                return
            # 挂单列表不为空时
            for i in range(len(self.__list_order_pending)):  # 遍历挂单列表
                # 找到回报与挂单列表中OrderRef相同的记录
                if self.__list_order_pending[i]['OrderRef'] == dict_args['Order']['OrderRef']:
                    if dict_args['Order']['OrderStatus'] == '0':  # 全部成交
                        self.__list_order_pending.remove(self.__list_order_pending[i])  # 将全部成交单从挂单列表删除
                    elif dict_args['Order']['OrderStatus'] == '1':  # 部分成交还在队列中
                        # i = dict_args['Order']  # 更新挂单列表
                        self.__list_order_pending[i] = dict_args['Order']  # 更新挂单列表
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：部分成交还在队列中")
                    elif dict_args['Order']['OrderStatus'] == '2':  # 部分成交不在队列中
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：部分成交不在队列中")
                    elif dict_args['Order']['OrderStatus'] == '3':  # 未成交还在队列中
                        # i = dict_args['Order']  # 更新挂单列表
                        self.__list_order_pending[i] = dict_args['Order']  # 更新挂单列表
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：未成交还在队列中")
                    elif dict_args['Order']['OrderStatus'] == '4':  # 未成交不在队列中
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：未成交不在队列中")
                    elif dict_args['Order']['OrderStatus'] == '5':  # 撤单
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：撤单，合约：", dict_args['Order']['InstrumentID'])
                        self.__list_order_pending.remove(self.__list_order_pending[i])  # 将全部成交单从挂单列表删除
                    elif dict_args['Order']['OrderStatus'] == 'a':  # 未知
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：未知")
                    elif dict_args['Order']['OrderStatus'] == 'b':  # 尚未触发
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：尚未触发")
                    elif dict_args['Order']['OrderStatus'] == 'c':  # 已触发
                        if Utils.Strategy_print:
                            print("Strategy.update_list_order_pending() 报单状态：已触发")
                    if Utils.Strategy_print:
                        print("Strategy.update_list_order_pending() 更新后self.__list_order_pending=", self.__list_order_pending)
                    return
            # 挂单列表中找不到对应的OrderRef记录时，新添加挂单到self.__list_order_pending
            if dict_args['Order']['OrderStatus'] in ['1', '3']:
                self.__list_order_pending.append(dict_args['Order'])
                if Utils.Strategy_print:
                    print("Strategy.update_list_order_pending() 报单状态：部分成交还在队列中，未成交还在队列中")
        if Utils.Strategy_print:
            print("Strategy.update_list_order_pending() 更新后self.__list_order_pending=", self.__list_order_pending)

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

    # 更新任务状态
    def update_task_status(self):
        # if Utils.Strategy_print:
        #     print("Strategy.update_task_status() 更新前self.__trade_tasking=", self.__trade_tasking)
        if self.__position_a_buy_today == self.__position_b_sell_today \
                and self.__position_a_buy_yesterday == self.__position_b_sell_yesterday \
                and self.__position_a_sell_today == self.__position_b_buy_today \
                and self.__position_a_sell_yesterday == self.__position_b_buy_yesterday \
                and len(self.__list_order_pending) == 0:
            self.__trade_tasking = False
        else:
            self.__trade_tasking = True
    """
    # 更新持仓量变量，共12个持仓变量
    def update_position(self, Trade):
        # A成交
        if Trade['InstrumentID'] == self.__list_instrument_id[0]:
            if Trade['OffsetFlag'] == '0':  # A开仓成交回报
                if Trade['Direction'] == '0':  # A买开仓成交回报
                    self.__position_a_buy_today += Trade['Volume']  # 更新持仓
                elif Trade['Direction'] == '1':  # A卖开仓成交回报
                    self.__position_a_sell_today += Trade['Volume']  # 更新持仓
            elif Trade['OffsetFlag'] == '3':  # A平今成交回报
                if Trade['Direction'] == '0':  # A买平今成交回报
                    self.__position_a_sell_today -= Trade['Volume']  # 更新持仓
                elif Trade['Direction'] == '1':  # A卖平今成交回报
                    self.__position_a_buy_today -= Trade['Volume']  # 更新持仓
            elif Trade['OffsetFlag'] == '4':  # A平昨成交回报
                if Trade['Direction'] == '0':  # A买平昨成交回报
                    self.__position_a_sell_yesterday -= Trade['Volume']  # 更新持仓
                elif Trade['Direction'] == '1':  # A卖平昨成交回报
                    self.__position_a_buy_yesterday -= Trade['Volume']  # 更新持仓
            self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
            self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        # B成交
        elif Trade['InstrumentID'] == self.__list_instrument_id[1]:
            if Trade['OffsetFlag'] == '0':  # B开仓成交回报
                if Trade['Direction'] == '0':  # B买开仓成交回报
                    self.__position_b_buy_today += Trade['Volume']  # 更新持仓
                elif Trade['Direction'] == '1':  # B卖开仓成交回报
                    self.__position_b_sell_today += Trade['Volume']  # 更新持仓
            elif Trade['OffsetFlag'] == '3':  # B平今成交回报
                if Trade['Direction'] == '0':  # B买平今成交回报
                    self.__position_b_sell_today -= Trade['Volume']  # 更新持仓
                elif Trade['Direction'] == '1':  # B卖平今成交回报
                    self.__position_b_buy_today -= Trade['Volume']  # 更新持仓
            elif Trade['OffsetFlag'] == '4':  # B平昨成交回报
                if Trade['Direction'] == '0':  # B买平昨成交回报
                    self.__position_b_sell_yesterday -= Trade['Volume']  # 更新持仓
                elif Trade['Direction'] == '1':  # B卖平昨成交回报
                    self.__position_b_buy_yesterday -= Trade['Volume']  # 更新持仓
            self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
            self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
        if Utils.Strategy_print:
            print("Strategy.update_position() 更新持仓量:")
            print("     A合约", self.__list_instrument_id[0], "今买、昨买、总买", self.__position_a_buy_today, self.__position_a_buy_yesterday,
                  self.__position_a_buy, "今卖、昨卖、总卖", self.__position_a_sell_today, self.__position_a_sell_yesterday,
                  self.__position_a_sell)
            print("     B合约", self.__list_instrument_id[1], "今买、昨买、总买", self.__position_b_buy_today, self.__position_b_buy_yesterday,
                  self.__position_b_buy, "今卖、昨卖、总卖", self.__position_b_sell_today, self.__position_b_sell_yesterday,
                  self.__position_b_sell)
    """

    # 更新持仓量变量，共12个持仓变量
    def update_position(self, Order):
        # A成交
        if Order['InstrumentID'] == self.__list_instrument_id[0]:
            if Order['OffsetFlag'] == '0':  # A开仓成交回报
                if Order['Direction'] == '0':  # A买开仓成交回报
                    self.__position_a_buy_today += Order['Volume']  # 更新持仓
                elif Order['Direction'] == '1':  # A卖开仓成交回报
                    self.__position_a_sell_today += Order['Volume']  # 更新持仓
            elif Order['OffsetFlag'] == '3':  # A平今成交回报
                if Order['Direction'] == '0':  # A买平今成交回报
                    self.__position_a_sell_today -= Order['Volume']  # 更新持仓
                elif Order['Direction'] == '1':  # A卖平今成交回报
                    self.__position_a_buy_today -= Order['Volume']  # 更新持仓
            elif Order['OffsetFlag'] == '4':  # A平昨成交回报
                if Order['Direction'] == '0':  # A买平昨成交回报
                    self.__position_a_sell_yesterday -= Order['Volume']  # 更新持仓
                elif Order['Direction'] == '1':  # A卖平昨成交回报
                    self.__position_a_buy_yesterday -= Order['Volume']  # 更新持仓
            self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
            self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        # B成交
        elif Order['InstrumentID'] == self.__list_instrument_id[1]:
            if Order['OffsetFlag'] == '0':  # B开仓成交回报
                if Order['Direction'] == '0':  # B买开仓成交回报
                    self.__position_b_buy_today += Order['Volume']  # 更新持仓
                elif Order['Direction'] == '1':  # B卖开仓成交回报
                    self.__position_b_sell_today += Order['Volume']  # 更新持仓
            elif Order['OffsetFlag'] == '3':  # B平今成交回报
                if Order['Direction'] == '0':  # B买平今成交回报
                    self.__position_b_sell_today -= Order['Volume']  # 更新持仓
                elif Order['Direction'] == '1':  # B卖平今成交回报
                    self.__position_b_buy_today -= Order['Volume']  # 更新持仓
            elif Order['OffsetFlag'] == '4':  # B平昨成交回报
                if Order['Direction'] == '0':  # B买平昨成交回报
                    self.__position_b_sell_yesterday -= Order['Volume']  # 更新持仓
                elif Order['Direction'] == '1':  # B卖平昨成交回报
                    self.__position_b_buy_yesterday -= Order['Volume']  # 更新持仓
            self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
            self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
        if Utils.Strategy_print:
            print("Strategy.update_position() 更新持仓量:")
            print("     A合约", self.__list_instrument_id[0], "今买、昨买、总买", self.__position_a_buy_today,
                  self.__position_a_buy_yesterday,
                  self.__position_a_buy, "今卖、昨卖、总卖", self.__position_a_sell_today, self.__position_a_sell_yesterday,
                  self.__position_a_sell)
            print("     B合约", self.__list_instrument_id[1], "今买、昨买、总买", self.__position_b_buy_today,
                  self.__position_b_buy_yesterday,
                  self.__position_b_buy, "今卖、昨卖、总卖", self.__position_b_sell_today, self.__position_b_sell_yesterday,
                  self.__position_b_sell)

    """
    # 更新持仓明细列表
    def update_list_position_detail(self, input_trade):
        trade = copy.deepcopy(input_trade)  # 形参深度拷贝到方法局部变量，目的是修改局部变量值不会影响到形参
        # 开仓单，添加到list，添加到list尾部
        if trade['OffsetFlag'] == '0':
            self.__list_position_detail.append(trade)
        # 平仓单，先开先平的原则从list里删除
        elif trade['OffsetFlag'] == '1':
            # 遍历self.__list_position_detail
            for i in range(len(self.__list_position_detail)):
                # trade中"OffsetFlag"为平今
                if trade['OffsetFlag'] == '3':
                    if self.__list_position_detail[i]['TradingDay'] == self.__TradingDay\
                            and trade['InstrumentID'] == self.__list_position_detail[i]['InstrumentID'] \
                            and trade['HedgeFlag'] == self.__list_position_detail[i]['HedgeFlag']\
                            and trade['Direction'] != self.__list_position_detail[i]['Direction']:
                            # list_position_detail中的交易日是当前交易日
                            # trade和list_position_detail中的合约代码相同
                            # trade和list_position_detail中的投保标志相同
                            # trade和list_position_detail中的买卖不同
                        # trade中的volume等于持仓明细列表中的volume
                        if trade['Volume'] == self.__list_position_detail[i]['Volume']:
                            del self.__list_position_detail[i]
                        # trade中的volume小于持仓明细列表中的volume
                        elif trade['Volume'] < self.__list_position_detail[i]['Volume']:
                            self.__list_position_detail[i]['Volume'] -= trade['Volume']
                        # trade中的volume大于持仓明细列表中的volume
                        elif trade['Volume'] > self.__list_position_detail[i]['Volume']:
                            trade['Volume'] -= self.__list_position_detail[i]['Volume']
                            del self.__list_position_detail[i]
                # trade中"OffsetFlag"为平昨
                elif trade['OffsetFlag'] == '4':
                    if self.__list_position_detail[i]['TradingDay'] != self.__TradingDay \
                            and trade['InstrumentID'] == self.__list_position_detail[i]['InstrumentID'] \
                            and trade['HedgeFlag'] == self.__list_position_detail[i]['HedgeFlag'] \
                            and trade['Direction'] != self.__list_position_detail[i]['Direction']:
                        # list_position_detail中的交易日不是当前交易日
                        # trade和list_position_detail中的合约代码相同
                        # trade和list_position_detail中的投保标志相同
                        # trade和list_position_detail中的买卖不同
                        # trade中的volume等于持仓明细列表中的volume
                        if trade['Volume'] == self.__list_position_detail[i]['Volume']:
                            del self.__list_position_detail[i]
                        # trade中的volume小于持仓明细列表中的volume
                        elif trade['Volume'] < self.__list_position_detail[i]['Volume']:
                            self.__list_position_detail[i]['Volume'] -= trade['Volume']
                        # trade中的volume大于持仓明细列表中的volume
                        elif trade['Volume'] > self.__list_position_detail[i]['Volume']:
                            trade['Volume'] -= self.__list_position_detail[i]['Volume']
                            del self.__list_position_detail[i]
    """

    # 更新持仓明细列表
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
                # 持仓明细中order与order_new比较：交易日相同、合约代码相同、投保标志相同、开平相反
                if i['TradingDay'] == order_new['TradingDay'] \
                        and i['InstrumentID'] == order_new['InstrumentID'] \
                        and i['CombHedgeFlag'] == order_new['CombHedgeFlag'] \
                        and i['Direction'] != order_new['Direction']:
                    # order_new的VolumeTradedBatch等于持仓列表首个满足条件的order的VolumeTradedBatch
                    if order_new['VolumeTradedBatch'] == i['VolumeTradedBatch']:
                        self.__list_position_detail.remove(i)
                    # order_new的VolumeTradedBatch小于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order_new['VolumeTradedBatch'] < i['VolumeTradedBatch']:
                        i['VolumeTradedBatch'] -= order_new['VolumeTradedBatch']
                    # order_new的VolumeTradedBatch大于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order_new['VolumeTradedBatch'] > i['VolumeTradedBatch']:
                        order_new['VolumeTradedBatch'] -= i['VolumeTradedBatch']
                        self.__list_position_detail.remove(i)  # 待验证for循环代码，待续，2017年1月12日22:56:31
        # order_new中"CombOffsetFlag"值="4"为平昨
        elif order_new['CombOffsetFlag'] == '4':
            pass

    # 统计指标
    def statistics(self):
        # 以一天的盘面为周期的统计指标
        # self.__today_profit = dict_args['today_profit']  # 平仓盈利
        # self.__today_commission = dict_args['today_commission']  # 手续费
        # self.__today_trade_volume = dict_args['commission']  # 成交量
        # self.__today_sum_slippage = dict_args['today_sum_slippage']  # 总滑价
        # self.__today_average_slippage = dict_args['today_average_slippage']  # 平均滑价
        #
        # self.__position_a_buy_today = dict_args['position_a_buy_today']  # A合约买持仓今仓
        # self.__position_a_buy_yesterday = dict_args['position_a_buy_yesterday']  # A合约买持仓昨仓
        # self.__position_a_buy = dict_args['position_a_buy']  # A合约买持仓总仓位
        # self.__position_a_sell_today = dict_args['position_a_sell_today']  # A合约卖持仓今仓
        # self.__position_a_sell_yesterday = dict_args['position_a_sell_yesterday']  # A合约卖持仓昨仓
        # self.__position_a_sell = dict_args['position_a_sell']  # A合约卖持仓总仓位
        # self.__position_b_buy_today = dict_args['position_b_buy_today']  # B合约买持仓今仓
        # self.__position_b_buy_yesterday = dict_args['position_b_buy_yesterday']  # B合约买持仓昨仓
        # self.__position_b_buy = dict_args['position_b_buy']  # B合约买持仓总仓位
        # self.__position_b_sell_today = dict_args['position_b_sell_today']  # B合约卖持仓今仓
        # self.__position_b_sell_yesterday = dict_args['position_b_sell_yesterday']  # B合约卖持仓昨仓
        # self.__position_b_sell = dict_args['position_b_sell']  # B合约卖持仓总仓位
        pass

if __name__ == '__main__':
    # df1 = pd.read_csv('D:/CTP_Dev/CTP数据样本/API查询/063802_第1次（启动时流文件为空）/063802_QryTrade.csv', header=0)
    # s = df1['OrderRef'].astype(str).str[-1:].astype(int)
    # df1['StrategyID'] = s
    # df2 = df1[df1.StrategyID == 11]
    # print(df1)

    # 初始化今仓
    """
    self.__user.get_dfQryTrade() 替换为 get_dfQryTrade
    self.__dfQryTrade 替换为 self_dfQryTrade
    self.__dfQryTrade_Strategy 替换为 self_dfQryTradeStrategy
    """
    get_dfQryTrade = pd.read_csv('D:/CTP_Dev/CTP数据样本/API查询/063802_第1次（启动时流文件为空）/063802_QryTrade.csv', header=0)
    get_dfQryTrade['StrategyID'] = get_dfQryTrade['OrderRef'].astype(str).str[-2:].astype(
        int)  # 截取OrderRef后两位数为StrategyID
    # print("get_dfQryTrade\n", get_dfQryTrade)
