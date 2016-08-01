# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""

import time
import PyCTP_Market


# 对CTP_API返回的dict结构内部的元素编码从bytes转换为utf-8，该方法也适用于单个变量的格式转换
def code_transform(data):
    # 传入参数为list
    if isinstance(data, list):
        list_output = []
        for i_dict in data:
            if isinstance(i_dict, dict):  # k是个dict
                data_output = {}
                for j_key in i_dict:  # j是dict内部单个元素的key
                    data_output[j_key] = code_transform(i_dict[j_key])
                list_output.append(data_output)
        return list_output
    # 传入参数为dict
    elif isinstance(data, dict):
        data_output = {}
        for i in data:
            data_output[i] = code_transform(data[i])
        return data_output
    # 传入参数为单个变量
    elif isinstance(data, bytes):
        return data.decode('gbk')
    else:
        return data


# 打印主菜单
def print_menu():
    time.sleep(1.0)
    print('===========================')
    print('|请输入您的操作编号:')
    print('|【qe】查询交易所信息')
    print('|【qi】查询合约信息')
    print('|【qa】查询账户信息')
    print('|【qc】查询账户资金')
    print('|【qp】查询账户持仓')
    print('|【qo】查询委托记录')
    print('|【qt】查询交易记录')
    print('|【qm】查询行情')
    print('|【sm】订阅行情')
    print('|【i】报单')
    print('|【a】撤单')
    print('|【s】保存数据到本地')
    print('|【e】退出')
    print('===========================')


# 人机交互
def gui():
    while True:
        print_menu()
        input_var = input()

        if input_var == 's':
            PyCTP_Market.PyCTP_Market.df_data.to_csv('/data')
            pass
        else:
            # 输入错误重新输入
            print('input error, please input again\n')
            continue

'''
# 与MultiUserTradeSys独立
# 管理员类，用来管理operator
class Administrator:
    @staticmethod
    def add_operator(operator_name, operator_password, email=''):
        # 调用pymongoDB，进行insert操作

        # 不能重复添加operator

        pass

    @staticmethod
    def del_operator(operator_name, operator_password='', email=''):
        # 调用pymongoDB，进行remove操作
        pass
'''

