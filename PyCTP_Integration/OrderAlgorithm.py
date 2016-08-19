# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""

import os
import time
import DBManager


class OrderAlgorithm:
    # 下单算法类
    def __init__(self, dict_arguments, user):
        self.__list_order_ref = None
        self.__execute_flag = dict_arguments['order_algorithm']
        self.__user = user
        pass

    def set_execute_flag(self, execute_flag):
        self.__execute_flag = execute_flag

    def execute(self):
        if self.__execute_flag == '1':
            self.order_algorithm_one()
        elif self.__execute_flag == '2':
            self.order_algorithm_two()

    def order_algorithm_one(self):
        pass

    def order_algorithm_two(self):
        pass
