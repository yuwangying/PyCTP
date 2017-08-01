# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


import copy
import json
from PyQt4 import QtGui
import datetime
import Utils
from pandas import DataFrame, Series
import pandas as pd
from PyQt4 import QtCore
import PyCTP
# import queue
# import threading
# from PyCTP_Trade import PyCTP_Trader_API
# from PyCTP_Market import PyCTP_Market_API
# from OrderAlgorithm import OrderAlgorithm
# import time


class Strategy():
    # 定义信号，必须放到__init__之前
    # signal_UI_spread_short = QtCore.pyqtSignal(str)  # 定义信号，设置单账户窗口空头价差值
    # signal_UI_spread_long = QtCore.pyqtSignal(str)
    # signal_UI_spread_short_total = QtCore.pyqtSignal(str)
    # signal_UI_spread_long_total = QtCore.pyqtSignal(str)
    # signal_UI_spread_short_change_color = QtCore.pyqtSignal(str)  # 定义信号，设置单账户窗口空头价差颜色
    # signal_UI_spread_long_change_color = QtCore.pyqtSignal(str)
    # signal_UI_spread_short_total_change_color = QtCore.pyqtSignal(str)
    # signal_UI_spread_long_total_change_color = QtCore.pyqtSignal(str)
    # signal_UI_change_color = QtCore.pyqtSignal(str)  # 定义信号，改变颜色
    # signal_UI_update_strategy = QtCore.pyqtSignal(object)  # 改写，所有策略对象的信号signal_UI_update_strategy分别连接到所有QAccountWidget对象的槽update_strategy
    # signal_update_spread_signal = QtCore.pyqtSignal(dict)  # 改写：将策略对象信号signal_UI_update_spread_signal连接到策略所属的单账户窗口
    # signal_update_spread_total = QtCore.pyqtSignal(dict)  # 改写：将策略对象信号signal_UI_update_spread_total连接到总账户窗口和所属的单账户窗口

    # 定义信号：策略对象修改策略 -> 界面刷新策略（Strategy.signal_update_strategy -> QAccountWidget.slot_update_strategy()）
    # signal_update_strategy = QtCore.pyqtSignal(object)  # 形参为Strategy对象
    # 定义信号：策略对象持仓发生变化 -> 界面刷新持仓显示（Strategy.signal_update_strategy_position -> QAccountWidget.slot_update_strategy_position）
    # signal_update_strategy_position = QtCore.pyqtSignal(object)  # 形参为Strategy对象
    # 定义信号：策略发送信号 -> 修改持仓按钮设置为可用，并修改文本“发送持仓”改为“设置持仓”
    # signal_pushButton_set_position_setEnabled = QtCore.pyqtSignal()
    # 定义信号：转发tick到槽函数 -> self.slot_handle_tick
    # signal_handle_tick = QtCore.pyqtSignal(dict)

    # class Strategy功能:接收行情，接收Json数据，触发交易信号，将交易任务交给OrderAlgorithm
    def __init__(self, dict_args, obj_user):
        print('Strategy.__init__() 创建策略，user_id=', dict_args['user_id'], 'strategy_id=', dict_args['strategy_id'])
        self.__user = obj_user  # user实例
        self.init_variable()  # 初始化变量
        self.__MdApi_TradingDay = self.__user.get_MdApi_TradingDay()  # 获取TdApi的交易日
        self.set_arguments(dict_args)  # 设置策略参数，形参由server端获取到
        # 从API查询期货合约信息中未找到该合约代码，则不创建Strategy对象
        # if self.if_exist_instrument_id(self.__a_instrument_id) == False:
        #     return
        # if self.if_exist_instrument_id(self.__b_instrument_id) == False:
        #     return
        self.get_td_api_arguments()  # 从TdApi获取必要的参数（合约乘数、手续费等）
        self.init_position_detail()  # 初始化策略持仓明细order、持仓明细trade
        # self.update_position_of_position_detail_for_trade()  # 利用trade持仓明细更新策略持仓变量
        self.update_position_of_position_detail_for_order()  # 利用order持仓明细更新策略持仓变量
        # self.init_position()  # 初始化策略持仓
        self.init_statistics()  # 初始化统计指标
        print('Strategy.__init__() 策略准备完成，user_id=', dict_args['user_id'], 'strategy_id=', dict_args['strategy_id'])

        # 临时变量，检查策略接收到的OnRtnOrder\OnRtnTrade记录是否正确
        self.__df_OnRtnOrder = DataFrame()
        self.__df_OnRtnTrade = DataFrame()

    # 设置参数
    def set_arguments(self, dict_args):
        self.__dict_arguments = copy.deepcopy(dict_args)  # 将形参转存为私有变量
        # print(">>> Strategy.set_arguments() dict_args =", dict_args)
        self.__trader_id = dict_args['trader_id']
        self.__user_id = dict_args['user_id']
        self.__strategy_id = dict_args['strategy_id']
        print("Strategy.set_arguments() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "dict_args =", dict_args)

        self.__trade_model = dict_args['trade_model']  # 交易模型
        self.__order_algorithm = dict_args['order_algorithm']  # 下单算法选择标志位
        self.__instrument_a_scale = dict_args['instrument_a_scale']  # A合约乘数
        self.__instrument_b_scale = dict_args['instrument_b_scale']  # B合约乘数
        self.__lots = dict_args['lots']  # 总手
        self.__lots_batch = dict_args['lots_batch']  # 每批下单手数
        self.__stop_loss = dict_args['stop_loss']  # 止损，单位为最小跳数
        self.__strategy_on_off = dict_args['strategy_on_off']  # 策略开关，0关、1开
        self.__spread_shift = dict_args['spread_shift']  # 价差让价（超价触发）
        # self.__a_instrument_id = dict_args['list_instrument_id'][0]  # A合约代码
        # self.__b_instrument_id = dict_args['list_instrument_id'][1]  # B合约代码
        self.__a_instrument_id = dict_args['a_instrument_id']  # B合约代码
        self.__b_instrument_id = dict_args['b_instrument_id']  # B合约代码
        self.__a_limit_price_shift = dict_args['a_limit_price_shift']  # A合约报价偏移
        self.__b_limit_price_shift = dict_args['b_limit_price_shift']  # B合约报价偏移
        self.__a_wait_price_tick = dict_args['a_wait_price_tick']  # A合约挂单等待最小跳数
        self.__b_wait_price_tick = dict_args['b_wait_price_tick']  # B合约挂单等待最小跳数
        self.__a_order_action_limit = dict_args['a_order_action_limit']  # A合约撤单次数限制
        self.__b_order_action_limit = dict_args['b_order_action_limit']  # B合约撤单次数限制
        self.__buy_open = dict_args['buy_open']  # 触发买开（开多单）
        self.__sell_close = dict_args['sell_close']  # 触发卖平（平多单）
        self.__sell_open = dict_args['sell_open']  # 触发卖开（开空单）
        self.__buy_close = dict_args['buy_close']  # 触发买平（平空单）
        self.__sell_open_on_off = dict_args['sell_open_on_off']    # 价差卖开，开关，初始值为1，状态开
        self.__buy_close_on_off = dict_args['buy_close_on_off']    # 价差买平，开关，初始值为1，状态开
        self.__sell_close_on_off = dict_args['sell_close_on_off']  # 价差卖平，开关，初始值为1，状态开
        self.__buy_open_on_off = dict_args['buy_open_on_off']     # 价差买开，开关，初始值为1，状态开
        self.__update_position_detail_record_time = dict_args['update_position_detail_record_time']  # 修改策略持仓时间，空字符串：本交易日没有修改持仓
        # print("Strategy.set_arguments() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__update_position_detail_record_time =", self.__update_position_detail_record_time)

    # 获取参数
    def get_arguments(self):
        self.__dict_arguments = {
            'trader_id': self.__trader_id,
            'user_id': self.__user_id,
            'strategy_id': self.__strategy_id,
            'on_off': self.__strategy_on_off,
            'trade_model': self.__trade_model,
            'order_algorithm': self.__order_algorithm,
            'instrument_a_scale': self.__instrument_a_scale,
            'instrument_b_scale': self.__instrument_b_scale,
            'lots': self.__lots,
            'lots_batch': self.__lots_batch,
            'stop_loss': self.__stop_loss,
            'strategy_on_off': self.__strategy_on_off,
            'spread_shift': self.__spread_shift,
            'a_instrument_id': self.__a_instrument_id,
            'b_instrument_id': self.__b_instrument_id,
            'a_limit_price_shift': self.__a_limit_price_shift,
            'b_limit_price_shift': self.__b_limit_price_shift,
            'a_wait_price_tick': self.__a_wait_price_tick,
            'b_wait_price_tick': self.__b_wait_price_tick,
            'a_order_action_limit': self.__a_order_action_limit,
            'b_order_action_limit': self.__b_order_action_limit,
            'buy_open': self.__buy_open,
            'sell_close': self.__sell_close,
            'sell_open': self.__sell_open,
            'buy_close': self.__buy_close,
            'sell_open_on_off': self.__sell_open_on_off,
            'buy_close_on_off': self.__buy_close_on_off,
            'sell_close_on_off': self.__sell_close_on_off,
            'buy_open_on_off': self.__buy_open_on_off
        }
        return self.__dict_arguments

    # 声明变量
    def init_variable(self):
        # 标志位
        self.__filter_OnRtnOrder = False  # 策略当前交易日有设置过持仓，设置持仓时间过滤
        self.__filter_OnRtnTrade = False  # 策略当前交易日有设置过持仓，设置持仓时间过滤
        self.__a_tick = None  # A合约tick（第一腿）
        self.__b_tick = None  # B合约tick（第二腿）
        self.__Margin_Occupied_CFFEX = 0
        self.__Margin_Occupied_SHFE = 0
        self.__Margin_Occupied_CZCE = 0
        self.__Margin_Occupied_DCE = 0

        # 持仓变量
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
        self.__position = 0  # 总持仓量
        # 策略统计类变量
        self.__a_order_times = 0  # A委托次数
        self.__b_order_times = 0  # B委托次数
        self.__a_order_lots = 0  # A委托手数
        self.__b_order_lots = 0  # B委托手数
        self.__a_traded_lots = 0  # A成交手数
        self.__b_traded_lots = 0  # B成交手数
        self.__total_traded_lots = 0  # A、B成交手数合计
        self.__a_traded_amount = 0  # A成交金额
        self.__b_traded_amount = 0  # B成交金额
        self.__total_traded_amount = 0  # A、B成交金额
        self.__a_commission = 0  # A手续费
        self.__b_commission = 0  # B手续费
        self.__a_commission_order = 0  # A合约申报费，中金所股指期货合约存在申报费
        self.__b_commission_order = 0  # B合约申报费
        self.__total_commission = 0  # 总手续费
        self.__a_trade_rate = 0  # A成交概率(成交手数/报单手数)
        self.__b_trade_rate = 0  # B成交概率(成交手数/报单手数)
        self.__a_profit_close = 0  # A平仓盈亏
        self.__b_profit_close = 0  # B平仓盈亏
        self.__profit_close = 0  # 平仓盈亏
        self.__profit_position = 0  # 持仓盈亏
        self.__profit = 0  # 净盈亏
        self.__a_action_count = 0  # 期货账户内A的撤单次数
        self.__b_action_count = 0  # 期货账户内的B撤单次数
        self.__a_action_count_strategy = 0  # 本策略的A撤单次数
        self.__b_action_count_strategy = 0  # 本策略的B撤单次数
        self.__current_margin = 0  # 占用保证金

        self.__dict_statistics = {
            # 成交统计的类计指标（trade）
            'a_profit_close': self.__a_profit_close,  # A平仓盈亏
            'b_profit_close': self.__b_profit_close,  # B平仓盈亏
            'profit_close': self.__profit_close,  # 平仓盈亏
            'commission': self.__total_commission,  # 手续费
            'profit': self.__profit,  # 净盈亏
            'a_traded_count': self.__a_traded_lots,  # A成交量
            'b_traded_count': self.__b_traded_lots,  # B成交量
            'a_traded_amount': self.__a_traded_amount,  # A成交金额
            'b_traded_amount': self.__b_traded_amount,  # B成交金额
            'total_traded_amount': self.__total_traded_amount,  # A、B成交金额之和
            'a_commission_count': self.__a_commission,  # A手续费
            'b_commission_count': self.__b_commission,  # B手续费
            'profit_position': self.__profit_position,  # 持仓盈亏
            'current_margin': self.__current_margin,  # 当前保证金总额
            # 报单统计的累计指标（order）
            'a_order_lots': self.__a_order_lots,  # A委托手数
            'b_order_lots': self.__b_order_lots,  # B委托手数
            'a_order_count': self.__a_order_times,  # A委托次数
            'b_order_count': self.__b_order_times,  # B委托次数
            'a_action_count': self.__a_action_count,  # A撤单次数
            'b_action_count': self.__b_action_count,  # B撤单次数
            'a_trade_rate': self.__a_trade_rate,  # A成交概率(成交手数/报单手数)
            'b_trade_rate': self.__b_trade_rate  # B成交概率(成交手数/报单手数)
        }

        # 统计申报费的OrderRef管理list
        self.__list_OrderRef_for_count_commission_order = list()

    def get_list_strategy_view(self):
        # ['开关', '期货账号', '策略编号', '交易合约', '总持仓', '买持仓', '卖持仓', '持仓盈亏', '平仓盈亏', '手续费', '净盈亏', '成交量', '成交金额', 'A成交率', 'B成交率', '交易模型', '下单算法']
        checkBox = QtGui.QCheckBox()
        if self.__strategy_on_off == 1:
            checkBox.setText("开")
        elif self.__strategy_on_off == 0:
            checkBox.setText("关")
        self.__list_strategy_view = [checkBox,
                                     self.__user_id,
                                     self.__strategy_id,
                                     (self.__a_instrument_id + ',' + self.__b_instrument_id),
                                     (self.__position_a_buy + self.__position_a_sell),
                                     self.__position_a_buy,
                                     self.__position_a_sell,
                                     self.__profit_position,
                                     self.__profit_close,
                                     self.__total_commission,
                                     self.__profit,
                                     (self.__a_traded_lots + self.__b_traded_lots),
                                     self.__total_traded_amount,
                                     self.__a_trade_rate,
                                     self.__b_trade_rate,
                                     self.__trade_model,
                                     self.__order_algorithm
                                            ]
        return self.__list_strategy_view

    # 装载持仓明细数据order和trade
    def init_position_detail(self):
        print("Strategy.init_position_detail() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "len(self.__update_position_detail_record_time) =", len(self.__update_position_detail_record_time))
        # RESUM模式启动，xml数据可用，装载xml数据
        if self.__user.get_TdApi_start_model() == PyCTP.THOST_TERT_RESUME:
            # 持仓明细order
            self.__list_position_detail_for_order = list()  # 初始化本策略持仓明细order
            for i in self.__user.get_xml_list_position_detail_for_order():
                if i['strategy_id'] == self.__strategy_id:
                    self.__list_position_detail_for_order.append(i)

            # 持仓明细trade
            self.__list_position_detail_for_trade = list()  # 初始化本策略持仓明细trade
            for i in self.__user.get_xml_list_position_detail_for_trade():
                if i['strategy_id'] == self.__strategy_id:
                    self.__list_position_detail_for_trade.append(i)

        # RESTART模式启动，xml数据不可用，装载server数据
        elif self.__user.get_TdApi_start_model() == PyCTP.THOST_TERT_RESTART:  # RESTART模式启动，xml数据不可用
            # 当前交易日没有修改过策略持仓，持仓明细初始值为昨日持仓明细
            if len(self.__update_position_detail_record_time) == 0:
                # 昨日持仓明细order
                self.__list_position_detail_for_order = list()
                for i in self.__user.get_server_list_position_detail_for_order_yesterday():
                    if i['StrategyID'] == self.__strategy_id:
                        self.__list_position_detail_for_order.append(i)
                # 昨日持仓明细trade
                self.__list_position_detail_for_trade = list()
                for i in self.__user.get_server_list_position_detail_for_trade_yesterday():
                    if i['StrategyID'] == self.__strategy_id:
                        self.__list_position_detail_for_trade.append(i)
                len1 = len(self.__list_position_detail_for_order)
                len2 = len(self.__list_position_detail_for_trade)
                print("Strategy.init_position_detail() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "昨持仓明细 为初始化持仓明细，order、trade持仓明细的长度分别为", len1, len2)
            # 当前交易日有修改过策略持仓，持仓明细初始值为修改策略持仓一刻时保存的今日持仓明细
            else:
                # 今日持仓明细order
                self.__list_position_detail_for_order = list()
                for i in self.__user.get_server_list_position_detail_for_order_today():
                    if i['StrategyID'] == self.__strategy_id:
                        self.__list_position_detail_for_order.append(i)
                # 今日持仓明细trade
                self.__list_position_detail_for_trade = list()
                for i in self.__user.get_server_list_position_detail_for_trade_today():
                    if i['StrategyID'] == self.__strategy_id:
                        self.__list_position_detail_for_trade.append(i)
                len1 = len(self.__list_position_detail_for_order)
                len2 = len(self.__list_position_detail_for_trade)
                self.__filter_OnRtnOrder = True  # OnRtnOrder
                self.__filter_OnRtnTrade = True  # OnRtnTrade
                self.__filter_date = self.__update_position_detail_record_time[:8]
                self.__filter_time = self.__update_position_detail_record_time[8:]
                print("Strategy.init_position_detail() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "今持仓明细 为初始化持仓明细，order、trade持仓明细的长度分别为", len1, len2)

            print("Strategy.init_position_detail() user_id =", self.__user_id, "strategy_id =", self.__strategy_id,
                  "self.__list_position_detail_for_order =", self.__list_position_detail_for_order)
            print("Strategy.init_position_detail() user_id =", self.__user_id, "strategy_id =", self.__strategy_id,
                  "self.__list_position_detail_for_trade =", self.__list_position_detail_for_trade)

    # 程序运行中查询策略信息，收到服务端消息之后设置策略实例参数
    def set_arguments_query_strategy_info(self, dict_args):
        print(">>> Strategy.set_arguments_query_strategy_info() user_id=", self.__user_id, "strategy_id=", self.__strategy_id)
        self.__dict_arguments = dict_args  # 将形参转存为私有变量
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
        self.__a_limit_price_shift = dict_args['a_limit_price_shift']  # A合约报价偏移
        self.__b_limit_price_shift = dict_args['b_limit_price_shift']  # B合约报价偏移
        self.__a_wait_price_tick = dict_args['a_wait_price_tick']  # A合约挂单等待最小跳数
        self.__b_wait_price_tick = dict_args['b_wait_price_tick']  # B合约挂单等待最小跳数
        self.__stop_loss = dict_args['stop_loss']  # 止损，单位为最小跳数
        self.__lots = dict_args['lots']  # 总手
        self.__lots_batch = dict_args['lots_batch']  # 每批下单手数
        self.__a_order_action_limit = dict_args['a_order_action_limit']  # A合约撤单次数限制
        self.__a_order_action_limit = dict_args['b_order_action_limit']  # B合约撤单次数限制
        self.__strategy_on_off = dict_args['strategy_on_off']  # 策略开关，0关、1开
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

    # 初始化持仓明细列表，由order维护
    def init_list_position_detail_for_order(self):
        # 获取本策略昨收盘时刻的持仓明细列表，值类型为list，长度可能为0，数据从服务端获取
        # 筛选出昨日持仓明细列表
        list_position_detail_info = self.__ctp_manager.get_SocketManager().get_list_position_detail_info_for_order()
        print("Strategy.init_list_position_detail_for_order() list_position_detail_info =", list_position_detail_info)
        for i in list_position_detail_info:
            if i['userid'] == self.__user_id and i['strategyid'] == self.__strategy_id:
                self.__list_position_detail_for_order.append(i)

        # 更新撤单计数、更新挂单列表、self.__list_QryOrder中增加字段VolumeTradeBatch、更新持仓明细列表
        # print("Strategy.init_list_position_detail_for_order() len(self.__list_QryOrder) =", len(self.__list_QryOrder))
        # if len(self.__list_QryOrder) > 0:  # 本策略的self.__list_QryOrder有记录
        #     for i in self.__list_QryOrder:  # 遍历本策略的self.__list_QryOrder
        #         self.statistics_for_order(i)  # 成交统计
        #         self.update_list_order_process(i)  # 更新挂单列表
        #         i = self.add_VolumeTradedBatch(i)  # 增加本次成交量字段VolumeTradedBatch
        #         self.update_list_position_detail_for_order(i)  # 更新持仓明细列表
        #     return True
        # elif len(self.__list_QryOrder) == 0:  # 本策略的self.__list_QryOrder无记录
        #     return True

    # 初始化持仓明细列表，由trade维护
    def init_list_position_detail_for_trade(self):
        # 获取本策略昨收盘时刻的持仓明细列表，值类型为list，长度可能为0，数据从服务端获取
        # 筛选出昨日持仓明细列表
        for i in self.__ctp_manager.get_SocketManager().get_list_position_detail_info_for_trade():
            if i['userid'] == self.__user_id and i['strategyid'] == self.__strategy_id:
                self.__list_position_detail_for_trade.append(i)

        # 更新持仓明细列表
        # if len(self.__list_QryTrade) > 0:  # 本策略的self.__list_QryOrder有记录
        #     # print(">>> Strategy.init_list_position_detail_for_trade() len(self.__list_QryTrade) =", len(self.__list_QryTrade))
        #     for i in self.__list_QryTrade:  # 遍历本策略的self.__list_QryOrder
        #         # print(">>> ", i)
        #         self.statistics_for_trade(i)  # 成交统计，统计出了平仓盈亏之外的成交统计类数据
        #         self.update_list_position_detail_for_trade(i)  # 更新持仓明细列表
        #     return True
        # elif len(self.__list_QryTrade) == 0:  # 本策略的self.__list_QryOrder无记录
        #     return True

    # 更新持仓明细列表
    def update_list_position_detail_for_order(self, order_input):
        """
        order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        '0'：开仓
        '1'：平仓
        '3'：平今
        '4'：平昨
        """
        # 跳过无成交的order记录
        if order_input['VolumeTradedBatch'] == 0:
            return

        order = copy.deepcopy(order_input)

        # order_new中"CombOffsetFlag"值="0"为开仓，不用考虑全部成交还是部分成交，开仓order直接添加到持仓明细列表里
        if order['CombOffsetFlag'] == '0':
            self.__list_position_detail_for_order.append(order)
        # order_new中"CombOffsetFlag"值="3"为平今
        elif order['CombOffsetFlag'] == '3':
            shift = 0  # 游标修正值
            len_list_position_detail_for_order = len(self.__list_position_detail_for_order)
            # for i in self.__list_position_detail_for_order:  # i为order结构体，类型为dict
            for i in range(len_list_position_detail_for_order):  # i为order结构体，类型为dict
                # 持仓明细中order与order_new比较：交易日相同、合约代码相同、投保标志相同
                if self.__list_position_detail_for_order[i-shift]['TradingDay'] == order['TradingDay'] \
                        and self.__list_position_detail_for_order[i-shift]['InstrumentID'] == order['InstrumentID'] \
                        and self.__list_position_detail_for_order[i-shift]['CombHedgeFlag'] == order['CombHedgeFlag'] \
                        and self.__list_position_detail_for_order[i-shift]['Direction'] != order['Direction']:
                    # order_new的VolumeTradedBatch等于持仓列表首个满足条件的order的VolumeTradedBatch
                    if order['VolumeTradedBatch'] == self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']:
                        self.__list_position_detail_for_order.remove(self.__list_position_detail_for_order[i-shift])
                        break
                    # order_new的VolumeTradedBatch小于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order['VolumeTradedBatch'] < self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']:
                        self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch'] -= order['VolumeTradedBatch']
                        break
                    # order_new的VolumeTradedBatch大于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order['VolumeTradedBatch'] > self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']:
                        order['VolumeTradedBatch'] -= self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']
                        self.__list_position_detail_for_order.remove(self.__list_position_detail_for_order[i-shift])
                        shift += 1  # 游标修正值
        # order_new中"CombOffsetFlag"值="4"为平昨
        elif order['CombOffsetFlag'] == '4':
            shift = 0
            len_list_position_detail_for_order = len(self.__list_position_detail_for_order)
            # for i in self.__list_position_detail_for_order:  # i为order结构体，类型为dict
            for i in range(len_list_position_detail_for_order):  # i为order结构体，类型为dict
                # 持仓明细中order与order_new比较：交易日不相同、合约代码相同、投保标志相同
                if self.__list_position_detail_for_order[i-shift]['TradingDay'] != order['TradingDay'] \
                        and self.__list_position_detail_for_order[i-shift]['InstrumentID'] == order['InstrumentID'] \
                        and self.__list_position_detail_for_order[i-shift]['CombHedgeFlag'] == order['CombHedgeFlag'] \
                        and self.__list_position_detail_for_order[i-shift]['Direction'] != order['Direction']:
                    # order_new的VolumeTradedBatch等于持仓列表首个满足条件的order的VolumeTradedBatch
                    if order['VolumeTradedBatch'] == self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']:
                        self.__list_position_detail_for_order.remove(self.__list_position_detail_for_order[i-shift])
                        break
                    # order_new的VolumeTradedBatch小于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order['VolumeTradedBatch'] < self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']:
                        self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch'] -= order['VolumeTradedBatch']
                        break
                    # order_new的VolumeTradedBatch大于持仓列表首个满足条件的order的VolumeTradedBatch
                    elif order['VolumeTradedBatch'] > self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']:
                        order['VolumeTradedBatch'] -= self.__list_position_detail_for_order[i-shift]['VolumeTradedBatch']
                        self.__list_position_detail_for_order.remove(self.__list_position_detail_for_order[i-shift])
                        shift += 1  # 游标修正值

    def update_list_position_detail_for_trade(self, trade_input):
        # order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        # '0'：开仓
        # '1'：平仓
        # '3'：平今
        # '4'：平昨
        trade = copy.deepcopy(trade_input)  # 形参深度拷贝到方法局部变量，目的是修改局部变量值不会影响到形参
        # self.statistics_for_trade(trade)  # 统计
        # trade_new中"OffsetFlag"值="0"为开仓，不用考虑全部成交还是部分成交，开仓trade直接添加到持仓明细列表里
        if trade['OffsetFlag'] == '0':
            # A合约
            if trade['InstrumentID'] == self.__a_instrument_id:
                trade['CurrMargin'] = trade['Price'] * trade['Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            # B合约
            elif trade['InstrumentID'] == self.__b_instrument_id:
                trade['CurrMargin'] = trade['Price'] * trade['Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            self.__list_position_detail_for_trade.append(trade)  # 添加到持仓明细列表
        # trade_new中"OffsetFlag"值="3"为平今
        elif trade['OffsetFlag'] == '3':
            shift = 0
            len_list_position_detail_for_trade = len(self.__list_position_detail_for_trade)
            for i in range(len_list_position_detail_for_trade):  # i为trade结构体，类型为dict
                # 持仓明细中trade与trade_new比较：交易日相同、合约代码相同、投保标志相同
                if self.__list_position_detail_for_trade[i-shift]['TradingDay'] == trade['TradingDay'] \
                        and self.__list_position_detail_for_trade[i-shift]['InstrumentID'] == trade['InstrumentID'] \
                        and self.__list_position_detail_for_trade[i-shift]['HedgeFlag'] == trade['HedgeFlag'] \
                        and self.__list_position_detail_for_trade[i-shift]['Direction'] != trade['Direction']:
                    # trade_new的Volume等于持仓列表首个满足条件的trade的Volume
                    if trade['Volume'] == self.__list_position_detail_for_trade[i-shift]['Volume']:
                        self.count_profit(trade, self.__list_position_detail_for_trade[i-shift])
                        self.__list_position_detail_for_trade.remove(self.__list_position_detail_for_trade[i-shift])
                        # shift += 1  # 游标修正值
                        break
                    # trade_new的Volume小于持仓列表首个满足条件的trade的Volume
                    elif trade['Volume'] < self.__list_position_detail_for_trade[i-shift]['Volume']:
                        self.count_profit(trade, self.__list_position_detail_for_trade[i-shift])
                        self.__list_position_detail_for_trade[i-shift]['Volume'] -= trade['Volume']
                        break
                    # trade_new的Volume大于持仓列表首个满足条件的trade的Volume
                    elif trade['Volume'] > self.__list_position_detail_for_trade[i-shift]['Volume']:
                        self.count_profit(trade, self.__list_position_detail_for_trade[i-shift])
                        trade['Volume'] -= self.__list_position_detail_for_trade[i-shift]['Volume']
                        self.__list_position_detail_for_trade.remove(self.__list_position_detail_for_trade[i-shift])
                        shift += 1  # 游标修正值
        # trade_new中"OffsetFlag"值="4"为平昨
        elif trade['OffsetFlag'] == '4':
            shift = 0
            # print(">>> Strategy.update_list_position_detail_for_trade() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, " len(self.__list_position_detail_for_trade) =", len(self.__list_position_detail_for_trade))
            len_list_position_detail_for_trade = len(self.__list_position_detail_for_trade)
            for i in range(len_list_position_detail_for_trade):  # i为trade结构体，类型为dict
                # # 持仓明细中trade与trade_new比较：交易日不相同、合约代码相同、投保标志相同
                # try:
                #     print(">>>Strategy.update_list_position_detail_for_trade() TradingDay", self.__list_position_detail_for_trade[i-shift]['TradingDay'], trade['TradingDay'])
                # except:
                #     print(">>>Strategy.update_list_position_detail_for_trade() self.__list_position_detail_for_trade[i-shift] =", self.__list_position_detail_for_trade[i-shift])
                #     print(">>>Strategy.update_list_position_detail_for_trade() trade =", trade)

                if self.__list_position_detail_for_trade[i-shift]['TradingDay'] != trade['TradingDay'] \
                        and self.__list_position_detail_for_trade[i-shift]['InstrumentID'] == trade['InstrumentID'] \
                        and self.__list_position_detail_for_trade[i-shift]['HedgeFlag'] == trade['HedgeFlag'] \
                        and self.__list_position_detail_for_trade[i-shift]['Direction'] != trade['Direction']:
                    # trade_new的Volume等于持仓列表首个满足条件的trade的Volume
                    if trade['Volume'] == self.__list_position_detail_for_trade[i-shift]['Volume']:
                        self.count_profit(trade, self.__list_position_detail_for_trade[i-shift])
                        self.__list_position_detail_for_trade.remove(self.__list_position_detail_for_trade[i-shift])
                        shift += 1  # 游标修正值
                        break
                    # trade_new的Volume小于持仓列表首个满足条件的trade的Volume
                    elif trade['Volume'] < self.__list_position_detail_for_trade[i-shift]['Volume']:
                        self.count_profit(trade, self.__list_position_detail_for_trade[i-shift])
                        self.__list_position_detail_for_trade[i-shift]['Volume'] -= trade['Volume']
                        break
                    # trade_new的Volume大于持仓列表首个满足条件的trade的Volume
                    elif trade['Volume'] > self.__list_position_detail_for_trade[i-shift]['Volume']:
                        self.count_profit(trade, self.__list_position_detail_for_trade[i-shift])
                        trade['Volume'] -= self.__list_position_detail_for_trade[i-shift]['Volume']
                        self.__list_position_detail_for_trade.remove(self.__list_position_detail_for_trade[i-shift])
                        shift += 1  # 游标修正值
        else:
            print("Strategy.update_list_position_detail_for_trade() 既不属于A合约也不属于B合约的Trade")

    def action_for_UI_query(self):
        print("Strategy.action_for_UI_query() User子进程数据 user_id =", self.__user_id, "strategy_id =", self.__strategy_id)
        # print(" self.__current_margin =", self.update_current_margin())
        print("A总卖", self.__position_a_sell, "A昨卖", self.__position_a_sell_yesterday)
        print("B总买", self.__position_b_buy, "B昨卖", self.__position_b_buy_yesterday)
        print("A总买", self.__position_a_buy, "A昨买", self.__position_a_buy_yesterday)
        print("B总卖", self.__position_b_sell, "B昨卖", self.__position_b_sell_yesterday)
        # print("平仓盈亏-手续费=净盈亏", self.__profit_close, self.__total_commission, self.__profit)
        # print(" self.__list_position_detail_for_trade 长度", len(self.__list_position_detail_for_trade))
        # for i in self.__list_position_detail_for_trade:
        #     print(i)
        # print(" self.__list_position_detail_for_order 长度", len(self.__list_position_detail_for_order))
        # for i in self.__list_position_detail_for_order:
        #     print(i)

    # 设置持仓时更新持仓明细列表专用方法，较update_list_position_detail_for_trade()去掉了统计类代码
    def update_list_position_detail_for_trade_set_position(self, trade):
        # print(">>> Strategy.update_list_position_detail_for_trade_set_position() trade =", trade)
        # order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        # '0'：开仓
        # '1'：平仓
        # '3'：平今
        # '4'：平昨
        trade_new = copy.deepcopy(trade)  # 形参深度拷贝到方法局部变量，目的是修改局部变量值不会影响到形参
        # self.statistics_for_trade(trade)  # 统计
        # trade_new中"OffsetFlag"值="0"为开仓，不用考虑全部成交还是部分成交，开仓trade直接添加到持仓明细列表里
        # print(">>> Strategy.update_list_position_detail_for_trade_set_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "虚拟平仓之前 len(self.__list_position_detail_for_trade) =", len(self.__list_position_detail_for_trade))
        if trade_new['OffsetFlag'] == '0':
            # A合约
            if trade_new['InstrumentID'] == self.__a_instrument_id:
                trade_new['CurrMargin'] = trade_new['Price'] * trade_new[
                    'Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            # B合约
            elif trade_new['InstrumentID'] == self.__b_instrument_id:
                trade_new['CurrMargin'] = trade_new['Price'] * trade_new[
                    'Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            self.__list_position_detail_for_trade.append(trade_new)  # 添加到持仓明细列表
        # trade_new中"OffsetFlag"值="3"为平今
        elif trade_new['OffsetFlag'] == '3':
            shift = 0
            # print(">>> Strategy.update_list_position_detail_for_trade_set_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "虚拟平今")
            len_list_position_detail_for_trade = len(self.__list_position_detail_for_trade)
            for i in range(len_list_position_detail_for_trade):  # i为order结构体，类型为dict
                # 持仓明细中trade与trade_new比较：交易日相同、合约代码相同、投保标志相同
                if self.__list_position_detail_for_trade[i - shift]['TradingDay'] == trade_new['TradingDay'] \
                        and self.__list_position_detail_for_trade[i - shift]['InstrumentID'] == trade_new[
                            'InstrumentID'] \
                        and self.__list_position_detail_for_trade[i - shift]['HedgeFlag'] == trade_new[
                            'HedgeFlag'] \
                        and self.__list_position_detail_for_trade[i - shift]['Direction'] != trade_new[
                            'Direction']:
                    # print(">>> Strategy.update_list_position_detail_for_trade_set_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "虚拟平今执行")
                    # trade_new的Volume等于持仓列表首个满足条件的trade的Volume
                    if trade_new['Volume'] == self.__list_position_detail_for_trade[i - shift]['Volume']:
                        # self.count_profit(trade_new, self.__list_position_detail_for_trade[i - shift])
                        self.__list_position_detail_for_trade.remove(
                            self.__list_position_detail_for_trade[i - shift])
                        # shift += 1  # 游标修正值
                        break
                    # trade_new的Volume小于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] < self.__list_position_detail_for_trade[i - shift]['Volume']:
                        # self.count_profit(trade_new, self.__list_position_detail_for_trade[i - shift])
                        self.__list_position_detail_for_trade[i - shift]['Volume'] -= trade_new['Volume']
                        break
                    # trade_new的Volume大于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] > self.__list_position_detail_for_trade[i - shift]['Volume']:
                        # self.count_profit(trade_new, self.__list_position_detail_for_trade[i - shift])
                        trade_new['Volume'] -= self.__list_position_detail_for_trade[i - shift]['Volume']
                        self.__list_position_detail_for_trade.remove(
                            self.__list_position_detail_for_trade[i - shift])
                        shift += 1  # 游标修正值

        # trade_new中"OffsetFlag"值="4"为平昨
        elif trade_new['OffsetFlag'] == '4':
            shift = 0
            # print(">>> Strategy.update_list_position_detail_for_trade_set_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "虚拟平昨")
            len_list_position_detail_for_trade = len(self.__list_position_detail_for_trade)
            for i in range(len_list_position_detail_for_trade):  # i为trade结构体，类型为dict
                print(self.__list_position_detail_for_trade[i - shift]['TradingDay'], "!=", trade_new['TradingDay'], "\n", self.__list_position_detail_for_trade[i - shift]['InstrumentID'], "==", trade_new['InstrumentID'], "\n", self.__list_position_detail_for_trade[i - shift]['HedgeFlag'], "==", trade_new['HedgeFlag'], "\n", self.__list_position_detail_for_trade[i - shift]['Direction'], "!=", trade_new[ 'Direction'])
                if self.__list_position_detail_for_trade[i - shift]['TradingDay'] != trade_new['TradingDay'] \
                        and self.__list_position_detail_for_trade[i - shift]['InstrumentID'] == trade_new[
                            'InstrumentID'] \
                        and self.__list_position_detail_for_trade[i - shift]['HedgeFlag'] == trade_new[
                            'HedgeFlag'] \
                        and self.__list_position_detail_for_trade[i - shift]['Direction'] != trade_new[
                            'Direction']:
                    # print(">>> Strategy.update_list_position_detail_for_trade_set_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "虚拟平昨执行")
                    # trade_new的Volume等于持仓列表首个满足条件的trade的Volume
                    if trade_new['Volume'] == self.__list_position_detail_for_trade[i - shift]['Volume']:
                        # self.count_profit(trade_new, self.__list_position_detail_for_trade[i - shift])
                        self.__list_position_detail_for_trade.remove(
                            self.__list_position_detail_for_trade[i - shift])
                        shift += 1  # 游标修正值
                        break
                    # trade_new的Volume小于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] < self.__list_position_detail_for_trade[i - shift]['Volume']:
                        # self.count_profit(trade_new, self.__list_position_detail_for_trade[i - shift])
                        self.__list_position_detail_for_trade[i - shift]['Volume'] -= trade_new['Volume']
                        break
                    # trade_new的Volume大于持仓列表首个满足条件的trade的Volume
                    elif trade_new['Volume'] > self.__list_position_detail_for_trade[i - shift]['Volume']:
                        # self.count_profit(trade_new, self.__list_position_detail_for_trade[i - shift])
                        trade_new['Volume'] -= self.__list_position_detail_for_trade[i - shift]['Volume']
                        self.__list_position_detail_for_trade.remove(
                            self.__list_position_detail_for_trade[i - shift])
                        shift += 1  # 游标修正值
        # print(">>> Strategy.update_list_position_detail_for_trade_set_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "虚拟平仓之后 len(self.__list_position_detail_for_trade) =", len(self.__list_position_detail_for_trade))

    # 更新占用保证金
    def update_current_margin(self):
        # print(">>> Strategy.update_current_margin() user_id =", self.__user_id, "strategy_id =", self.__strategy_id)
        # 中金所：同品种的买持仓和卖持仓，仅收较大单边保证金，同一品种内不区分不同月份合约
        # 上期所：同品种的买持仓和卖持仓，仅收较大单边保证金，同一品种内不区分不同月份合约
        # 郑商所：同一个合约买持仓和卖持仓，仅收较大单边保证金
        # 大商所：没有保证金免收政策
        self.__Margin_Occupied_CFFEX = self.Margin_Occupied_CFFEX()
        self.__Margin_Occupied_SHFE = self.Margin_Occupied_SHFE()
        self.__Margin_Occupied_CZCE = self.Margin_Occupied_CZCE()
        self.__Margin_Occupied_DCE = self.Margin_Occupied_DCE()
        # print(">>>Strategy.update_current_margin() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "\n    self.__Margin_Occupied_CFFEX =", self.__Margin_Occupied_CFFEX, "\n    self.__Margin_Occupied_SHFE =", self.__Margin_Occupied_SHFE, "\n    self.__Margin_Occupied_CZCE =", self.__Margin_Occupied_CZCE, "\n    self.__Margin_Occupied_DCE =", self.__Margin_Occupied_DCE)
        # self.__Margin_Occupied_total = self.__Margin_Occupied_CFFEX + self.__Margin_Occupied_SHFE + self.__Margin_Occupied_CZCE + self.__Margin_Occupied_DCE
        # 策略统计结构体中的元素：策略持仓占用保证金
        self.__current_margin = self.__Margin_Occupied_CFFEX + self.__Margin_Occupied_SHFE + self.__Margin_Occupied_CZCE + self.__Margin_Occupied_DCE
        return self.__current_margin

    # 从API获取必要的参数
    def get_td_api_arguments(self):
        # 通过API查询的数据，统一放到期货账户登录成功之后再调用
        self.__a_price_tick = self.get_price_tick(self.__a_instrument_id)  # A合约最小跳价
        self.__b_price_tick = self.get_price_tick(self.__b_instrument_id)  # B合约最小跳价
        self.__a_instrument_multiple = self.get_instrument_multiple(self.__a_instrument_id)  # A合约乘数
        self.__b_instrument_multiple = self.get_instrument_multiple(self.__b_instrument_id)  # B合约乘数
        self.__a_instrument_margin_ratio = self.get_instrument_margin_ratio(self.__a_instrument_id)  # A合约保证金率
        self.__b_instrument_margin_ratio = self.get_instrument_margin_ratio(self.__b_instrument_id)  # B合约保证金率
        self.__exchange_id_a = self.get_exchange_id(self.__a_instrument_id)  # A合约所属的交易所代码
        self.__exchange_id_b = self.get_exchange_id(self.__b_instrument_id)  # A合约所属的交易所代码
        self.__dict_commission_a = self.__user.get_commission(self.__a_instrument_id, self.__exchange_id_a)  # A合约手续费的dict
        self.__dict_commission_b = self.__user.get_commission(self.__b_instrument_id, self.__exchange_id_b)  # B合约手续费的dict

    # 装载xml
    def load_xml(self):
        # 如果从本地硬盘中正常获取到xml
        if self.__ctp_manager.get_XML_Manager().get_read_xml_status():
            self.__dict_arguments = dict()  # 从xml文件中读取的单策略的参数（含仓位）dict
            for i in self.__ctp_manager.get_XML_Manager().get_list_arguments():
                if self.__user_id == i['user_id'] and self.__strategy_id == i['strategy_id']:
                    self.set_arguments(i)  # 设置策略参数
                    self.set_position(i)  # 设置策略持仓变量

            for i in self.__ctp_manager.get_XML_Manager().get_list_statistics():
                if self.__user_id == i['user_id'] and self.__strategy_id == i['strategy_id']:
                    self.set_statistics(i)  # 赋值给单个变量和self.__dict_statistics
                    break

            for i in self.__ctp_manager.get_XML_Manager().get_list_position_detail_for_order():
                if self.__user_id == i['user_id'] and self.__strategy_id == i['strategy_id']:
                    self.__list_position_detail_for_order.append(i)

            for i in self.__ctp_manager.get_XML_Manager().get_list_position_detail_for_trade():
                if self.__user_id == i['user_id'] and self.__strategy_id == i['strategy_id']:
                    self.__list_position_detail_for_trade.append(i)

    # 获取策略占用保证金
    def get_current_margin(self):
        return self.__current_margin

    # 获取策略手续费
    def get_commission(self):
        return self.__total_commission

    # 获取策略持仓盈亏
    def get_profit_position(self):
        return self.__profit_position

    # 获取策略平仓盈亏
    def get_profit_close(self):
        return self.__profit_close

    """
    # 初始化持仓变量
    def init_position(self):
        print("Strategy.init_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id,
              "len(self.__list_position_detail_for_order) =", len(self.__list_position_detail_for_order))
        if len(self.__list_position_detail_for_order) == 0:
            return True
        elif len(self.__list_position_detail_for_order) > 0:
            for i in self.__list_position_detail_for_order:  # 遍历持仓明细列表
                if i['TradingDay'] == self.__TradingDay:  # 今仓
                    if i['InstrumentID'] == self.__a_instrument_id:  # A合约
                        if i['Direction'] == '0':  # 买
                            self.__position_a_buy_today += i['VolumeTradedBatch']  # A今买
                        elif i['Direction'] == '1':  # 卖
                            self.__position_a_sell_today += i['VolumeTradedBatch']  # A今卖
                    elif i['InstrumentID'] == self.__b_instrument_id:  # B合约
                        if i['Direction'] == '0':  # 买
                            self.__position_b_buy_today += i['VolumeTradedBatch']  # B今买
                        elif i['Direction'] == '1':  # 卖
                            self.__position_b_sell_today += i['VolumeTradedBatch']  # B今卖
                else:  # 非今仓
                    if i['InstrumentID'] == self.__a_instrument_id:  # A合约
                        if i['Direction'] == '0':  # 买
                            self.__position_a_buy_yesterday += i['VolumeTradedBatch']  # A昨买
                        elif i['Direction'] == '1':  # 卖
                            self.__position_a_sell_yesterday += i['VolumeTradedBatch']  # A昨卖
                    elif i['InstrumentID'] == self.__b_instrument_id:  # B合约
                        if i['Direction'] == '0':  # 买
                            self.__position_b_buy_yesterday += i['VolumeTradedBatch']  # B昨买
                        elif i['Direction'] == '1':  # 卖
                            self.__position_b_sell_yesterday += i['VolumeTradedBatch']  # B昨卖
            self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday  # A总买
            self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday  # A总卖
            self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday  # B总买
            self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday  # B总卖
            print("Strategy.init_position() userid =", self.__user_id, "strategy_id =", self.__strategy_id, "更新持仓:")
            print("     A卖(", self.__position_a_sell, ",", self.__position_a_sell_yesterday, ")")
            print("     B买(", self.__position_b_buy, ",", self.__position_b_buy_yesterday, ")")
            print("     A买(", self.__position_a_buy, ",", self.__position_a_buy_yesterday, ")")
            print("     B卖(", self.__position_b_sell, ",", self.__position_b_sell_yesterday, ")")
            return True
    """

    # 初始化持仓变量，遍历持仓明细列表trade计算得出
    def init_position(self):
        for trade in self.__list_position_detail_for_trade:
            if trade['instrumentid'] == self.__a_instrument_id:
                if trade['direction'] == '0':
                    if trade['tradingday'] == self.__MdApi_TradingDay:
                        self.__position_a_buy_today += trade['volume']  # A今买
                    else:
                        self.__position_a_buy_yesterday += trade['volume']  # A昨买
                elif trade['direction'] == '1':
                    if trade['tradingday'] == self.__MdApi_TradingDay:
                        self.__position_a_sell_today += trade['volume']  # A今卖
                    else:
                        self.__position_a_sell_yesterday += trade['volume']  # A昨卖
            elif trade['instrumentid'] == self.__b_instrument_id:
                if trade['direction'] == '0':
                    if trade['tradingday'] == self.__MdApi_TradingDay:
                        self.__position_b_buy_today += trade['volume']  # B今买
                    else:
                        self.__position_b_buy_yesterday += trade['volume']  # B昨买
                elif trade['direction'] == '1':
                    if trade['tradingday'] == self.__MdApi_TradingDay:
                        self.__position_b_sell_today += trade['volume']  # B今卖
                    else:
                        self.__position_b_sell_yesterday += trade['volume']  # B昨卖
            self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday  # A总买
            self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday  # A总卖
            self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday  # B总买
            self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday  # B总卖
            self.__position = self.__position_a_buy + self.__position_a_sell  # 总持仓

        # strategy_position = self.get_position()
        # data_main = {}
        # for key in strategy_position:
        #     data_main[key] = str(strategy_position[key])
        # data_main['strategy_id'] = self.__strategy_id  # data_main中加入键strategy_id
        # dict_msg = {
        #     'DataFlag': 'strategy_position',
        #     'UserId': self.__user_id,
        #     'DataMain': data_main  # 最新策略持仓
        # }
        # # print(">>> Strategy.init_position() user_id =", self.__user_id, 'data_flag = strategy_position', 'data_msg =', dict_msg)
        # self.__user.get_Queue_user().put(dict_msg)  # 进程通信：user->main，发送最新策略持仓

    # 统计指标
    def init_statistics(self):
        # RESUME模式,xml数据可用,装载xml数据
        if self.__user.get_TdApi_start_model() == PyCTP.THOST_TERT_RESUME:
            # 策略统计数据
            self.__dict_statistics = dict()
            for i in self.__user.get_xml_list_strategy_statistics():
                if i['strategy_id'] == self.__strategy_id:
                    self.__dict_statistics = i
                    self.set_statistics(self.__dict_statistics)  # 设置策略统计
                    break
            # print(">>> Strategy.init_strategy_data() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__dict_statistics =", self.__dict_statistics)

            # 进程间通信：策略统计
            dict_statistics = dict()
            for key in self.__dict_statistics:
                dict_statistics[key] = str(self.__dict_statistics[key])
            dict_msg = {
                'DataFlag': 'strategy_statistics',
                'UserId': self.__user_id,
                # 'DataMain': self.__dict_statistics  # 最新策略统计
                'DataMain': dict_statistics  # 最新策略统计
            }
            # print("Strategy.init_strategy_data() user_id =", self.__user_id, 'data_flag = strategy_statistics', 'data_msg =', dict_msg)
            self.__user.get_Queue_user().put(dict_msg)  # 进程通信：user->main，发送最新策略持仓
        # RESTART模式,xml数据不可用,使用初始值
        elif self.__user.get_TdApi_start_model() == PyCTP.THOST_TERT_RESTART:
            self.__dict_statistics = {
                # 成交统计的类计指标（trade）
                'a_profit_close': self.__a_profit_close,  # A平仓盈亏
                'b_profit_close': self.__b_profit_close,  # B平仓盈亏
                'profit_close': self.__profit_close,  # 平仓盈亏
                'commission': self.__total_commission,  # 手续费
                'profit': self.__profit,  # 净盈亏
                'a_traded_count': self.__a_traded_lots,  # A成交量
                'b_traded_count': self.__b_traded_lots,  # B成交量
                'a_traded_amount': self.__a_traded_amount,  # A成交金额
                'b_traded_amount': self.__b_traded_amount,  # B成交金额
                'a_commission_count': self.__a_commission,  # A手续费
                'b_commission_count': self.__b_commission,  # B手续费
                'profit_position': self.__profit_position,  # 持仓盈亏
                'current_margin': 0,  # self.__current_margin,  # 当前保证金总额
                # 报单统计的累计指标（order）
                'a_order_lots': self.__a_order_lots,  # A委托手数
                'b_order_lots': self.__b_order_lots,  # B委托手数
                'a_order_count': self.__a_order_times,  # A委托次数
                'b_order_count': self.__b_order_times,  # B委托次数
                'a_action_count': self.__a_action_count,  # A撤单次数
                'b_action_count': self.__b_action_count,  # B撤单次数
                'a_trade_rate': self.__a_trade_rate,  # A成交概率(成交手数/报单手数)
                'b_trade_rate': self.__b_trade_rate  # B成交概率(成交手数/报单手数)
            }

        self.set_statistics(self.get_statistics())  # 设置统计指标，主动触发进程间通信

            # # 遍历trade
        # for i in self.__list_QryTrade:
        #     # A合约的trade
        #     if i['InstrumentID'] == self.__a_instrument_id:
        #         self.__a_traded_lots += i['Volume']  # 成交量
        #         self.__a_traded_amount += i['Price'] * i['Volume'] * self.__a_instrument_multiple  # 成交金额
        #         self.__a_commission += self.count_commission(i)  # 手续费
        #
        #     elif i['InstrumentID'] == self.__b_instrument_id:
        #         self.__b_traded_lots += i['Volume']  # 成交量
        #         self.__b_commission += self.count_commission(i)  # 手续费
        #         self.__a_traded_amount += i['Price'] * i['Volume'] * self.__a_instrument_multiple  # 成交金额
        #
        # self.__total_commission = self.__a_commission + self.__b_commission
        # self.__profit = self.__profit_close - self.__total_commission
        # self.__dict_statistics['profit_close'] = self.__profit_close  # 平仓盈亏
        # self.__dict_statistics['commission'] = self.__total_commission  # 手续费
        # self.__dict_statistics['profit'] = self.__profit  # 净盈亏
        # self.__dict_statistics['volume'] = self.__a_traded_lots + self.__b_traded_lots  # 成交量
        # self.__dict_statistics['amount'] = self.__a_traded_amount + self.__b_traded_amount  # 成交金额
        # self.__dict_statistics['A_traded_rate'] = 0  # A成交率
        # self.__dict_statistics['B_traded_rate'] = 0  # B成交率

    # 更新持仓量变量，共12个持仓变量
    def update_position_for_OnRtnOrder(self, order):
        # print(">>> Strategy.update_position_for_OnRtnOrder() order =", order)
        # A成交
        if order['InstrumentID'] == self.__a_instrument_id:
            if order['CombOffsetFlag'] == '0':  # A开仓成交回报
                if order['Direction'] == '0':  # A买开仓成交回报
                    self.__position_a_buy_today += order['VolumeTradedBatch']  # 更新持仓
                elif order['Direction'] == '1':  # A卖开仓成交回报
                    self.__position_a_sell_today += order['VolumeTradedBatch']  # 更新持仓
            elif order['CombOffsetFlag'] == '3':  # A平今成交回报
                if order['Direction'] == '0':  # A买平今成交回报
                    self.__position_a_sell_today -= order['VolumeTradedBatch']  # 更新持仓
                elif order['Direction'] == '1':  # A卖平今成交回报
                    self.__position_a_buy_today -= order['VolumeTradedBatch']  # 更新持仓
            elif order['CombOffsetFlag'] == '4':  # A平昨成交回报
                if order['Direction'] == '0':  # A买平昨成交回报
                    self.__position_a_sell_yesterday -= order['VolumeTradedBatch']  # 更新持仓
                elif order['Direction'] == '1':  # A卖平昨成交回报
                    self.__position_a_buy_yesterday -= order['VolumeTradedBatch']  # 更新持仓
            # self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
            # self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        # B成交
        elif order['InstrumentID'] == self.__b_instrument_id:
            if order['CombOffsetFlag'] == '0':  # B开仓成交回报
                if order['Direction'] == '0':  # B买开仓成交回报
                    self.__position_b_buy_today += order['VolumeTradedBatch']  # 更新持仓
                elif order['Direction'] == '1':  # B卖开仓成交回报
                    self.__position_b_sell_today += order['VolumeTradedBatch']  # 更新持仓
            elif order['CombOffsetFlag'] == '3':  # B平今成交回报
                if order['Direction'] == '0':  # B买平今成交回报
                    self.__position_b_sell_today -= order['VolumeTradedBatch']  # 更新持仓
                elif order['Direction'] == '1':  # B卖平今成交回报
                    self.__position_b_buy_today -= order['VolumeTradedBatch']  # 更新持仓
            elif order['CombOffsetFlag'] == '4':  # B平昨成交回报
                if order['Direction'] == '0':  # B买平昨成交回报
                    self.__position_b_sell_yesterday -= order['VolumeTradedBatch']  # 更新持仓
                elif order['Direction'] == '1':  # B卖平昨成交回报
                    self.__position_b_buy_yesterday -= order['VolumeTradedBatch']  # 更新持仓
            # self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
            # self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
        self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
        self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
        self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
        self.__position = self.__position_b_sell + self.__position_b_buy

        # if Utils.Strategy_print:
        print("Strategy.update_position_for_OnRtnOrder() userid =", self.__user_id, "strategy_id =", self.__strategy_id, "更新持仓:")
        print("     A卖(", self.__position_a_sell, ",", self.__position_a_sell_yesterday, ")")
        print("     B买(", self.__position_b_buy, ",", self.__position_b_buy_yesterday, ")")
        print("     A买(", self.__position_a_buy, ",", self.__position_a_buy_yesterday, ")")
        print("     B卖(", self.__position_b_sell, ",", self.__position_b_sell_yesterday, ")")

    # 更新持仓变量，由OnRtnTrade()调用
    def update_position_for_OnRtnTrade(self, trade):
        if trade['Direction'] not in ['0', '1']:
            print(">>> Strategy.update_position_for_OnRtnTrade() 异常 user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "trade['Direction'] =", trade['Direction'])
        if trade['Volume'] == 0:
            print(">>> Strategy.update_position_for_OnRtnTrade() 异常 user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "trade['Volume'] =", trade['Volume'])
        # A成交
        if trade['InstrumentID'] == self.__a_instrument_id:
            if trade['OffsetFlag'] == '0':  # A开仓成交回报
                if trade['Direction'] == '0':  # A买开仓成交回报
                    self.__position_a_buy_today += trade['Volume']  # 更新持仓
                elif trade['Direction'] == '1':  # A卖开仓成交回报
                    self.__position_a_sell_today += trade['Volume']  # 更新持仓
            elif trade['OffsetFlag'] == '3':  # A平今成交回报
                if trade['Direction'] == '0':  # A买平今成交回报
                    self.__position_a_sell_today -= trade['Volume']  # 更新持仓
                elif trade['Direction'] == '1':  # A卖平今成交回报
                    self.__position_a_buy_today -= trade['Volume']  # 更新持仓
            elif trade['OffsetFlag'] == '4':  # A平昨成交回报
                if trade['Direction'] == '0':  # A买平昨成交回报
                    self.__position_a_sell_yesterday -= trade['Volume']  # 更新持仓
                elif trade['Direction'] == '1':  # A卖平昨成交回报
                    self.__position_a_buy_yesterday -= trade['Volume']  # 更新持仓
            else:
                print(">>> Strategy.update_position_for_OnRtnTrade() 异常 user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "A成交，else:")
            # self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
            # self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        # B成交
        elif trade['InstrumentID'] == self.__b_instrument_id:
            if trade['OffsetFlag'] == '0':  # B开仓成交回报
                if trade['Direction'] == '0':  # B买开仓成交回报
                    self.__position_b_buy_today += trade['Volume']  # 更新持仓
                elif trade['Direction'] == '1':  # B卖开仓成交回报
                    self.__position_b_sell_today += trade['Volume']  # 更新持仓
            elif trade['OffsetFlag'] == '3':  # B平今成交回报
                if trade['Direction'] == '0':  # B买平今成交回报
                    self.__position_b_sell_today -= trade['Volume']  # 更新持仓
                elif trade['Direction'] == '1':  # B卖平今成交回报
                    self.__position_b_buy_today -= trade['Volume']  # 更新持仓
            elif trade['OffsetFlag'] == '4':  # B平昨成交回报
                if trade['Direction'] == '0':  # B买平昨成交回报
                    self.__position_b_sell_yesterday -= trade['Volume']  # 更新持仓
                elif trade['Direction'] == '1':  # B卖平昨成交回报
                    self.__position_b_buy_yesterday -= trade['Volume']  # 更新持仓
            else:
                print(">>> Strategy.update_position_for_OnRtnTrade() 异常 user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "B成交，else:")
        else:
            print(">>> Strategy.update_position_for_OnRtnTrade() 异常 user_id =", self.__user_id, "strategy_id =",
                  self.__strategy_id, "既不属于A合约也不属于B合约")

        self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
        self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
        self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
        self.__position = self.__position_b_sell + self.__position_b_buy

        print("Strategy.update_position_for_OnRtnTrade() userid =", self.__user_id, "strategy_id =", self.__strategy_id)
        print("     A卖(", self.__position_a_sell, ",", self.__position_a_sell_yesterday, ")")
        print("     B买(", self.__position_b_buy, ",", self.__position_b_buy_yesterday, ")")
        print("     A买(", self.__position_a_buy, ",", self.__position_a_buy_yesterday, ")")
        print("     B卖(", self.__position_b_sell, ",", self.__position_b_sell_yesterday, ")")

    # 更新持仓变量，遍历持仓明细trade
    def update_position_of_position_detail_for_trade(self):
        self.__position_a_buy = 0
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
        for trade in self.__list_position_detail_for_trade:
            # 今仓
            if trade['TradingDay'] == self.__MdApi_TradingDay:
                # A合约
                if trade['InstrumentID'] == self.__a_instrument_id:
                    # 买
                    if trade['Direction'] == '0':
                        self.__position_a_buy_today +=trade['Volume']
                    # 卖
                    else:
                        self.__position_a_sell_today += trade['Volume']
                # B合约
                else:
                    # 买
                    if trade['Direction'] == '0':
                        self.__position_b_buy_today += trade['Volume']
                    # 卖
                    else:
                        self.__position_b_sell_today += trade['Volume']
            # 昨仓
            else:
                # A合约
                if trade['InstrumentID'] == self.__a_instrument_id:
                    # 买
                    if trade['Direction'] == '0':
                        self.__position_a_buy_yesterday += trade['Volume']
                    # 卖
                    else:
                        self.__position_a_sell_yesterday += trade['Volume']
                # B合约
                else:
                    # 买
                    if trade['Direction'] == '0':
                        self.__position_b_buy_yesterday += trade['Volume']
                    # 卖
                    else:
                        self.__position_b_sell_yesterday += trade['Volume']
        self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
        self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
        self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
        self.__position = self.__position_b_buy + self.__position_b_sell
        print("Strategy.update_position_for_position_detail() userid =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__list_position_detail_for_trade =", self.__list_position_detail_for_trade)
        # print("Strategy.update_position_for_position_detail() userid =", self.__user_id, "strategy_id =", self.__strategy_id)
        print("     A卖(", self.__position_a_sell, ",", self.__position_a_sell_yesterday, ")")
        print("     B买(", self.__position_b_buy, ",", self.__position_b_buy_yesterday, ")")
        print("     A买(", self.__position_a_buy, ",", self.__position_a_buy_yesterday, ")")
        print("     B卖(", self.__position_b_sell, ",", self.__position_b_sell_yesterday, ")")

    # 利用order持仓明细更新持仓变量
    def update_position_of_position_detail_for_order(self):
        self.__position_a_buy = 0
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
        for order in self.__list_position_detail_for_order:
            if order['TradingDay'] == self.__MdApi_TradingDay:  # 今仓
                if order['InstrumentID'] == self.__a_instrument_id:  # A合约
                    if order['Direction'] == '0':  # 买
                        self.__position_a_buy_today += order['VolumeTradedBatch']
                    elif order['Direction'] == '1':  # 卖
                        self.__position_a_sell_today += order['VolumeTradedBatch']
                elif order['InstrumentID'] == self.__b_instrument_id:  # B合约
                    if order['Direction'] == '0':  # 买
                        self.__position_b_buy_today += order['VolumeTradedBatch']
                    elif order['Direction'] == '1':  # 卖
                        self.__position_b_sell_today += order['VolumeTradedBatch']
            else:  # 昨仓
                if order['InstrumentID'] == self.__a_instrument_id:  # A合约
                    if order['Direction'] == '0':  # 买
                        self.__position_a_buy_yesterday += order['VolumeTradedBatch']
                    elif order['Direction'] == '1':  # 卖
                        self.__position_a_sell_yesterday += order['VolumeTradedBatch']
                elif order['InstrumentID'] == self.__b_instrument_id:  # B合约
                    if order['Direction'] == '0':  # 买
                        self.__position_b_buy_yesterday += order['VolumeTradedBatch']
                    elif order['Direction'] == '1':  # 卖
                        self.__position_b_sell_yesterday += order['VolumeTradedBatch']
        self.__position_a_buy = self.__position_a_buy_today + self.__position_a_buy_yesterday
        self.__position_a_sell = self.__position_a_sell_today + self.__position_a_sell_yesterday
        self.__position_b_buy = self.__position_b_buy_today + self.__position_b_buy_yesterday
        self.__position_b_sell = self.__position_b_sell_today + self.__position_b_sell_yesterday
        self.__position = self.__position_b_buy + self.__position_b_sell
        print("Strategy.update_position_of_position_detail_for_order() userid =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__list_position_detail_for_trade =", self.__list_position_detail_for_trade)
        # print("Strategy.update_position_of_position_detail_for_order() userid =", self.__user_id, "strategy_id =", self.__strategy_id)
        print("     A卖(", self.__position_a_sell, ",", self.__position_a_sell_yesterday, ")")
        print("     B买(", self.__position_b_buy, ",", self.__position_b_buy_yesterday, ")")
        print("     A买(", self.__position_a_buy, ",", self.__position_a_buy_yesterday, ")")
        print("     B卖(", self.__position_b_sell, ",", self.__position_b_sell_yesterday, ")")

    # 报单统计（order）
    def statistics_for_order(self, Order):
        """
        统计指标
        self.__a_order_value = 0  # A委托手数
        self.__b_order_value = 0  # B委托手数
        self.__a_order_times = 0  # A委托次数
        self.__b_order_times = 0  # B委托次数
        """
        # Order结构体重键名VolumeTotal：未成交数量，VolumeTotalOriginal：报单量，VolumeTraded：成交数量
        # 筛选出交易所的报单回调做统计（OrderSysID长度为12，VolumeTraded值为0）
        if len(Order['OrderSysID']) == 12:
            if Order['OrderStatus'] in ['0', '5']:  # '0': 全部成交，'5': 撤单
                # A合约的Order
                if Order['InstrumentID'] == self.__a_instrument_id:
                    self.__a_order_lots += Order['VolumeTotalOriginal']  # A委托手数
                    self.__a_order_times += 1  # A委托次数
                    self.__a_trade_rate = self.__a_traded_lots / self.__a_order_lots  # A成交率
                # B合约的Order
                elif Order['InstrumentID'] == self.__b_instrument_id:
                    self.__b_order_lots += Order['VolumeTotalOriginal']  # B委托手数
                    self.__b_order_times += 1  # B委托次数
                    self.__b_trade_rate = self.__b_traded_lots / self.__b_order_lots  # B成交率
                # print(">>> Strategy.statistics_for_order() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "a_traded_lots / a_order_lots / a_order_times", self.__a_traded_lots, '/', self.__a_order_lots, '/', self.__a_order_times, "b_traded_lots / b_order_lots / b_order_times", self.__b_traded_lots, '/', self.__b_order_lots, '/', self.__b_order_times)
                self.__dict_statistics['A_traded_rate'] = self.__a_trade_rate  # A成交率
                self.__dict_statistics['B_traded_rate'] = self.__b_trade_rate  # B成交率
            # 撤单数量统计
            if Order['OrderStatus'] == '5':
                if Order['InstrumentID'] == self.__a_instrument_id:
                    self.__a_action_count_strategy += 1
                else:
                    self.__b_action_count_strategy += 1

    # 成交统计（trade）
    def statistics_for_trade(self, Trade):
        """
        统计指标
        A、B的成交量
        A、B的成交金额
        A、B的手续费
        """
        # A合约的Trade
        if Trade['InstrumentID'] == self.__a_instrument_id:
            self.__a_traded_lots += Trade['Volume']  # 成交量
            self.__a_traded_amount += Trade['Price'] * Trade['Volume'] * self.__a_instrument_multiple  # 成交金额
            self.__a_commission += self.count_commission(Trade)  # A手续费
            if self.__a_order_lots > 0:
                self.__a_trade_rate = self.__a_traded_lots / self.__a_order_lots  # A成交率
        # B合约的Trade
        elif Trade['InstrumentID'] == self.__b_instrument_id:
            self.__b_traded_lots += Trade['Volume']  # 成交量
            self.__b_traded_amount += Trade['Price'] * Trade['Volume'] * self.__b_instrument_multiple  # 成交金额
            self.__b_commission += self.count_commission(Trade)  # B手续费
            if self.__b_order_lots > 0:
                self.__b_trade_rate = self.__b_traded_lots / self.__b_order_lots  # A成交率
        else:
            print("Strategy.statistics_for_trade() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "既不属于A也不属于B合约的trade")
        self.__total_traded_lots = self.__a_traded_lots + self.__b_traded_lots
        self.__total_traded_amount = self.__a_traded_amount + self.__b_traded_amount  # A、B成交金额合计
        self.__total_commission = self.__a_commission + self.__b_commission  # 手续费
        self.__profit = self.__profit_close - self.__total_commission  # 更新净盈亏
        self.__dict_statistics['volume'] = self.__total_traded_lots  # 成交量
        self.__dict_statistics['amount'] = self.__total_traded_amount  # 成交金额
        self.__dict_statistics['commission'] = self.__total_commission  # 手续费
        self.__dict_statistics['A_traded_rate'] = self.__a_trade_rate  # A成交率
        self.__dict_statistics['B_traded_rate'] = self.__b_trade_rate  # B成交率
        # print(">>> Strategy.statistics_for_trade() user_id =", self.__user_id, "strategy_id =", self.__strategy_id,
        #       "a_traded_lots / a_order_lots / a_order_times", self.__a_traded_lots, '/', self.__a_order_lots, '/',
        #       self.__a_order_times, "b_traded_lots / b_order_lots / b_order_times", self.__b_traded_lots, '/',
        #       self.__b_order_lots, '/', self.__b_order_times)

    # order、trade统计
    def statistics(self, order=None, trade=None):
        # print(">>> Strategy.statistics() user_id =", self.__user_id, "strategy_id =", self.__strategy_id)
        # 根据order统计A、B合约的：报单手数、撤单手数
        if isinstance(order, dict):
            # print(">>> Strategy.statistics() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "order =", order)
            if order['OrderStatus'] in ['0', '5']:  # 仅统计'OrderStatus'为0和5的原始报单量
                if order['InstrumentID'] == self.__a_instrument_id:  # A合约
                    self.__dict_statistics['a_order_lots'] += order['VolumeTotalOriginal']  # A报单手数
                    # if order['OrderStatus'] == '5':  # 撤单，在user的OnRtnOrder中统计
                    #     self.__dict_statistics['a_action_count'] += 1  # A撤单次数
                elif order['InstrumentID'] == self.__b_instrument_id:  # B合约
                    self.__dict_statistics['b_order_lots'] += order['VolumeTotalOriginal']  # B报单手数
                    # if order['OrderStatus'] == '5':  # 撤单，在user的OnRtnOrder中统计
                    #     self.__dict_statistics['b_action_count'] += 1  # B撤单次数

        # 根据trade统计A、B合约的：手续费、平仓盈亏、成交手数、成交金额
        if isinstance(trade, dict):
            # A合约
            if trade['InstrumentID'] == self.__a_instrument_id:  # A合约
                self.__dict_statistics['a_traded_count'] += trade['Volume']  # A成交手数
                self.__dict_statistics['a_traded_amount'] += trade['Volume'] * trade['Price'] * self.__a_instrument_multiple # A成交金额
                self.__dict_statistics['a_commission_count'] += self.count_commission(trade)  # A手续费
            # B合约
            elif trade['InstrumentID'] == self.__b_instrument_id:  # B合约
                self.__dict_statistics['b_traded_count'] += trade['Volume']  # B成交手数
                self.__dict_statistics['b_traded_amount'] += trade['Volume'] * trade['Price'] * self.__b_instrument_multiple # A成交金额
                self.__dict_statistics['b_commission_count'] += self.count_commission(trade)  # B手续费
            # 总手续费
            self.__dict_statistics['commission_count'] = self.__dict_statistics['a_commission_count'] + self.__dict_statistics['b_commission_count']

        # order和trade都可能触发变化的指标：A成交概率、B成交概率
        if self.__dict_statistics['a_order_count'] > 0:
            self.__dict_statistics['a_trade_rate'] = self.__dict_statistics['a_traded_count'] / self.__dict_statistics['a_order_count']
        if self.__dict_statistics['b_order_count'] > 0:
            self.__dict_statistics['b_trade_rate'] = self.__dict_statistics['b_traded_count'] / self.__dict_statistics['b_order_count']

    # 获取策略交易统计指标dict
    def get_dict_statistics(self):
        return self.__dict_statistics

    # 统计持仓明细中属于中金所的持仓保证金
    def Margin_Occupied_CFFEX(self):
        self.__Margin_Occupied_CFFEX = 0
        # 从持仓明细中过滤出中金所的持仓明细
        list_position_detail_for_trade_CFFEX = list()
        for i in self.__list_position_detail_for_trade:
            if i['ExchangeID'] == 'CFFEX':
                i['CommodityID'] = Utils.extract_commodity_id(i['InstrumentID'])  # 品种代码
                list_position_detail_for_trade_CFFEX.append(i)
        if len(list_position_detail_for_trade_CFFEX) == 0:  # 无持仓，返回保证金初始值0
            return self.__Margin_Occupied_CFFEX

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
            self.__Margin_Occupied_CFFEX = self.count_single_instrument_margin_CFFEX(list_position_detail_for_trade_CFFEX)
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
        return self.__Margin_Occupied_CFFEX

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_CFFEX(self, list_input):
        list_position_detail_for_trade_CFFEX = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_CFFEX:
            i['CurrMargin'] = i['Price'] * i['Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
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
        # print(">>>Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "len(self.__list_position_detail_for_trade) =", len(self.__list_position_detail_for_trade), "len(self.__list_position_detail_for_order) =", len(self.__list_position_detail_for_order))
        for i in self.__list_position_detail_for_trade:
            # print(">>>Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "i['ExchangeID'] =", i['ExchangeID'])
            if i['ExchangeID'] == 'SHFE':
                i['CommodityID'] = i['InstrumentID'][:2]
                list_position_detail_for_trade_SHFE.append(i)
        if len(list_position_detail_for_trade_SHFE) == 0:  # 无上期所持仓，返回初始值0
            # print(">>>Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "无上期所持仓，返回保证金初始值0")
            return self.__Margin_Occupied_SHFE

        # 选出持仓明细中存在的品种代码
        list_commodity_id = list()  # 保存持仓中存在品种代码
        for i in list_position_detail_for_trade_SHFE:
            if i['CommodityID'] in list_commodity_id:
                pass
            else:
                list_commodity_id.append(i['CommodityID'])
        # 同品种买持仓占用保证金求和n1、卖持仓保证金求和n2，保证金收取政策为max(n1,n2)
        # a合约和b合约是同一个品种
        if len(list_commodity_id) == 1:
            self.__Margin_Occupied_SHFE = self.count_single_instrument_margin_SHFE(list_position_detail_for_trade_SHFE)
            # print(">>> Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__Margin_Occupied_SHFE =", self.__Margin_Occupied_SHFE)
        # a合约和b合约是不同的品种
        elif len(list_commodity_id) == 2:
            # 分别选出两种持仓的明细
            list_position_detail_for_trade_SHFE_0 = list()
            list_position_detail_for_trade_SHFE_1 = list()
            for i in list_position_detail_for_trade_SHFE:
                if list_commodity_id[0] == i['CommodityID']:
                    list_position_detail_for_trade_SHFE_0.append(i)
                elif list_commodity_id[1] == i['CommodityID']:
                    list_position_detail_for_trade_SHFE_1.append(i)
            # 计算两个品种分别占用的持仓保证金
            margin_0 = self.count_single_instrument_margin_SHFE(list_position_detail_for_trade_SHFE_0)
            margin_1 = self.count_single_instrument_margin_SHFE(list_position_detail_for_trade_SHFE_1)
            self.__Margin_Occupied_SHFE = margin_0 + margin_1
        return self.__Margin_Occupied_SHFE

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_SHFE(self, list_input):
        list_position_detail_for_trade_SHFE = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_SHFE:
            i['CurrMargin'] = i['Price'] * i['Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            if i['Direction'] == '0':
                margin_buy += i['CurrMargin']
            elif i['Direction'] == '1':
                margin_sell += i['CurrMargin']
        margin = max(margin_buy, margin_sell)
        return margin

    # 统计持仓明细中属于上海期货交易所的持仓保证金
    def Margin_Occupied_CZCE(self):
        self.__Margin_Occupied_CZCE = 0
        # 从持仓明细中过滤出郑州期货交易所的持仓明细
        list_position_detail_for_trade_CZCE = list()
        for i in self.__list_position_detail_for_trade:
            if i['ExchangeID'] == 'CZCE':
                i['CommodityID'] = i['InstrumentID'][:2]
                list_position_detail_for_trade_CZCE.append(i)
        if len(list_position_detail_for_trade_CZCE) == 0:  # 无上期所持仓，返回初始值0
            return self.__Margin_Occupied_CZCE

        # 选出持仓明细中存在的品种代码
        list_commodity_id = list()  # 保存持仓中存在品种代码
        for i in list_position_detail_for_trade_CZCE:
            if i['CommodityID'] in list_commodity_id:
                pass
            else:
                list_commodity_id.append(i['CommodityID'])
        # 同品种买持仓占用保证金求和n1、卖持仓保证金求和n2，保证金收取政策为max(n1,n2)
        # a合约和b合约是同一个品种
        self.__Margin_Occupied_CZCE = self.count_single_instrument_margin_CZCE(list_position_detail_for_trade_CZCE)
        # print(">>> Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__Margin_Occupied_CZCE =", self.__Margin_Occupied_CZCE)
        return self.__Margin_Occupied_CZCE

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_CZCE(self, list_input):
        list_position_detail_for_trade_CZCE = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_CZCE:
            i['CurrMargin'] = i['Price'] * i['Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            if i['Direction'] == '0':
                margin_buy += i['CurrMargin']
            elif i['Direction'] == '1':
                margin_sell += i['CurrMargin']
        margin = margin_buy + margin_sell
        return margin

    # 统计持仓明细中属于大连期货交易所的持仓保证金
    def Margin_Occupied_DCE(self):
        self.__Margin_Occupied_DCE = 0
        # 从持仓明细中过滤出大连期货交易所的持仓明细
        list_position_detail_for_trade_DCE = list()
        for i in self.__list_position_detail_for_trade:
            if i['ExchangeID'] == 'DCE':
                i['CommodityID'] = i['InstrumentID'][:2]
                list_position_detail_for_trade_DCE.append(i)
        if len(list_position_detail_for_trade_DCE) == 0:  # 无大连期货交易所持仓，返回初始值0
            return self.__Margin_Occupied_DCE
        self.__Margin_Occupied_DCE = self.count_single_instrument_margin_DCE(list_position_detail_for_trade_DCE)
        # # 选出持仓明细中存在的品种代码
        # list_commodity_id = list()  # 保存持仓中存在品种代码
        # for i in list_position_detail_for_trade_DCE:
        #     if i['CommodityID'] in list_commodity_id:
        #         pass
        #     else:
        #         list_commodity_id.append(i['CommodityID'])
        # # 同品种买持仓占用保证金求和n1、卖持仓保证金求和n2，保证金收取政策为max(n1,n2)
        # # a合约和b合约是同一个品种
        # if len(list_commodity_id) == 1:
        #     self.__Margin_Occupied_DCE = self.count_single_instrument_margin_DCE(list_position_detail_for_trade_DCE)
        #     # print(">>> Strategy.Margin_Occupied_SHFE() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__Margin_Occupied_DCE =", self.__Margin_Occupied_DCE)
        # # a合约和b合约是不同的品种
        # elif len(list_commodity_id) == 2:
        #     # 分别选出两种持仓的明细
        #     list_position_detail_for_trade_DCE_0 = list()
        #     list_position_detail_for_trade_DCE_1 = list()
        #     for i in list_position_detail_for_trade_DCE:
        #         if list_commodity_id[0] == i['CommodityID']:
        #             list_position_detail_for_trade_DCE_0.append(i)
        #         elif list_commodity_id[1] == i['CommodityID']:
        #             list_position_detail_for_trade_DCE_1.append(i)
        #     # 计算两个品种分别占用的持仓保证金
        #     margin_0 = self.count_single_instrument_margin_DCE(list_position_detail_for_trade_DCE_0)
        #     margin_1 = self.count_single_instrument_margin_DCE(list_position_detail_for_trade_DCE_1)
        #     self.__Margin_Occupied_DCE = margin_0 + margin_1
        return self.__Margin_Occupied_DCE

    # 同一个品种持仓保证金计算，形参为持仓明细trade，返回实际保证金占用值
    def count_single_instrument_margin_DCE(self, list_input):
        list_position_detail_for_trade_DCE = list_input
        margin_buy = 0  # 买持仓保证金
        margin_sell = 0  # 卖持仓保证金
        for i in list_position_detail_for_trade_DCE:
            i['CurrMargin'] = i['Price'] * i['Volume'] * self.__a_instrument_multiple * self.__a_instrument_margin_ratio
            if i['Direction'] == '0':
                margin_buy += i['CurrMargin']
            elif i['Direction'] == '1':
                margin_sell += i['CurrMargin']
        margin = margin_buy + margin_sell
        return margin

    # 计算手续费，形参为trade记录结构体，返回值为该笔trade记录的手续费金额
    def count_commission(self, trade):
        # A合约的trade
        if trade['InstrumentID'] == self.__a_instrument_id:
            # 开仓
            if trade['OffsetFlag'] == '0':
                commission_amount = \
                    self.__dict_commission_a['OpenRatioByMoney'] * trade['Price'] * trade['Volume'] * self.__a_instrument_multiple \
                    + self.__dict_commission_a['OpenRatioByVolume'] * trade['Volume']
            # 平今
            elif trade['OffsetFlag'] == '3':
                commission_amount = \
                    self.__dict_commission_a['CloseTodayRatioByMoney'] * trade['Price'] * trade['Volume'] * self.__a_instrument_multiple \
                    + self.__dict_commission_a['CloseTodayRatioByVolume'] * trade['Volume']
            # 平昨
            elif trade['OffsetFlag'] == '4':
                commission_amount = \
                    self.__dict_commission_a['CloseRatioByMoney'] * trade['Price'] * trade['Volume'] * self.__a_instrument_multiple \
                    + self.__dict_commission_a['CloseRatioByVolume'] * trade['Volume']
        elif trade['InstrumentID'] == self.__b_instrument_id:
            # 开仓
            if trade['OffsetFlag'] == '0':
                commission_amount = \
                    self.__dict_commission_a['OpenRatioByMoney'] * trade['Price'] * trade['Volume'] * self.__a_instrument_multiple \
                    + self.__dict_commission_a['OpenRatioByVolume'] * trade['Volume']
            # 平今
            elif trade['OffsetFlag'] == '3':
                commission_amount = \
                    self.__dict_commission_a['CloseTodayRatioByMoney'] * trade['Price'] * trade['Volume'] * self.__a_instrument_multiple \
                    + self.__dict_commission_a['CloseTodayRatioByVolume'] * trade['Volume']
            # 平昨
            elif trade['OffsetFlag'] == '4':
                commission_amount = \
                    self.__dict_commission_a['CloseRatioByMoney'] * trade['Price'] * trade['Volume'] * self.__a_instrument_multiple \
                    + self.__dict_commission_a['CloseRatioByVolume'] * trade['Volume']
        return commission_amount

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
                    if InstrumentID == self.__a_instrument_id:
                        self.__a_commission_order += 1
                    elif InstrumentID == self.__b_instrument_id:
                        self.__b_commission_order += 1
                    # print(">>>Strategy.count_commission_order() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "申报费", self.__a_instrument_id, "=", self.__a_commission_order, self.__b_instrument_id, "=", self.__b_commission_order)
                else:
                    if order['OrderStatus'] in ['0', '5']:
                        self.__list_OrderRef_for_count_commission_order.remove(OrderRef)
                        if order['OrderStatus'] == '5':
                            if InstrumentID == self.__a_instrument_id:
                                self.__a_commission_order += 1
                            elif InstrumentID == self.__b_instrument_id:
                                self.__b_commission_order += 1
                            # print(">>>Strategy.count_commission_order() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "申报费", self.__a_instrument_id, "=", self.__a_commission_order, self.__b_instrument_id, "=", self.__b_commission_order)

    # 计算策略持仓盈亏，由行情回调驱动
    def update_profit_position(self, tick):
        if len(self.__list_position_detail_for_trade) > 0:  # 有持仓时更新持仓盈亏
            for i in self.__list_position_detail_for_trade:  # 遍历持仓列表
                if tick['InstrumentID'] == i['InstrumentID']:  # 找到持仓明细中合约代码与最新行情合约代码相同的
                    # A合约
                    if i['InstrumentID'] == self.__a_instrument_id:
                        # 买持仓
                        if i['Direction'] == '0':
                            i['profit_position'] = (tick['BidPrice1'] - i['Price']) * self.__a_instrument_multiple * i['Volume']
                        # 卖持仓
                        elif i['Direction'] == '1':
                            i['profit_position'] = (i['Price'] - tick['AskPrice1']) * self.__a_instrument_multiple * i['Volume']
                    # B合约
                    elif i['InstrumentID'] == self.__b_instrument_id:
                        # 买持仓
                        if i['Direction'] == '0':
                            i['profit_position'] = (tick['BidPrice1'] - i['Price']) * self.__b_instrument_multiple * i['Volume']
                        # 卖持仓
                        elif i['Direction'] == '1':
                            i['profit_position'] = (i['Price'] - tick['AskPrice1']) * self.__b_instrument_multiple * i['Volume']
                if 'profit_position' in i:  # 持仓明细中已经存字段'profit_position'的
                    self.__profit_position += i['profit_position']  # 单策略所有持仓盈亏累积

    # 计算平仓盈亏，形参分别为开仓和平仓的trade
    def count_profit(self, trade_close, trade_open):
        """
        order中的CombOffsetFlag 或 trade中的OffsetFlag值枚举：
        '0'：开仓
        '1'：平仓
        '3'：平今
        '4'：平昨
        """
        volume_traded = min(trade_close['Volume'], trade_open['Volume'])  # 成交量以较小值一个为准
        profit_close = 0  # 平仓盈亏临时变量
        if trade_close['InstrumentID'] == self.__a_instrument_id:  # A合约
            if trade_close['Direction'] == '0':  # 买平仓
                profit_close = (trade_open['Price'] - trade_close['Price']) * self.__a_instrument_multiple * volume_traded
            elif trade_close['Direction'] == '1':  # 卖平仓
                profit_close = (trade_close['Price'] - trade_open['Price']) * self.__a_instrument_multiple * volume_traded
            self.__a_profit_close += profit_close
            self.__dict_statistics['a_profit_close'] += profit_close  # A平仓盈亏
        elif trade_close['InstrumentID'] == self.__b_instrument_id:  # B合约
            if trade_close['Direction'] == '0':  # 买平仓
                profit_close = (trade_open['Price'] - trade_close['Price']) * self.__b_instrument_multiple * volume_traded
            elif trade_close['Direction'] == '1':  # 卖平仓
                profit_close = (trade_close['Price'] - trade_open['Price']) * self.__b_instrument_multiple * volume_traded
            self.__b_profit_close += profit_close
            self.__dict_statistics['b_profit_close'] += profit_close  # A平仓盈亏
        else:
            print("Strategy.count_profit() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "既不属于A合约也不属于B合约的Trade")
        self.__profit_close = self.__a_profit_close + self.__b_profit_close
        self.__profit = self.__profit_close - self.__total_commission
        # A、B平仓盈亏累计
        self.__dict_statistics['profit_close'] = self.__profit_close
        # A、B净盈亏之和
        self.__dict_statistics['profit'] = self.__profit

        # self.__b_instrument_multiple,正确
        # 输出A、B各自平仓盈亏检查,错误
        # print(">>> Strategy.count_profit() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__a_profit_close =", self.__a_profit_close, "self.__b_profit_close =", self.__b_profit_close)

    # 设置strategy初始化状态
    def set_init_finished(self, bool_input):
        self.__init_finished = bool_input
        # 通知给User
        # self.__user.set_strategy_init_finished(bool_input)
    
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
        list_instrument_id = [self.__a_instrument_id, self.__b_instrument_id]
        return list_instrument_id

    def get_a_instrument_id(self):
        return self.__a_instrument_id

    def get_b_instrument_id(self):
        return self.__b_instrument_id

    # 判断从API查询的合约信息中是否存在形参的合约，存在：返回True，不存在：返回False
    def if_exist_instrument_id(self, instrument_id):
        found_flag = False
        for i in self.__user.get_instrument_info():
            if i['InstrumentID'] == instrument_id:
                found_flag = True
                return True
        if found_flag == False:
            return False

    # 获取指定合约最小跳'PriceTick'
    def get_price_tick(self, instrument_id):
        found = False
        for i in self.__user.get_instrument_info():
            if i['InstrumentID'] == instrument_id:
                found = True
                return i['PriceTick']
        if found is False:
            print("Strategy.get_price_tick() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "instrument_id =", instrument_id, "异常，获取合约最小跳，未找到合约")
            return 0

    # 获取指定合约乘数
    def get_instrument_multiple(self, instrument_id):
        found = False
        for i in self.__user.get_instrument_info():
            if i['InstrumentID'] == instrument_id:
                found = True
                return i['VolumeMultiple']
        if found is False:
            print("Strategy.get_instrument_multiple() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "instrument_id =", instrument_id, "异常，获取合约乘数失败，未找到合约")
            return 0

    # 获取指定合约保证金率
    def get_instrument_margin_ratio(self, instrument_id):
        found = False
        for i in self.__user.get_instrument_info():
            if i['InstrumentID'] == instrument_id:
                found = True
                return i['LongMarginRatio']
        if found is False:
            print("Strategy.get_instrument_margin_ratio() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "instrument_id =", instrument_id, "异常，获取合约保证金率失败，未找到合约")
            return 0

    # 获取指定合约所属的交易搜代码
    def get_exchange_id(self, instrument_id):
        found = False
        for i in self.__user.get_instrument_info():
            if i['InstrumentID'] == instrument_id:
                found = True
                return i['ExchangeID']
        if found is False:
            print("Strategy.get_exchange_id() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "instrument_id =", instrument_id, "异常，获取合约所属交易所代码失败，未找到合约")
            return 0
    
    # # 更新撤单次数，在user类中的order回调中调用，第一时间更新撤单计数
    # def update_action_count(self):
    #     self.__a_action_count = self.__user.get_dict_action()[self.__a_instrument_id]
    #     self.__b_action_count = self.__user.get_dict_action()[self.__b_instrument_id]

    def set_a_action_count(self, int_count):
        print(">>> Strategy.set_a_action_count() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "instrument_id =", self.__a_instrument_id, "self.__a_action_count =", self.__a_action_count)
        self.__a_action_count = int_count
        # self.signal_update_strategy_position.emit(self)  # 更新界面

    def set_b_action_count(self, int_count):
        print(">>> Strategy.set_b_action_count() user_id =", self.__user_id, "strategy_id =", self.__strategy_id,
              "instrument_id =", self.__b_instrument_id, "self.__b_action_count =", self.__b_action_count)
        self.__b_action_count = int_count
        # self.signal_update_strategy_position.emit(self)  # 更新界面

    def get_a_action_count_strategy(self):
        return self.__a_action_count_strategy

    def get_b_action_count_strategy(self):
        return self.__b_action_count_strategy

    def get_a_action_count(self):
        return self.__a_action_count

    def get_b_action_count(self):
        return self.__b_action_count

    def set_a_open_count(self, int_count):
        self.__a_open_count = int_count

    def set_b_open_count(self, int_count):
        self.__b_open_count = int_count

    def get_a_open_count(self):
        return self.__a_open_count

    def get_b_open_count(self):
        return self.__b_open_count

    # 获取策略交易开关
    def get_on_off(self):
        return self.__strategy_on_off

    def set_on_off(self, int_input):
        self.__strategy_on_off = int_input
        # self.signal_update_strategy.emit(self)

    def get_spread_short(self):
        return self.__spread_short

    def get_spread_long(self):
        return self.__spread_long

    def get_a_price_tick(self):
        return self.__a_price_tick

    def get_b_price_tick(self):
        return self.__b_price_tick

    def set_clicked_status(self, int_input):  # 0：未选中、1：单账户窗口中被选中、2：总账户窗口中被选中
        self.__clicked_status = int_input

    # 设置持仓
    def set_position(self, dict_args):
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
        self.__position = self.__position_a_buy + self.__position_a_sell
        # print(">>> Strategy.set_position() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "dict_args=", dict_args)
        # 如果界面初始化完成、程序运行当中，每次调用该方法都触发界面类的槽函数update_strategy
        # if self.__user.get_CTPManager().get_init_finished():
        # self.signal_pushButton_set_position_setEnabled.emit()
        # self.signal_update_strategy.emit(self)  # 信号槽连接：策略对象修改策略 -> 界面刷新策略
        print("Strategy.set_position() userid =", self.__user_id, "strategy_id =", self.__strategy_id)
        print("     A卖(", self.__position_a_sell, ",", self.__position_a_sell_yesterday, ")")
        print("     B买(", self.__position_b_buy, ",", self.__position_b_buy_yesterday, ")")
        print("     A买(", self.__position_a_buy, ",", self.__position_a_buy_yesterday, ")")
        print("     B卖(", self.__position_b_sell, ",", self.__position_b_sell_yesterday, ")")

        data_main = self.get_position()
        data_main['strategy_id'] = self.__strategy_id  # dict结构体中加入strategy_id
        dict_msg = {
            'DataFlag': 'strategy_position',
            'UserId': self.__user_id,
            'DataMain': data_main  # 最新策略持仓

        }
        print(">>> Strategy.set_position() user_id =", self.__user_id, 'data_flag = strategy_position',
              'data_msg =', dict_msg)
        self.__user.get_Queue_user().put(dict_msg)  # 进程通信：user->main，发送最新策略持仓

    def get_position(self):
        dict_position = {
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
            'position': self.__position
        }
        return dict_position

    # 设置持仓明细，收到socket设置持仓量回报时调用
    def set_list_position_detail(self, dict_args):
        print(">>> Strategy.set_list_position_detail() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "dict_args =", dict_args)
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        volume = self.__position_a_buy_yesterday - dict_args['position_a_buy_yesterday']  # A昨买需要减去的量
        if volume > 0:
            Direction = '1'  # 卖
            CombOffsetFlag = '4'  # 平昨
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__a_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)

        volume = self.__position_a_buy_today - dict_args['position_a_buy_today']  # A今买需要减去的量
        if volume > 0:
            Direction = '1'  # 卖
            CombOffsetFlag = '3'  # 平今
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__a_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)

        volume = self.__position_a_sell_yesterday - dict_args['position_a_sell_yesterday']  # A昨卖需要减去的量
        if volume > 0:
            Direction = '0'  # 买
            CombOffsetFlag = '4'  # 平昨
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__a_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)

        volume = self.__position_a_sell_today - dict_args['position_a_sell_today']  # A今卖需要减去的量
        if volume > 0:
            Direction = '0'  # 买
            CombOffsetFlag = '3'  # 平今
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__a_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)

        volume = self.__position_b_buy_yesterday - dict_args['position_b_buy_yesterday']  # B昨买需要减去的量
        if volume > 0:
            Direction = '1'  # 卖
            CombOffsetFlag = '4'  # 平昨
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__b_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)

        volume = self.__position_b_buy_today - dict_args['position_b_buy_today']  # B今买需要减去的量
        if volume > 0:
            Direction = '1'  # 卖
            CombOffsetFlag = '3'  # 平今
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__b_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)

        volume = self.__position_b_sell_yesterday - dict_args['position_b_sell_yesterday']  # B昨卖需要减去的量
        if volume > 0:
            Direction = '0'  # 买
            CombOffsetFlag = '4'  # 平昨
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__b_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)

        volume = self.__position_b_sell_today - dict_args['position_b_sell_today']  # B今卖需要减去的量
        if volume > 0:
            Direction = '0'  # 买
            CombOffsetFlag = '3'  # 平今
            CombHedgeFlag = '1'  # 投机
            InstrumentID = self.__b_instrument_id  # 合约代码
            TradingDay = self.__MdApi_TradingDay
            self.set_list_position_detail_accessory(InstrumentID=InstrumentID,
                                                    Direction=Direction,
                                                    CombOffsetFlag=CombOffsetFlag,
                                                    CombHedgeFlag=CombHedgeFlag,
                                                    Volume=volume,
                                                    TradingDay=TradingDay)
        self.update_position_of_position_detail_for_trade()  # 遍历持仓明细列表，更新持仓量

    # 模拟Order、Trade结构体，作为更新持仓明细
    def set_list_position_detail_accessory(self, InstrumentID, Direction, CombOffsetFlag, CombHedgeFlag, Volume, TradingDay):
        order = {
            'InstrumentID': InstrumentID,
            'Direction': Direction,
            'CombOffsetFlag': CombOffsetFlag,
            'CombHedgeFlag': CombHedgeFlag,
            'VolumeTraded': Volume,
            'VolumeTradedBatch': Volume,
            'TradingDay': TradingDay}
        trade = {
            'InstrumentID': InstrumentID,
            'Direction': Direction,
            'OffsetFlag': CombOffsetFlag,
            'HedgeFlag': CombHedgeFlag,
            'Volume': Volume,
            'TradingDay': TradingDay}
        # print(">>> Strategy.set_list_position_detail_accessory() len(self.__list_position_detail_for_order) =", len(self.__list_position_detail_for_order), self.__list_position_detail_for_order)
        self.update_list_position_detail_for_order(order)
        # print(">>> Strategy.set_list_position_detail_accessory() len(self.__list_position_detail_for_order) =", len(self.__list_position_detail_for_order), self.__list_position_detail_for_order)
        self.update_list_position_detail_for_trade_set_position(trade)  # 该方法不更新统计类指标
        # print(">>> Strategy.set_list_position_detail_accessory() len(self.__list_position_detail_for_trade) =", len(self.__list_position_detail_for_trade), "self.__list_position_detail_for_trade =", self.__list_position_detail_for_trade)

    # 设置统计指标的值，包含dict内键值和对应的strategy对象的属性值赋值
    def set_statistics(self, dict_args):
        self.__a_order_times = dict_args['a_order_count']
        self.__b_order_times = dict_args['b_order_count']
        self.__a_traded_lots = dict_args['a_traded_count']
        self.__b_traded_lots = dict_args['b_traded_count']
        self.__total_traded_lots = dict_args['total_traded_count']
        self.__a_traded_amount = dict_args['a_traded_amount']
        self.__b_traded_amount = dict_args['b_traded_amount']
        self.__total_traded_amount = dict_args['total_traded_amount']
        self.__a_commission = dict_args['a_commission_count']
        self.__b_commission = dict_args['b_commission_count']
        self.__total_commission = dict_args['commission']
        self.__a_trade_rate = dict_args['a_trade_rate']
        self.__b_trade_rate = dict_args['b_trade_rate']
        self.__a_profit_close = dict_args['a_profit_close']
        self.__b_profit_close = dict_args['b_profit_close']
        self.__profit_close = dict_args['profit_close']
        self.__profit_position = dict_args['profit_position']
        self.__profit = dict_args['profit']
        self.__a_action_count = dict_args['a_action_count']
        self.__b_action_count = dict_args['b_action_count']

        # data_main = self.get_statistics()
        # data_main['strategy_id'] = self.__strategy_id  # dict结构体中加入strategy_id
        # dict_msg = {
        #     'DataFlag': 'strategy_statistics',
        #     'UserId': self.__user_id,
        #     'DataMain': data_main  # 最新策略统计
        # }
        # # print(">>> Strategy.set_statistics() user_id =", self.__user_id, 'data_flag = strategy_statistics', 'data_msg =', dict_msg)
        # self.__user.get_Queue_user().put(dict_msg)  # 进程通信：user->main，发送最新策略持仓

    # 计算持仓盈亏
    def count_profit_position(self):
        self.__profit_position = 0
        if self.__a_tick is not None and self.__b_tick is not None:
            for trade in self.__list_position_detail_for_trade:
                # A买持仓
                if trade['InstrumentID'] == self.__a_instrument_id and trade['Direction'] == '0':
                    trade['ProfitPosition'] = (self.__a_tick['LastPrice'] - trade['Price']) * self.__a_instrument_multiple * trade['Volume']
                    self.__profit_position += trade['ProfitPosition']
                # A卖持仓
                elif trade['InstrumentID'] == self.__a_instrument_id and trade['Direction'] == '1':
                    trade['ProfitPosition'] = (trade['Price'] - self.__a_tick['LastPrice']) * self.__a_instrument_multiple * trade['Volume']
                    self.__profit_position += trade['ProfitPosition']
                # B买持仓
                elif trade['InstrumentID'] == self.__b_instrument_id and trade['Direction'] == '0':
                    trade['ProfitPosition'] = (self.__b_tick['LastPrice'] - trade['Price']) * self.__b_instrument_multiple * trade['Volume']
                    self.__profit_position += trade['ProfitPosition']
                # B卖持仓
                elif trade['InstrumentID'] == self.__b_instrument_id and trade['Direction'] == '1':
                    trade['ProfitPosition'] = (trade['Price'] - self.__b_tick['LastPrice']) * self.__b_instrument_multiple * trade['Volume']
                    self.__profit_position += trade['ProfitPosition']
        # else:
        #     print(">>> Strategy.count_profit_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "tick为空")
        # print(">>> Strategy.count_profit_position() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "self.__profit_position =", self.__profit_position)
        return self.__profit_position

    def get_statistics(self):
        dict_statistics = {
            'user_id': self.__user_id,
            'strategy_id': self.__strategy_id,
            'a_order_count': self.__a_order_times,  # A委托次数
            'b_order_count': self.__b_order_times,  # B委托次数
            'a_traded_count': self.__a_traded_lots,  # A成交量
            'b_traded_count': self.__b_traded_lots,  # B成交量
            'total_traded_count': self.__a_traded_lots + self.__b_traded_lots,  # 所有成交量
            'a_traded_amount': self.__a_traded_amount,  # A成交金额
            'b_traded_amount': self.__b_traded_amount,  # B成交金额
            'total_traded_amount': self.__total_traded_amount,  # 总成交量
            'a_commission_count': self.__a_commission + self.__a_commission_order,  # A手续费
            'b_commission_count': self.__b_commission + self.__b_commission_order,  # B手续费
            'commission': self.__total_commission,  # 总手续费
            'a_trade_rate': self.__a_trade_rate,  # A成交概率(成交手数/报单手数)
            'b_trade_rate': self.__b_trade_rate,  # B成交概率(成交手数/报单手数)
            'a_profit_close': self.__a_profit_close,  # A平仓盈亏
            'b_profit_close': self.__b_profit_close,  # B平仓盈亏
            'profit_close': self.__profit_close,  # 平仓盈亏
            'profit_position': self.count_profit_position(),  # 持仓盈亏
            'profit': self.__profit,  # 净盈亏
            'a_action_count': self.__a_action_count,  # A撤单次数
            'b_action_count': self.__b_action_count,  # B撤单次数
            'a_action_count_strategy': self.__a_action_count_strategy,  # A撤单次数
            'b_action_count_strategy': self.__b_action_count_strategy,  # B撤单次数
            'current_margin': self.update_current_margin()  # 占用保证金
        }
        return dict_statistics

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

    # 生成报单引用，从左到右，第1位为识别符，第2到第10位为递增，第11到第12位为策略编号
    def add_order_ref(self):
        order_ref_part1 = '1'
        s0 = '000000000'
        s1 = str(self.__user.add_order_ref_part2())
        order_ref_part2 = s0[:len(s0)-len(s1)] + s1
        order_ref_part3 = self.__strategy_id
        order_ref_total = (order_ref_part1 + order_ref_part2 + order_ref_part3).encode()
        return order_ref_total

    # 从user类的list_QryOrder中选出本策略的list_QryOrder
    def get_list_QryOrder(self):
        if len(self.__user.get_list_QryOrder()) > 0:
            for i in self.__user.get_list_QryOrder():
                print(">>> Strategy.get_list_QryOrder() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "i =", i)
                if i['StrategyID'] == self.__strategy_id:  # 策略id相同
                    self.__list_QryOrder.append(i)
        print(">>> Strategy.get_list_QryOrder() user_id =", self.__user_id, "strategy_id =", self.__strategy_id,
              "len(self.__list_QryOrder) =", len(self.__list_QryOrder))
        return self.__list_QryOrder

    # 从user类的list_QryTrade中选出本策略的list_QryTrade
    def get_list_QryTrade(self):
        print(">>> Strategy.get_list_QryTrade() user_id =", self.__user_id,
              "len(self.__user.get_list_QryTrade()) =", len(self.__user.get_list_QryTrade()))
        if len(self.__user.get_list_QryTrade()) > 0:
            for i in self.__user.get_list_QryTrade():
                if i['StrategyID'] == self.__strategy_id:  # 策略id相同
                    self.__list_QryTrade.append(i)
        print(">>> Strategy.get_list_QryTrade() user_id =", self.__user_id, "strategy_id =", self.__strategy_id,
              "len(self.__list_QryTrade) =", len(self.__list_QryTrade))
        return self.__list_QryTrade

    # 回调函数：行情推送
    def OnRtnDepthMarketData(self, tick):
        # self.signal_handle_tick.emit(tick)  # 触发信号
        """ 行情推送
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
            self.__b_tick = copy.deepcopy(tick)
            self.update_profit_position(self.__b_tick)  # 更新持仓盈亏
            # print(self.__user_id + self.__strategy_id, "B合约：", self.__b_tick)
        # 过滤出A合约的tick
        elif tick['InstrumentID'] == self.__list_instrument_id[0]:
            self.__a_tick = copy.deepcopy(tick)
            self.update_profit_position(self.__b_tick)  # 更新持仓盈亏
            # print(self.__user_id + self.__strategy_id, "A合约：", self.__a_tick)

        # 计算市场盘口价差、量
        if self.__a_tick is None or self.__b_tick is None:
            return
        self.__spread_long = self.__a_tick['BidPrice1'] - self.__b_tick['AskPrice1']
        self.__spread_long_volume = min(self.__a_tick['BidVolume1'], self.__b_tick['AskVolume1'])
        self.__spread_short = self.__a_tick['AskPrice1'] - self.__b_tick['BidPrice1']
        self.__spread_short_volume = min(self.__a_tick['AskVolume1'], self.__b_tick['BidVolume1'])

        # 没有下单任务执行中，进入选择下单算法
        if not self.__trade_tasking:
            self.select_order_algorithm(self.__order_algorithm)
        # 有下单任务执行中，跟踪交易任务
        elif self.__trade_tasking:
            dict_args = {'flag': 'tick', 'tick': tick}
            self.trade_task(dict_args)

        # 刷新界面价差
        self.spread_to_ui()
        """
        if tick is None:
            return

        self.slot_handle_tick(tick)  # 转到行情处理

    @QtCore.pyqtSlot(dict)
    def slot_handle_tick(self, tick):
        """ 行情推送 """
        # print(">>> Strategy.OnRtnDepthMarketData() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "tick=", tick)

            # 策略初始化未完成，跳过
        # if self.__init_finished is False:
            # print("Strategy.OnRtnDepthMarketData() user_id=", self.__user_id, "strategy_id=", self.__strategy_id, "策略初始化未完成")
            # return
        # # CTPManager初始化未完成，跳过
        # if self.__user.get_CTPManager().get_init_finished() is False:
        #     return

        # 过滤出B合约的tick
        if tick['InstrumentID'] == self.__b_instrument_id:
            self.__b_tick = copy.deepcopy(tick)
            # self.update_profit_position(self.__b_tick)  # 更新持仓盈亏
            # print(self.__user_id + self.__strategy_id, "B合约：", self.__b_tick)
        # 过滤出A合约的tick
        elif tick['InstrumentID'] == self.__a_instrument_id:
            self.__a_tick = copy.deepcopy(tick)
            # self.update_profit_position(self.__b_tick)  # 更新持仓盈亏
            # print(self.__user_id + self.__strategy_id, "A合约：", self.__a_tick)

        # 计算市场盘口价差、量
        if self.__a_tick is not None and self.__b_tick is not None:
            self.__spread_long = self.__a_tick['BidPrice1'] - self.__b_tick['AskPrice1']
            self.__spread_long_volume = min(self.__a_tick['BidVolume1'], self.__b_tick['AskVolume1'])
            self.__spread_short = self.__a_tick['AskPrice1'] - self.__b_tick['BidPrice1']
            self.__spread_short_volume = min(self.__a_tick['AskVolume1'], self.__b_tick['BidVolume1'])

        # 没有下单任务执行中，进入选择下单算法
        # if not self.__trade_tasking:
        #     self.select_order_algorithm(self.__order_algorithm)
        # 有下单任务执行中，跟踪交易任务
        # elif self.__trade_tasking:
        #     dict_args = {'flag': 'tick', 'tick': tick}
        #     self.trade_task(dict_args)

        # 窗口创建未完成
        # if self.__user.get_CTPManager().get_ClientMain().get_init_UI_finished() is False:
        #     return
        # 没有显示窗口
        # if self.__user.get_CTPManager().get_ClientMain().get_showEvent() is False:
        #     return

        # 刷新界面行情
        # self.spread_to_ui()

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
        # self.trade_task(dict_args)  # 转到交易任务处理

    def OnRspOrderAction(self, InputOrderAction, RspInfo, RequestID, IsLast):
        """报单操作请求响应:撤单操作响应"""
        if Utils.Strategy_print:
            print('Strategy.OnRspOrderAction()', 'OrderRef:', InputOrderAction['OrderRef'], 'InputOrderAction:', InputOrderAction, 'RspInfo:', RspInfo, 'RequestID:', RequestID, 'IsLast:', IsLast)
        dict_args = {'flag': 'OnRspOrderAction',
                     'InputOrderAction': InputOrderAction,
                     'RspInfo': RspInfo,
                     'RequestID': RequestID,
                     'IsLast': IsLast}
        # self.trade_task(dict_args)  # 转到交易任务处理

    def OnRtnOrder(self, Order):
        # Order = copy.deepcopy(Order_input)  # 深度拷贝
        """报单回报"""
        # print(">>> Strategy.OnRtnOrder() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "Order =", Order)
        if Utils.Strategy_print:
            print('Strategy.OnRtnOrder()', 'OrderRef:', Order['OrderRef'], 'Order', Order)

        # 添加字段，本次成交量'VolumeTradedBatch'
        Order = self.add_VolumeTradedBatch(Order)

        # 更新持仓明细列表
        self.update_list_position_detail_for_order(Order)

        # 更新持仓变量
        # self.update_position_for_OnRtnOrder(Order)
        # self.update_position_of_position_detail_for_order()  # 遍历持仓明细更新持仓变量

        series_order = Series(Order)
        self.__df_OnRtnOrder = DataFrame.append(self.__df_OnRtnOrder, other=series_order, ignore_index=True)

        # 统计order指标
        # self.statistics(order=Order)

        # 更新统计指标
        self.statistics_for_order(Order)

        # 统计中金所部分品种申报费：IF\IH\IC
        self.count_commission_order(Order)

        # 更新界面
        # self.signal_update_strategy.emit(self)

        # self.update_list_order_process(order_new)  # 更新挂单列表
        # self.update_position(order_new)  # 更新持仓变量
        # self.update_task_status()  # 更新交易执行任务状态
        # dict_args = {'flag': 'OnRtnOrder', 'Order': Order}
        # self.trade_task(dict_args)  # 转到交易任务处理
        # self.statistics_for_order(Order)  # 统计
        #   # 更新界面

    def OnRtnTrade(self, Trade):
        # Trade = copy.deepcopy(trade_input)  # 形参深度拷贝到方法局部变量，目的是修改局部变量值不会影响到形参
        """成交回报"""
        if Utils.Strategy_print:
            print('Strategy.OnRtnTrade()', 'OrderRef:', Trade['OrderRef'], 'Trade', Trade)
        # self.__queue_OnRtnTrade.put(Trade)  # 放入队列
        # 检查，当前策略的Trade记录
        # 所有trade回调保存到DataFrame格式变量
        series_order = Series(Trade)
        self.__df_OnRtnTrade = DataFrame.append(self.__df_OnRtnTrade, other=series_order, ignore_index=True)

        # 更新统计指标
        self.statistics_for_trade(Trade)

        # 修改持仓的OnRtnTrade过滤：更新持仓量、更新持仓明细、更新占用保证金
        if self.__filter_OnRtnTrade:
            # print("Strategy.OnRtnTrade() self.__filter_date =", self.__filter_date, "self.__filter_time =", self.__filter_time)
            # print("Strategy.OnRtnTrade() Trade['TradeDate'] =", Trade['TradeDate'], "Trade['TradeTime'] =", Trade['TradeTime'])
            if Trade['TradeDate'] < self.__filter_date \
                    or (Trade['TradeDate'] == self.__filter_date and Trade['TradeTime'] < self.__filter_time):
                print("Strategy.OnRtnTrade() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "时间过滤，跳过持仓量统计")
                return

        # 更新持仓列表
        self.update_list_position_detail_for_trade(Trade)

        # 更新持仓变量
        self.update_position_for_OnRtnTrade(Trade)
        # self.update_position_of_position_detail_for_trade()  # 遍历持仓明细更新持仓变量

        # 更新界面
        # self.signal_update_strategy.emit(self)
        # self.update_position(Trade)  # 更新持仓量变量
        # self.update_task_status()  # 更新任务状态
        # dict_args = {'flag': 'OnRtnTrade', 'Trade': Trade}
        # self.trade_task(dict_args)  # 转到交易任务处理
        # self.statistics_for_trade(Trade)  # 交易数据统计
        # self.update_list_position_detail_for_trade(Trade)  # 更新持仓明细列表
        # self.signal_update_strategy_position.emit(self)  # 更新界面持仓

    def OnErrRtnOrderAction(self, OrderAction, RspInfo):
        """ 报单操作错误回报 """
        if Utils.Strategy_print:
            print('Strategy.OnErrRtnOrderAction()', 'OrderRef:', OrderAction['OrderRef'], 'OrderAction:', OrderAction, 'RspInfo:', RspInfo)
        dict_args = {'flag': 'OnErrRtnOrderAction', 'OrderAction': OrderAction, 'RspInfo': RspInfo}
        # self.trade_task(dict_args)  # 转到交易任务处理

    def OnErrRtnOrderInsert(self, InputOrder, RspInfo):
        """报单录入错误回报"""
        if Utils.Strategy_print:
            print('Strategy.OnErrRtnOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo)
        dict_args = {'flag': 'OnErrRtnOrderInsert',
                     'InputOrder': InputOrder,
                     'RspInfo': RspInfo}
        # self.trade_task(dict_args)  # 转到交易任务处理

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
        if self.__a_tick is not None or self.__b_tick is not None:
            return

        # 策略开关为关则直接跳出，不执行开平仓逻辑判断，依次为：策略开关、单个期货账户开关（user）、总开关（trader）
        if self.__strategy_on_off == 0 or self.__user.get_on_off() == 0 or self.__user.get_CTPManager().get_on_off() == 0:
            print("Strategy.order_algorithm_one() 策略开关状态", self.__strategy_on_off, self.__user.get_on_off(), self.__user.get_CTPManager().get_on_off())
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
            self.__instrument_a_tick_after_tasking = self.__a_tick
            self.__instrument_b_tick_after_tasking = self.__b_tick
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
                                          'LimitPrice': self.__a_tick['BidPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__b_tick['AskPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # self.trade_task(self.__a_order_insert_args)  # 执行下单任务
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
            self.__instrument_a_tick_after_tasking = self.__a_tick
            self.__instrument_b_tick_after_tasking = self.__b_tick
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
                                          'LimitPrice': self.__a_tick['AskPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__b_tick['BidPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # self.trade_task(self.__a_order_insert_args)  # 执行下单任务
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
            self.__instrument_a_tick_after_tasking = self.__a_tick
            self.__instrument_b_tick_after_tasking = self.__b_tick
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
                                          'LimitPrice': self.__a_tick['BidPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__b_tick['AskPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # self.trade_task(self.__a_order_insert_args)  # 执行下单任务
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
            self.__instrument_a_tick_after_tasking = self.__a_tick
            self.__instrument_b_tick_after_tasking = self.__b_tick
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
                                          'LimitPrice': self.__a_tick['AskPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__b_tick['BidPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # self.trade_task(self.__a_order_insert_args)  # 执行下单任务
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
            # 交易任务由服务端进行，客户端不做交易任务的操作
            """交易任务开始入口"""
            if Utils.Strategy_print:
                print('Strategy.trade_task() A合约报单，OrderRef=', dict_args['OrderRef'], '报单参数：', dict_args)
            # self.__user.get_trade().OrderInsert(dict_args)  # A合约报单
        # 报单录入请求响应
        elif dict_args['flag'] == 'OnRspOrderInsert':
            if Utils.Strategy_print:
                print("Strategy.trade_task() 报单录入请求响应，dict_args['flag'] == 'OnRspOrderInsert'")
            pass
        # 报单操作请求响应
        elif dict_args['flag'] == 'OnRspOrderAction':
            if Utils.Strategy_print:
                print("Strategy.trade_task() 报单操作请求响应，dict_args['flag'] == 'OnRspOrderAction'")
            pass
        # 报单回报
        elif dict_args['flag'] == 'OnRtnOrder':
            # 交易任务由服务端进行，客户端不做交易任务的操作
            """
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
                    LimitPrice = self.__b_tick['AskPrice1']  # B报单价格，找市场最新对手价
                elif dict_args['Order']['Direction'] == '1':
                    LimitPrice = self.__b_tick['BidPrice1']
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
            """
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
            # 交易任务由服务端进行，客户端不做交易任务的操作
            """当交易任务进行中时，判断是否需要撤单"""
            """
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
            """

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
        # if order['OrderStatus'] in ['0', '1']:  # 全部成交、部分成交还在队列中
        #     # 原始报单量为1手，本次成交量就是1手
        #     if order['VolumeTotalOriginal'] == 1:
        #         order['VolumeTradedBatch'] = 1
        #     elif order['VolumeTotalOriginal'] > 1:
        #         for i in self.__list_order_process:
        #             if i['OrderRef'] == order['OrderRef']:  # 在列表中找到相同的OrderRef记录
        #                 order['VolumeTradedBatch'] = order['VolumeTraded'] - i['VolumeTraded']  # 本次成交量
        #                 break
        # else:  # 非（全部成交、部分成交还在队列中）
        #     order['VolumeTradedBatch'] = 0
        # return order
        if order['OrderStatus'] == '0':  # 订单状态：全部成交
            order['VolumeTradedBatch'] = order['VolumeTotalOriginal']
        elif order['OrderStatus'] == '1':  # 订单状态：部分成交还在队列中
            found_flag = False  # 找到的标志位，初始值false
            for i_order in self.__list_position_detail_for_order:
                if order['OrderRef'] == i_order['OrderRef']:
                    found_flag = True
                    order['VolumeTradedBatch'] = order['VolumeTraded'] - i_order['VolumeTraded']
                    break
            if not found_flag:
                order['VolumeTradedBatch'] = order['VolumeTraded']
        elif order['OrderStatus'] in ['2', '3', '4', '5', 'a', 'b', 'c']:  # 订单状态：部分成交不在队列中
            order['VolumeTradedBatch'] = 0
        else:
            print("Strategy.add_VolumeTradedBatch() user_id =", self.__user_id, "strategy_id =", self.__strategy_id, "订单状态：异常，order =", order)

        return order

    # 添加字段"成交价"，order结构中加入字段Price
    def add_Price(self, trade):
        pass

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

    # 将order和trade记录保存到本地
    def save_df_order_trade(self):
        order_file_path = "data/order_" + self.__user_id + "_" + self.__strategy_id + '.csv'
        trade_file_path = "data/trade_" + self.__user_id + "_" + self.__strategy_id + '.csv'
        print(">>> PyCTP_Trade.save_df_order_trade() order_file_path =", order_file_path)
        print(">>> PyCTP_Trade.save_df_order_trade() trade_file_path =", trade_file_path)
        self.__df_OnRtnOrder.to_csv(order_file_path)
        self.__df_OnRtnTrade.to_csv(trade_file_path)


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
