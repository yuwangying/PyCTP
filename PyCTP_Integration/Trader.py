# -*- coding: utf-8 -*-
"""
Created on 2016年8月12日21:49:19

@author: YuWanying
"""


from PyCTP_Trade import PyCTP_Trader_API
import Utils


# 交易员类
class Trader:
    def __init__(self, dict_argument):  # trader_id, trader_name, password, is_active):
        # print('创建Trader: operator_id=', operator_id, 'BrokerID=', BrokerID, 'user_id=', user_id)
        self.__trader_id = dict_argument['trader_id']
        self.__trader_name = dict_argument['trader_name']
        self.__password = dict_argument['password']
        self.__is_active = dict_argument['is_active']
        self.__list_user = list()  # 保存交易员名下的期货账户列表

    # 获取trader_id
    def get_trader_id(self):
        return self.__trader_id

    # 设置交易员密码
    def set_password(self, password):
        self.__password = password

    # 获取交易员密码
    def get_password(self):
        return self.__password

    # 设置交易员活跃状态
    def set_is_active(self, is_active):
        self.__is_active = is_active

    # 获取交易员活跃状态
    def get_is_active(self):
        return self.__is_active

    # 设置交易员名称
    def set_trader_name(self, trader_name):
        self.__trader_name = trader_name

    # 获取交易员名称
    def get_trader_name(self):
        return self.__trader_name

    # 设置交易员id
    def set_trader_id(self, trader_id):
        self.__trader_id = trader_id

    # 获取交易员id
    def get_trader_id(self):
        return self.__trader_id

