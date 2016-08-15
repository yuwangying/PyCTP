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
import pandas as pd
from pandas import Series, DataFrame
import FunctionLog
from pymongo import MongoClient
import DBManager
from PyCTP_Trade import PyCTP_Trader_API
from PyCTP_Market import PyCTP_Market_API
import Utils
import User
from MarketManager import MarketManager


DBM = DBManager.DBManger()


# 新增operator_id下面的某个期货账户
def add_user(operator_id, BrokerID, FrontAddress, user_id, password):
    print('add_user(): operator_id=', operator_id, 'BrokerID=', BrokerID, 'user_id=', user_id)
    # 24小时测试环境-交易、行情前置：180.168.146.187:10030、180.168.146.187:10031
    # 标准CTP仿真环境-交易、行情前置：180.168.146.187:10000、180.168.146.187:10010
    # 国贸期货CTP-交易、行情前置：tcp://101.95.8.190:41205、tcp://101.95.8.190:41213
    # trade_front_address = b'tcp://180.168.146.187:10030'
    add_user_arguments = {'operator_id': operator_id,
                       'BrokerID': BrokerID,
                       'UserID': user_id,
                       'Password': password,
                       'FrontAddress': FrontAddress}
    # 新增期货账户，创建TradeApi实例
    return User.User(operator_id, BrokerID, FrontAddress, user_id, password)


# 删除operator_id下面的某个期货账户
# 参数说明： user=class User实例名称
def del_user(user, operator_id, BrokerID, FrontAddress, user_id):
    print('del_user(): operator_id=', operator_id, 'BrokerID=', BrokerID, 'user_id=', user_id)
    del_user_arguments = {'operator_id': operator_id,
                          'BrokerID': BrokerID,
                          'UserID': user_id,
                          'FrontAddress': FrontAddress}
    # 删除期货账户，释放TradeApi实例
    user.UnConnect()
    # 操作MongoDB，删除Operator下面的user_id（期货账户）


# 交易员登录验证
def trader_login(trader_id, password):
    return DBM.check_trader(trader_id, password)


# 管理员登录
def admin_login(admin_id, password):
    return DBM.check_admin(admin_id, password)


def __main__():
    # 多账户系统中，创建一个行情API
    market = MarketManager(front_address=b'tcp://180.168.146.187:10031', broker_id=b'9999')
    # market.sub_market([b'ni1609'], b'800658', b'01')
    print("交易日：", PyCTP_Market_API.TradingDay)

    # 进入人机交互模式
    Utils.gui()

if __name__ == '__main__':
    __main__()

