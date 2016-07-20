# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


from Trade import PyCTP_Trader, PyCTP_Trader_API
from Market import PyCTP_Market, PyCTP_Market_API


class Strategy:
    def __init__(self):
        print('新建Strategy类的实例')

    @staticmethod
    def strategy_1(len_ma1=10, len_ma2=20):
        print('strategy_1被调用，参数:', len_ma1, len_ma2)

    def strategy_2(self, len_ma1=10, len_ma2=20):
        print('strategy_2被调用，参数：', len_ma1, len_ma2)