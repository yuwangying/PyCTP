# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 13:50 2016
@author: YuWangying
"""

import sys
import time
import os
import threading
import chardet
from PyQt4 import QtCore
import pandas as pd
from pandas import Series, DataFrame
from pymongo import MongoClient
from DBManager import DBManger
from PyCTP_Trade import PyCTP_Trader_API
from PyCTP_Market import PyCTP_Market_API
import Utils
from Trader import Trader
from User import User
from Strategy import Strategy
from MarketManager import MarketManager
from collections import namedtuple  # Socket所需package
import socket
import struct


class CTPManager(QtCore.QObject):
    signal_insert_row_table_widget = QtCore.pyqtSignal()  # 定义信号：调用ClientMain中的方法insert_row_table_widget
    signal_remove_row_table_widget = QtCore.pyqtSignal()  # 定义信号：调用ClientMain中的方法remove_row_table_widget
    signal_hide_new_strategy = QtCore.pyqtSignal()  # 隐藏创建策略的小弹窗

    def __init__(self, parent=None):
        super(CTPManager, self).__init__(parent)  # 显示调用父类初始化方法，使用其信号槽机制
        self.__DBManager = DBManger()  # 创建数据库连接
        self.__MarketManager = None  # 行情管理实例，MarketManager
        self.__trader = None  # 交易员实例
        self.__list_user = list()  # 期货账户（TD）实例list
        self.__list_strategy = list()  # 交易策略实例list
        self.__list_instrument_info = list()  # 期货合约信息
        self.__got_list_instrument_info = False  # 获得了期货合约信息
        self.__on_off = 0  # 交易员的交易开关，初始值为关
        self.__only_close = 0  # 交易员的只平，初始值为关
        self.__init_finished = False  # 初始化完成

    # 初始化
    def init(self):
        # 创建行情实例
        self.create_md(self.__ClientMain.get_listMarketInfo()[0])

        # 创建期货账户
        for i in self.__ClientMain.get_listUserInfo():
            self.create_user(i)

        # 创建策略
        print("CTPManager.init() self.__ClientMain.get_listStrategyInfo()=", self.__ClientMain.get_listStrategyInfo())
        for i in self.__ClientMain.get_listStrategyInfo():
            self.create_strategy(i)

    # 创建MD
    def create_md(self, dict_arguments):
        # dict_arguments = {'front_address': 'tcp://180.168.146.187:10010', 'broker_id': '9999'}
        # 创建行情管理实例MarketManager
        self.__MarketManager = MarketManager(dict_arguments['frontaddress'],
                                             dict_arguments['brokerid'],
                                             dict_arguments['userid'],
                                             dict_arguments['password']
                                             )
        print("CTPManager.create_md() 行情接口交易日", self.__MarketManager.get_market().GetTradingDay())  # 行情API中获取到的交易日
        self.__MarketManager.get_market().set_strategy(self.__list_strategy)  # 将策略列表设置为Market_API类的属性

    # 创建trader
    def create_trader(self, dict_arguments):
        self.__trader = Trader(dict_arguments)
        self.__trader_id = self.__trader.get_trader_id()

    # 创建user(期货账户)
    def create_user(self, dict_arguments):
        # 不允许重复创建期货账户实例
        if len(self.__list_user) > 0:
            for i in self.__list_user:
                if i.get_user_id() == dict_arguments['userid']:
                    print("MultiUserTraderSys.create_user()已经存在user_id为", dict_arguments['userid'], "的实例，不允许重复创建")
                    return False
        obj_User = User(dict_arguments)
        obj_User.set_DBManager(self.__DBManager)  # 将数据库管理类设置为user的属性
        obj_User.set_CTPManager(self)  # 将CTPManager类设置为user的属性
        obj_User.qry_instrument_info()  # 查询合约信息
        self.__list_user.append(obj_User)  # user类实例添加到列表存放
        print("CTPManager.create_user() 创建期货账户实例", dict_arguments)

    # 将strategy对象添加到user里
    def add_strategy_to_user(self, obj_strategy):
        for i in self.__list_user:
            if i.get_user_id() == obj_strategy.get_user_id():
                i.add_strategy()

    # 创建strategy
    def create_strategy(self, dict_arguments):
        # 不允许重复创建策略实例
        if len(self.__list_strategy) > 0:
            for i in self.__list_strategy:
                if i.get_strategy_id() == dict_arguments['strategy_id'] and i.get_user_id() == dict_arguments['user_id']:
                    print("CTPManager.create_strategy() 不能重复创建，已经存在的strategy_id=", dict_arguments['strategy_id'])
                    return False

        print("CTPManager.create_strategy() user_id=", dict_arguments['user_id'], "strategy_id=", dict_arguments['strategy_id'])
        for i in self.__list_user:
            if i.get_user_id().decode() == dict_arguments['user_id']:  # 找到策略所属的user实例
                obj_strategy = Strategy(dict_arguments, i, self.__DBManager)  # 创建策略实例，user实例和数据库连接实例设置为strategy的属性
                i.add_strategy(obj_strategy)               # 将策略实例添加到user的策略列表
                self.__list_strategy.append(obj_strategy)  # 将策略实例添加到CTP_Manager的策略列表

        # 订阅行情
        list_instrument_id = list()
        for i in dict_arguments['list_instrument_id']:
            list_instrument_id.append(i.encode())  # 将合约代码转码为二进制字符串
        self.__MarketManager.sub_market(list_instrument_id, dict_arguments['user_id'], dict_arguments['strategy_id'])

        # 判断内核是否初始化完成
        if self.__init_finished is False:
            # 最后一个策略实例初始化完成，将内核初始化完成标志设置为True，跳转到界面初始化或显示
            lastStrategyInfo = self.__ClientMain.get_listStrategyInfo()[-1]
            if len(lastStrategyInfo) > 0:
                if lastStrategyInfo['strategy_id'] == obj_strategy.get_strategy_id() and lastStrategyInfo['user_id'] == obj_strategy.get_user_id():
                    self.__init_finished = True  # CTPManager初始化完成，跳转到界面初始化或显示
                    self.__ClientMain.create_QAccountWidget()  # 创建窗口界面
            else:
                self.__init_finished = True  # CTPManager初始化完成，跳转到界面初始化或显示
                self.__ClientMain.create_QAccountWidget()  # 创建窗口界面
        elif self.__init_finished:  # 程序运行中、初始化已经完成，在界面策略列表框内添加一行
            print(">>> CTPManager.create_strategy() 程序运行中、初始化已经完成，在界面策略列表框内添加一行策略id为", dict_arguments['strategy_id'])
            self.signal_insert_row_table_widget.emit()  # 在界面策略列表中显示添加的策略
            self.signal_hide_new_strategy.emit()  # 隐藏创建策略的小弹窗

    # 删除strategy
    def delete_strategy(self, dict_arguments):
        print("CTPManager.delete_strategy() 删除策略对象", dict_arguments)

        # 将obj_strategy从CTPManager的self.__list_strategy中删除
        for i_strategy in self.__list_strategy:
            if i_strategy.get_user_id() == dict_arguments['user_id']:
                # 退订该策略的行情
                self.__MarketManager.un_sub_market(i_strategy.get_list_instrument_id(),
                                                   dict_arguments['user_id'],
                                                   dict_arguments['strategy_id'])
                self.__list_strategy.remove(i_strategy)
                print(">>> CTPManager.delete_strategy() 从CTPManager的策略列表中删除策略", dict_arguments)
                break

        # 将obj_strategy从user中的list_strategy中删除
        for i_user in self.__list_user:
            if i_user.get_user_id().decode() == dict_arguments['user_id']:
                for i_strategy in i_user.get_list_strategy():
                    if i_strategy.get_strategy_id() == dict_arguments['strategy_id']:
                        i_user.get_list_strategy().remove(i_strategy)
                        print(">>> CTPManager.delete_strategy() 从user的策略列表中删除策略", dict_arguments)
                        break

        # 内核删除策略成功，通知界面删除策略
        self.signal_remove_row_table_widget.emit()  # 在界面策略列表中删除策略

    # 创建数据库连接实例
    def create_DBManager(self):
        self.__DBManager = DBManger()

    # 获取数据库连接实例
    def get_mdb(self):
        return self.__DBManager

    # 获取行情实例
    def get_md(self):
        return self.__MarketManager

    # 获取trader对象的list
    def get_trader(self):
        return self.__trader

    # 获取user对象的list
    def get_list_user(self):
        return self.__list_user

    # 获取strategy对象的list
    def get_list_strategy(self):
        return self.__list_strategy

    # 设置CTPManager内核初始化完成
    def set_init_finished(self, bool_input):
        print(">>> CTPManager.set_init_finished() CTPManager内核初始化完成")
        self.__init_finished = bool_input

    # 获取CTPManager内核初始化状态
    def get_init_finished(self):
        return self.__init_finished

    # 从user对象列表里找到指定user_id的user对象
    def find_user(self, user_id):
        for i in self.__list_user:
            if i.get_user_id() == user_id:
                return i

    def set_ClientMain(self, obj_ClientMain):
        self.__ClientMain = obj_ClientMain

    def get_ClientMain(self):
        return self.__ClientMain

    # 所有策略的昨仓保存到一个list，从服务端查询获得
    def set_YesterdayPosition(self, listYesterdayPosition):
        self.__listYesterdayPosition = listYesterdayPosition

    def get_YesterdayPosition(self):
        return self.__listYesterdayPosition

    # 新增trader_id下面的某个期货账户
    def add_user(self, trader_id, broker_id, front_address, user_id, password):
        print('add_user(): trader_id=', trader_id, 'broker_id=', broker_id, 'user_id=', user_id)
        add_user_arguments = {'trader_id': trader_id,
                              'broker_id': broker_id,
                              'UserID': user_id,
                              'Password': password,
                              'front_address': front_address}
        # 新增期货账户，创建TradeApi实例
        return User(add_user_arguments)
    
    # 删除trader_id下面的某个期货账户
    # 参数说明： user=class User实例名称
    def del_user(self, user, trader_id, broker_id, front_address, user_id):
        print('del_user(): trader_id=', trader_id, 'broker_id=', broker_id, 'user_id=', user_id)
        del_user_arguments = {'trader_id': trader_id,
                              'broker_id': broker_id,
                              'UserID': user_id,
                              'front_address': front_address}
        # 删除期货账户，释放TradeApi实例
        user.UnConnect()
        # 操作MongoDB，删除Operator下面的user_id（期货账户）
    
    # 交易员登录验证
    def trader_login(self, trader_id, password):
        return self.__DBManager.check_trader(trader_id, password)

    # 设置交易员id
    def set_trader_id(self, str_TraderID):
        self.__TraderID = str_TraderID

    # 获得交易员id
    def get_trader_id(self):
        return self.__TraderID

    def set_trader_name(self, str_TraderName):
        self.__TraderName = str_TraderName

    def get_trader_name(self):
        return self.__TraderName

    # 设置客户端的交易开关，0关、1开
    def set_on_off(self, int_on_off):
        self.__on_off = int_on_off

    # 获取客户端的交易开关，0关、1开
    def get_on_off(self):
        return self.__on_off

    # 设置交易开关，0关、1开
    def set_only_close(self, int_only_close):
        self.__only_close = int_only_close

    # 获取交易开关，0关、1开
    def get_only_close(self):
        return self.__only_close

    # 设置“已经获取到合约信息的状态”
    def set_got_list_instrument_info(self, bool_status):
        self.__got_list_instrument_info = bool_status

    # 获取“已经获取到合约信息的状态”
    def get_got_list_instrument_info(self):
        return self.__got_list_instrument_info

    # 设置合约信息
    def set_instrument_info(self, input_list):
        self.__list_instrument_info = input_list
        self.__list_instrument_id = list()
        for i in self.__list_instrument_info:
            self.__list_instrument_id.append(i['InstrumentID'])

    # 获取合约信息
    def get_instrument_info(self):
        return self.__list_instrument_info

    # 获取期货合约代码列表
    def get_list_instrument_id(self):
        return self.__list_instrument_id



