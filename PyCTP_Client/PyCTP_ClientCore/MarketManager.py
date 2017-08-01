# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 13:50 2016
@author: YuWangying
"""

import time
import os
import copy
from PyQt4.QtCore import QObject
from PyQt4 import QtCore
from PyCTP_Market import PyCTP_Market_API
import Utils
# import sys
# import threading
# import chardet
# import pandas as pd
# from pandas import Series, DataFrame


class MarketManager:
    # 已经订阅行情的合约列表，类型为list，全局变量，类外可取
    list_instrument_subscribed = []

    # 初始化时创建一个行情API连接，多账户交易系统只需要一个行情API
    # def __init__(self, front_address, broker_id, user_id='', password=''):
    def __init__(self, dict_args):
        print('process_id =', os.getpid(), ', MarketManager.__init__() dict_arguments =', dict_args)
        # 多账户系统中，只需要创建一个行情API
        front_address = dict_args['frontaddress']
        broker_id = dict_args['brokerid']
        user_id = dict_args['userid']
        password = dict_args['password']
        s_tmp = (front_address[6:]).encode()
        n_position = s_tmp.index(b':')
        s_part1 = (s_tmp[:n_position])
        s_part2 = (s_tmp[n_position+1:])
        s_path = b'conn/md/' + s_part1 + b'_' + s_part2 + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__market = PyCTP_Market_API.CreateFtdcMdApi(s_path)
        self.__market.set_MarketManager(self)
        # self.__market.set_strategy(strategy)
        self.__broker_id = broker_id.encode()
        self.__front_address = front_address.encode()
        self.__user_id = user_id.encode()
        self.__password = password.encode()
        # 连接行情前置
        self.__result_market_connect = Utils.code_transform(self.__market.Connect(self.__front_address))
        if self.__result_market_connect == 0:
            print('MarketManager.__init__() 连接行情前置成功，broker_id =', broker_id)
        else:
            print('MarketManager.__init__() 连接行情前置失败,broker_id =', broker_id, '返回值：', self.__result_market_connect)
            self.__init_finished = False  # 初始化失败
        # 登录行情账号
        self.__result_market_login = Utils.code_transform(self.__market.Login(self.__broker_id, self.__user_id, self.__password))
        if self.__result_market_login == 0:
            print('MarketManager.__init__() 登录行情账号成功，broker_id =', broker_id)
        else:
            print('MarketManager.__init__() 登录行情账号失败，broker_id =', broker_id, '返回值：', self.__result_market_login)
            self.__init_finished = False  # 初始化失败

        # 已经订阅行情的合约列表，为每一个合约创建一个字典，键名为instrument_id，键值为list，list元素为user_id+strategy_id
        # [{'cu1608': ['80065801', '80067501']}, {'cu1609': ['80065801', '80067501']}]
        self.__list_instrument_subscribed_detail = list()
        # 界面groupBox订阅行情详情列表
        # ['cu1705', 'cu1706']
        self.__list_instrument_subscribed_detail_group_box = list()

        self.__TradingDay = self.__market.get_TradingDay().decode()
        print("MarketManager.__init__() 行情端口交易日：", self.__TradingDay)
        self.__init_finished = True  # 初始化成功

    def get_TradingDay(self):
        return self.__TradingDay

    def get_result_market_connect(self):
        return self.__result_market_connect

    def get_result_market_login(self):
        return self.__result_market_login

    def get_init_finished(self):
        return self.__init_finished

    # 获取__market
    def get_market(self):
        return self.__market

    # user初始化strategy、strategy增删都要调用该方法
    def set_dict_strategy(self, dict_strategy):
        self.__dict_strategy = dict_strategy

    def set_User(self, obj_user):
        self.__user = obj_user

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

        if len(list_instrument_id_to_sub) > 0:
            time.sleep(1.0)
            # print(">>> MarketManager.sub_market() list_instrument_id_to_sub =", list_instrument_id_to_sub)
            for i in range(len(list_instrument_id_to_sub)):
                if isinstance(list_instrument_id_to_sub[i], str):
                    list_instrument_id_to_sub[i] = list_instrument_id_to_sub[i].encode()
            # print(">>> MarketManager.sub_market() list_instrument_id_to_sub =", list_instrument_id_to_sub)

            print('MarketManager.sub_market() 请求订阅行情', Utils.code_transform(self.__market.SubMarketData(list_instrument_id_to_sub)))
            MarketManager.list_instrument_subscribed.extend(list_instrument_id_to_sub)
        print('MarketManager.sub_market() 已订阅行情详情', self.__list_instrument_subscribed_detail)

    # 退订行情，策略退订某一合约行情的时候需考虑是否有其他账户策略正在订阅此合约的行情
    def un_sub_market(self, list_instrument_id, user_id, strategy_id):
        # list_instrument_id_to_un_sub = copy.deepcopy(list_instrument_id)  # 保存将要退订的合约列表
        list_instrument_id_to_un_sub = []  # 保存将要退订的合约列表
        # 遍历将要退订的合约列表
        for instrument_id in list_instrument_id:
            # 遍历已订阅的合约列表
            for instrument_id_subscribed in self.__list_instrument_subscribed_detail:  # instrument_id_subscribed是{b'cu1609': '80065801'}
                # 找到已经订阅的合约，将对应的订阅者（user_id+strategy_id）删除
                # if not isinstance(instrument_id, bytes):
                #     instrument_id = instrument_id.encode()
                if instrument_id in instrument_id_subscribed:
                    if (user_id + strategy_id) in instrument_id_subscribed[instrument_id]:
                        pass
                    else:
                        print("MarketManager.un_sub_market() 退订者身份错误", (user_id + strategy_id))
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
            for i in range(len(list_instrument_id_to_un_sub)):
                if isinstance(list_instrument_id_to_un_sub[i], str):
                    list_instrument_id_to_un_sub[i] = list_instrument_id_to_un_sub[i].encode()
            print('MarketManager.un_sub_market() 请求退订行情', list_instrument_id_to_un_sub, Utils.code_transform(self.__market.UnSubMarketData(list_instrument_id_to_un_sub)))
            # MarketManager.list_instrument_subscribed.remove(list_instrument_id_to_un_sub)
            MarketManager.list_instrument_subscribed = list(set(MarketManager.list_instrument_subscribed) - set(list_instrument_id_to_un_sub))
        print('MarketManager.sub_market() 订阅行情详情', self.__list_instrument_subscribed_detail)

    # 界面groupBox订阅行情函数
    def group_box_sub_market(self, list_instrument_id):
        list_instrument_id_will_subscribe = []  # 将要订阅行情的合约列表
        for instrument_id in list_instrument_id:
            find_flag = False
            for i in self.__list_instrument_subscribed_detail_group_box:
                # 已经订阅的行情不需要再订阅
                if instrument_id == i:
                    find_flag = True
                    break
            if not find_flag:  # 已经订阅行情列表里不存在，则需要订阅，加入到将要订阅的行情列表
                list_instrument_id_will_subscribe.append(instrument_id)
        if len(list_instrument_id_will_subscribe) > 0:
            for i in range(len(list_instrument_id_will_subscribe)):
                list_instrument_id_will_subscribe[i] = list_instrument_id_will_subscribe[i].encode()
            print('MarketManager.sub_market() 订阅行情', Utils.code_transform(self.__market.SubMarketData(list_instrument_id_will_subscribe)))

        list_instrument_id_will_unsubscribe = []  # 将要退订行情的合约列表
        for instrument_id in self.__list_instrument_subscribed_detail_group_box:
            find_flag = False
            for i in list_instrument_id:
                if instrument_id == i:
                    find_flag = True
                    break
            if not find_flag:
                list_instrument_id_will_unsubscribe.append(instrument_id)
        if len(list_instrument_id_will_unsubscribe) > 0:
            for i in range(len(list_instrument_id_will_unsubscribe)):
                list_instrument_id_will_unsubscribe[i] = list_instrument_id_will_unsubscribe[i].encode()
            print('MarketManager.sub_market() 订阅行情', Utils.code_transform(self.__market.UnSubMarketData(list_instrument_id_will_subscribe)))

    # 登出行情账号，包含登出、断开连接、释放实例
    def un_connect(self):
        time.sleep(1.0)
        print('MarketManager.un_connect() 断开行情连接', self.__market.UnConnect())  # 包含断开连接和释放实例

    # 行情回调
    def OnRtnDepthMarketData(self, tick):
        # print(">>> MarketManager.OnRtnDepthMarketData() tick =", tick)
        instrument_id = tick['InstrumentID']
        for strategy_id in self.__dict_strategy:
            if instrument_id == self.__dict_strategy[strategy_id].get_a_instrument_id() or instrument_id == self.__dict_strategy[strategy_id].get_b_instrument_id():
                self.__dict_strategy[strategy_id].OnRtnDepthMarketData(tick)
        self.__user.OnRtnDepthMarketData(tick)


class MarketManagerForUi(QObject):
    signal_update_spread_ui = QtCore.pyqtSignal(list)  # 定义信号：价差行情发生变化将行情发送信号给界面

    # 已经订阅行情的合约列表，类型为list，全局变量，类外可取
    list_instrument_subscribed = []

    # 初始化时创建一个行情API连接，多账户交易系统只需要一个行情API
    # def __init__(self, front_address, broker_id, user_id='', password=''):
    def __init__(self, dict_args, parent=None):
        super(MarketManagerForUi, self).__init__(parent)
        print('process_id =', os.getpid(), ', MarketManagerForUi.__init__() dict_arguments =', dict_args)
        # 多账户系统中，只需要创建一个行情API
        front_address = dict_args['frontaddress']
        broker_id = dict_args['brokerid']
        user_id = dict_args['userid']
        password = dict_args['password']
        s_tmp = (front_address[6:]).encode()
        n_position = s_tmp.index(b':')
        s_part1 = (s_tmp[:n_position])
        s_part2 = (s_tmp[n_position + 1:])
        s_path = b'conn/md/' + s_part1 + b'_' + s_part2 + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__market = PyCTP_Market_API.CreateFtdcMdApi(s_path)
        self.__market.set_MarketManager(self)
        # self.__market.set_strategy(strategy)
        self.__broker_id = broker_id.encode()
        self.__front_address = front_address.encode()
        self.__user_id = user_id.encode()
        self.__password = password.encode()
        # 连接行情前置
        self.__result_market_connect = Utils.code_transform(self.__market.Connect(self.__front_address))
        if self.__result_market_connect == 0:
            print('MarketManagerForUi.__init__() 连接行情前置成功，broker_id =', broker_id)
        else:
            print('MarketManagerForUi.__init__() 连接行情前置失败,broker_id =', broker_id, '返回值：', self.__result_market_connect)
            self.__init_finished = False  # 初始化失败
        # 登录行情账号
        self.__result_market_login = Utils.code_transform(
            self.__market.Login(self.__broker_id, self.__user_id, self.__password))
        if self.__result_market_login == 0:
            print('MarketManagerForUi.__init__() 登录行情账号成功，broker_id =', broker_id)
        else:
            print('MarketManagerForUi.__init__() 登录行情账号失败，broker_id =', broker_id, '返回值：', self.__result_market_login)
            self.__init_finished = False  # 初始化失败

        # 已经订阅行情的合约列表，为每一个合约创建一个字典，键名为instrument_id，键值为list，list元素为user_id+strategy_id
        # [{'cu1608': ['80065801', '80067501']}, {'cu1609': ['80065801', '80067501']}]
        self.__list_instrument_subscribed_detail = list()
        # 界面groupBox订阅行情详情列表
        # ['cu1705', 'cu1706']
        self.__list_instrument_subscribed_detail_group_box = list()

        self.__TradingDay = self.__market.get_TradingDay().decode()
        print("MarketManagerForUi.__init__() 行情端口交易日：", self.__TradingDay)
        self.__init_finished = True  # 初始化成功
        self.__a_tick = None
        self.__b_tick = None
        self.__spread_long_last = 0.00001  # 最后一次保存的价差行情，初始值为一个不易出现的值
        self.__spread_short_last = 0.00001
        self.__last_list_market = [0, 0, 0, 0]  # 最后一次保存的价差行情[A买一, A卖一, B买一, B卖一]

    def get_TradingDay(self):
        return self.__TradingDay

    def get_result_market_connect(self):
        return self.__result_market_connect

    def get_result_market_login(self):
        return self.__result_market_login

    def get_init_finished(self):
        return self.__init_finished

    # 获取__market
    def get_market(self):
        return self.__market

    def set_QAccountWidget(self, obj):
        self.__QAccountWidget = obj

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
                    instrument_id_subscribed[instrument_id].append(user_id + strategy_id)
                    break
            # 没有订阅，则添加该订阅信息到已经订阅的合约列表
            if not bool_subscribed:
                self.__list_instrument_subscribed_detail.append({instrument_id: [user_id + strategy_id]})

        if len(list_instrument_id_to_sub) > 0:
            time.sleep(1.0)
            print('MarketManagerForUi.sub_market() 请求订阅行情', Utils.code_transform(self.__market.SubMarketData(list_instrument_id_to_sub)))
            MarketManagerForUi.list_instrument_subscribed.extend(list_instrument_id_to_sub)
        print('MarketManagerForUi.sub_market() 已订阅行情详情', self.__list_instrument_subscribed_detail)

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
                        print("MarketManagerForUi.un_sub_market() 退订者身份错误", (user_id + strategy_id))
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
            print('MarketManagerForUi.un_sub_market() 请求退订行情', list_instrument_id_to_un_sub,
                  Utils.code_transform(self.__market.UnSubMarketData(list_instrument_id_to_un_sub)))
            # MarketManagerForUi.list_instrument_subscribed.remove(list_instrument_id_to_un_sub)
            MarketManagerForUi.list_instrument_subscribed = list(
                set(MarketManagerForUi.list_instrument_subscribed) - set(list_instrument_id_to_un_sub))
        print('MarketManagerForUi.sub_market() 订阅行情详情', self.__list_instrument_subscribed_detail)

    # 界面groupBox订阅行情函数
    def group_box_sub_market(self, list_instrument_id):
        self.__a_instrument_id = list_instrument_id[0]
        self.__b_instrument_id = list_instrument_id[1]
        # print(">>> MarketManager.group_box_sub_market() self.__a_instrument_id =", self.__a_instrument_id, "self.__b_instrument_id =", self.__b_instrument_id)

        # 整理将要订阅的合约代码list
        list_instrument_id_will_subscribe = []  # 将要订阅行情的合约列表
        for instrument_id in list_instrument_id:
            find_flag = False
            for i in self.__list_instrument_subscribed_detail_group_box:
                # 已经订阅的行情不需要再订阅
                if instrument_id == i:
                    find_flag = True
                    break
            if not find_flag:  # 已经订阅行情列表里不存在，则需要订阅，加入到将要订阅的行情列表
                list_instrument_id_will_subscribe.append(instrument_id)

        # 订阅行情
        if len(list_instrument_id_will_subscribe) > 0:
            for i in range(len(list_instrument_id_will_subscribe)):
                # 添加将要订阅的合约代码到所有订阅行情列表中
                self.__list_instrument_subscribed_detail_group_box.append(list_instrument_id_will_subscribe[i])
                # 转换编码类型，MdApi接收b''类型
                list_instrument_id_will_subscribe[i] = list_instrument_id_will_subscribe[i].encode()
            print('MarketManagerForUi.group_box_sub_market() list_instrument_id_will_subscribe =', list_instrument_id_will_subscribe)
            print('MarketManagerForUi.group_box_sub_market() self.__market.SubMarketData() =',  Utils.code_transform(self.__market.SubMarketData(list_instrument_id_will_subscribe)))

        # 整理将要退订行情的合约代码list
        list_instrument_id_will_unsubscribe = []
        for instrument_id in self.__list_instrument_subscribed_detail_group_box:
            find_flag = False
            for i in list_instrument_id:
                if instrument_id == i:
                    find_flag = True
                    break
            if not find_flag:
                list_instrument_id_will_unsubscribe.append(instrument_id)

        # 退订行情
        if len(list_instrument_id_will_unsubscribe) > 0:
            time.sleep(1.0)
            for i in range(len(list_instrument_id_will_unsubscribe)):
                # 从所有订阅行情列表中删除退订的策略
                for instrument_id in self.__list_instrument_subscribed_detail_group_box:
                    if instrument_id == list_instrument_id_will_unsubscribe[i]:
                        self.__list_instrument_subscribed_detail_group_box.remove(instrument_id)
                        break
                # 转换编码类型，MdApi接收b''类型
                list_instrument_id_will_unsubscribe[i] = list_instrument_id_will_unsubscribe[i].encode()
            print('MarketManagerForUi.group_box_sub_market() list_instrument_id_will_unsubscribe =', list_instrument_id_will_unsubscribe)
            print('MarketManagerForUi.group_box_sub_market() self.__market.UnSubMarketData() =', Utils.code_transform(self.__market.UnSubMarketData(list_instrument_id_will_unsubscribe)))

        print('MarketManagerForUi.group_box_sub_market() 用户维护的所有订阅行情', self.__list_instrument_subscribed_detail_group_box)

    # 登出行情账号，包含登出、断开连接、释放实例
    def un_connect(self):
        time.sleep(1.0)
        print('MarketManagerForUi.un_connect() 断开行情连接', self.__market.UnConnect())  # 包含断开连接和释放实例

    # 行情回调
    def OnRtnDepthMarketData(self, tick):
        # print('MarketManagerForUi.OnRtnDepthMarketData() DepthMarketData =', DepthMarketData)  # 包含断开连接和释放实例
        if self.__a_instrument_id == tick['InstrumentID']:
            self.__a_tick = copy.deepcopy(tick)
        elif self.__b_instrument_id == tick['InstrumentID']:
            self.__b_tick = copy.deepcopy(tick)
        else:
            print('MarketManagerForUi.OnRtnDepthMarketData() 想要订阅的行情为', self.__a_instrument_id, self.__b_instrument_id, "实际接收行情为", tick['InstrumentID'])
        if self.__a_tick is None or self.__b_tick is None:
            return

        # # 下单算法1的行情：将价差行情基础结果传给界面
        # self.__spread_long = round((self.__a_tick['BidPrice1'] - self.__b_tick['AskPrice1']), 2)
        # # self.__spread_long_volume = min(self.__a_tick['BidVolume1'], self.__b_tick['AskVolume1'])
        # self.__spread_short = round((self.__a_tick['AskPrice1'] - self.__b_tick['BidPrice1']), 2)
        # # self.__spread_short_volume = min(self.__a_tick['AskVolume1'], self.__b_tick['BidVolume1'])
        # # print("MarketManagerForUi.OnRtnDepthMarketData() ", self.__a_instrument_id, "-", self.__b_instrument_id,"多头价差:", self.__spread_long, "空头价差:", self.__spread_short)
        # # 行情发生变化，发送信号给界面，刷新界面
        # if self.__spread_long != self.__spread_long_last or self.__spread_short != self.__spread_short_last:
        #     self.signal_update_spread_ui.emit([self.__spread_long, self.__spread_short])
        # # 保存最后一次价差行情
        # self.__spread_long_last = self.__spread_long
        # self.__spread_short_last = self.__spread_short

        # 下单算法2的行情：将市场行情传给界面
        list_market = [self.__a_tick['BidPrice1'], self.__a_tick['AskPrice1'], self.__b_tick['BidPrice1'], self.__b_tick['AskPrice1']]
        if self.__last_list_market != list_market:  # 行情有变化，触发信号：更新界面行情
            self.signal_update_spread_ui.emit(list_market)

        self.__last_list_market = list_market







