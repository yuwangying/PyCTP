# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 13:50 2016
@author: YuWangying
"""

import sys
import time
import os
import copy
import threading
import chardet
import pandas as pd
from pandas import Series, DataFrame
from PyCTP_Market import PyCTP_Market_API
import Utils


class MarketManager:
    # 已经订阅行情的合约列表，类型为list，全局变量，类外可取
    list_instrument_subscribed = []

    # 初始化时创建一个行情API连接，多账户交易系统只需要一个行情API
    def __init__(self, front_address, broker_id, user_id='', password=''):
        # 多账户系统中，只需要创建一个行情API
        s_tmp = (front_address[6:]).encode()
        n_position = s_tmp.index(b':')
        s_part1 = (s_tmp[:n_position])
        s_part2 = (s_tmp[n_position+1:])
        s_path = b'conn/md/' + s_part1 + b'_' + s_part2 + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__market = PyCTP_Market_API.CreateFtdcMdApi(s_path)
        # self.__market.set_strategy(strategy)
        self.__broker_id = broker_id.encode()
        self.__front_address = front_address.encode()
        self.__user_id = user_id.encode()
        self.__password = password.encode()
        print('===========================')
        print('连接行情前置', Utils.code_transform(self.__market.Connect(self.__front_address)))
        print('登陆行情账号', Utils.code_transform(self.__market.Login(self.__broker_id, self.__user_id, self.__password)))
        # 已经订阅行情的合约列表，为每一个合约创建一个字典，键名为instrument_id，键值为list，list元素为user_id+strategy_id
        # [{'cu1608': ['80065801', '80067501']}, {'cu1609': ['80065801', '80067501']}]
        self.__list_instrument_subscribed_detail = []

    # 获取__market
    def get_market(self):
        return self.__market

    # 订阅行情，过滤已经订阅过的行情
    def sub_market(self, list_instrument_id, user_id, strategy_id):
        list_instrument_id_to_sub = copy.deepcopy(list_instrument_id)  # 保存将要订阅的合约列表
        # 遍历将要订阅的合约列表
        for instrument_id in list_instrument_id:
            bool_subscribed = False  # 已经订阅设置为假
            # 遍历已经订阅的合约列表
            for instrument_id_subscribed in self.__list_instrument_subscribed_detail:  # instrument_id_subscribed是{b'cu1609': '80065801'}
                # 如果在已经订阅的合约中找到需要订阅的合约，则从将要订阅的合约列表list_instrument_id_to_sub中删除
                if instrument_id in instrument_id_subscribed:
                    list_instrument_id_to_sub.remove(instrument_id)
                    bool_subscribed = True  # 已经订阅设置为真
                    # 将合约的订阅者身份(user_id+strategy_id)添加到已经订阅的合约键值下面
                    instrument_id_subscribed[instrument_id].append(user_id+strategy_id)
                    break
            # 没有订阅，则添加该订阅信息到已经订阅的合约列表
            if not bool_subscribed:
                self.__list_instrument_subscribed_detail.append({instrument_id: [user_id+strategy_id]})

        print('===========================')
        if len(list_instrument_id_to_sub) > 0:
            time.sleep(1.0)
            print('MarketManager.sub_market()请求订阅行情', Utils.code_transform(self.__market.SubMarketData(list_instrument_id_to_sub)))
            MarketManager.list_instrument_subscribed.extend(list_instrument_id_to_sub)
        print('MarketManager.sub_market()订阅行情详情', self.__list_instrument_subscribed_detail)

    # 退订行情，策略退订某一合约行情的时候需考虑是否有其他账户策略正在订阅此合约的行情
    def un_sub_market(self, list_instrument_id, user_id, strategy_id):
        # list_instrument_id_to_un_sub = copy.deepcopy(list_instrument_id)  # 保存将要退订的合约列表
        list_instrument_id_to_un_sub = []  # 保存将要退订的合约列表
        # 遍历将要退订的合约列表
        for instrument_id in list_instrument_id:
            # 遍历已订阅的合约列表
            for instrument_id_subscribed in self.__list_instrument_subscribed_detail:  # instrument_id_subscribed是{b'cu1609': '80065801'}
                # 找到已经订阅的合约，将对应的订阅者（user_id+strategy_id）删除
                if not isinstance(instrument_id, bytes):
                    instrument_id = instrument_id.encode()
                if instrument_id in instrument_id_subscribed:
                    if (user_id + strategy_id) in instrument_id_subscribed[instrument_id]:
                        pass
                    else:
                        print("MarketManager.un_sub_market()退订者身份错误", (user_id + strategy_id))
                        return False
                    # 将合约的订阅者身份(user_id+strategy_id)从已经订阅的合约键值里删除
                    instrument_id_subscribed[instrument_id].remove(user_id + strategy_id)
                    # 如果订阅者为空，从已订阅列表中删除该键
                    if len(instrument_id_subscribed[instrument_id]) == 0:
                        self.__list_instrument_subscribed_detail.remove(instrument_id_subscribed)
                        list_instrument_id_to_un_sub.append(instrument_id)
                    break
        if len(list_instrument_id_to_un_sub) > 0:
            time.sleep(1.0)
            print('MarketManager.un_sub_market():请求退订行情', list_instrument_id_to_un_sub, Utils.code_transform(self.__market.UnSubMarketData(list_instrument_id_to_un_sub)))
            # MarketManager.list_instrument_subscribed.remove(list_instrument_id_to_un_sub)
            MarketManager.list_instrument_subscribed = list(set(MarketManager.list_instrument_subscribed) - set(list_instrument_id_to_un_sub))
        print('MarketManager.sub_market()订阅行情详情', self.__list_instrument_subscribed_detail)

    # 登出行情账号，包含登出、断开连接、释放实例
    def un_connect(self):
        time.sleep(1.0)
        print('un_connect():断开行情连接', self.__market.UnConnect())  # 包含断开连接和释放实例




