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
    print('|【e】查询交易所信息')
    print('|【s】查询合约信息')
    print('|【u】查询账户信息')
    print('|【t】查询账户资金')
    print('|【h】查询账户持仓')
    print('|【o】查询委托记录')
    print('|【d】查询交易记录')
    print('|【i】报单')
    print('|【a】撤单')
    print('|【l】保存文件本地')
    print('|【b】退出')
    print('===========================')


# 核对输入参数
# def check_arguments(input_params):
#     if input_params[0] != '{' or input_params[-1] != '}':
#         print('输入参数错误')
#         return False
#     try:
#         input_params = eval(input_params)
#     except SyntaxError as e:
#         print('except:', e)
#         print('输入参数错误')
#         continue
