# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


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
    print('===========================')
    print('|请输入您的操作编号:')
    print('|【1】查询交易所')
    print('|【2】查询合约')
    print('|【3】查询合约状态')
    print('|【4】查询账户信息')
    print('|【5】查询账户资金')
    print('|【6】查询账户持仓汇总')
    print('|【7】查询账户持仓明细')
    print('|【8】查询委托记录')
    print('|【9】查询交易记录')
    print('|【10】报单')
    print('|【11】撤单')
    print('|【s】保存文件本地')
    print('|【q】退出')
    print('===========================')

