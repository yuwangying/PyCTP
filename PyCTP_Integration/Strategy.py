# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


from PyCTP_Trade import PyCTP_Trader_API
from PyCTP_Market import PyCTP_Market_API
from OrderAlgorithm import OrderAlgorithm


class Strategy:
    # class Strategy功能:接收行情，接收Json数据，触发交易信号，将交易任务交给OrderAlgorithm
    # 形参{'trader_id': '1601', 'user_id': '800658', 'strategy_id': '01', 'order_algorithm':'01', 'list_instrument_id': ['cu1611', 'cu1610']}
    def __init__(self, dict_arguments, user):
        self.__trader_id = dict_arguments['trader_id']
        self.__user_id = dict_arguments['user_id']
        self.__strategy_id = dict_arguments['strategy_id']
        self.__order_algorithm = OrderAlgorithm(dict_arguments, user)
        self.__list_instrument_id = dict_arguments['list_instrument_id']
        self.__user = user  # 期货账户实例
        self.__instrument_a_tick = None  # A合约tick（第一腿）
        self.__instrument_b_tick = None  # B合约tick（第二腿）
        self.__spread_long = None  # 市场多头价差：A合约买一价 - B合约买一价
        self.__spread_long_volume = None  # 市场多头价差盘口挂单量min(A合约买一量 - B合约买一量)
        self.__spread_short = None  # 市场空头价差：A合约卖一价 - B合约卖一价
        self.__spread_short_volume = None  # 市场空头价差盘口挂单量：min(A合约买一量 - B合约买一量)
        self.__spread = None  # 市场最新价价差

    # 行情推送回调函数
    def get_tick(self, tick):
        # 过滤出B合约的tick
        if tick['InstrumentID'] == self.__list_instrument_id[1]:
            self.__instrument_b_tick = tick
        # 过滤出A合约的tick
        elif tick['InstrumentID'] == self.__list_instrument_id[0]:
            self.__instrument_a_tick = tick

    # 下单算法1：A合约以对手价发单，B合约以对手价发单
    def order_algorithm_one(self):
        # 计算市场价差
        if self.__instrument_a_tick is not None and self.__instrument_b_tick is not None:
            self.__spread_long = self.__instrument_a_tick['BidPrice1'] - self.__instrument_b_tick['BidPrice1']
            self.__spread_long_volume = min(
                self.__instrument_a_tick['BidVolume1'] - self.__instrument_b_tick['BidVolume1'])
            self.__spread_short = self.__instrument_a_tick['AskPrice1'] - self.__instrument_b_tick['AskPrice1']
            self.__spread_short_volume = min(
                self.__instrument_a_tick['AskVolume1'] - self.__instrument_b_tick['AskVolume1'])

    # 下单算法2：A合约以最新成交价发单，B合约以对手价发单
    def order_algorithm_two(self):
        pass

    # 下单算法3：A合约以挂单价发单，B合约以对手价发单
    def order_algorithm_three(self):
        pass

