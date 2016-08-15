# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""

import os
import time
import DBManager


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


# 打印交易员登录、交易员登录
def print_select_admin_trader():
    print('===========================')
    print('|请输入您的操作编号')
    print('|【1】管理员登录')
    print('|【2】交易员登录')
    print('|【q】退出')
    print('===========================')


def print_select_trader_user_manager():
    print('===========================')
    print('|请输入您的操作编号')
    print('|【1】交易员管理')
    print('|【2】期货账户管理')
    print('|【q】退出')
    print('===========================')


# 打印管理员管理菜单，管理员权限
def print_trader_manager():
    print('===========================')
    print('|请输入您的操作编号')
    print('|【1】查看交易员')
    print('|【2】增加交易员')
    print('|【3】删除交易员')
    print('|【4】修改交易员')
    print('|【q】退出')
    print('===========================')


# 打印交易员管理菜单，管理员权限
def print_user_manager():
    print('===========================')
    print('|请输入您的操作编号')
    print('|【1】查看期货账户')
    print('|【2】增加期货账户')
    print('|【3】删除期货账户')
    print('|【4】修改期货账户')
    print('|【q】退出')
    print('===========================')


# 打印交易员一般操作菜单，非管理员权限
def print_trader_menu():
    print('===========================')
    print('|请输入您的操作编号')
    print('|【1】查看所有期货账户')
    print('|【2】账户查询')
    print('|【3】持仓查询')
    print('|【4】报单查询')
    print('|【5】成交查询')
    print('|【6】报单')
    print('|【7】撤单')
    print('|【8】订阅行情')
    print('|【9】退订行情')
    print('|【10】创建交易策略')
    print('|【q】退出')
    print('===========================')


# 人机交互
def gui():
    from PyCTP_Market import PyCTP_Market_API
    import MultiUserTradeSys

    # MultiUserTradeSys.DBM = DBManager.DBManger()  # 在主程序之前已经创建了DBManager.DBManger()
    while True:
        print_select_admin_trader()
        v = input()

        if v == '1':  # 管理员登录
            print("请输入管理员账号")
            v_admin_id = input()
            print("请输入管理员密码")
            v_password = input()
            if not MultiUserTradeSys.DBM.check_admin(v_admin_id, v_password):
                continue
            time.sleep(0.5)

            while True:
                print_select_trader_user_manager()
                v = input()
                if v == '1':  # 进入交易员管理
                    while True:
                        print_trader_manager()
                        v = input()
                        if v == '1':  # 查看交易员
                            print("请输入要查看的交易员ID，查看所有请直接回车")
                            v = input()
                            print(MultiUserTradeSys.DBM.get_trader(v))
                            time.sleep(0.5)
                        elif v == '2':  # 创建交易员
                            print("请输入交易员信息：{'trader_id': 'xxx', 'trader_name': 'xxx', 'password': 'xxx', 'is_active': '1'}")
                            try:
                                v = eval(input())  # 控制台输入的格式str转换为dict
                                MultiUserTradeSys.DBM.create_trader(v)
                            except SyntaxError as e:
                                print("输入错误，请重新输入，错误信息：", e)
                            time.sleep(0.5)
                        elif v == '3':  # 删除交易员
                            print("请输入交易员账号")
                            v = input()
                            MultiUserTradeSys.DBM.delete_trader(v)
                            time.sleep(0.5)
                        elif v == '4':  # 修改交易员
                            print("请输入交易员信息：{'trader_id': 'xxx', 'trader_name': 'xxx', 'password': 'xxx', 'is_active': '1'}")
                            v = eval(input())  # 控制台输入的格式str转换为dict
                            MultiUserTradeSys.DBM.update_trader(v)
                            time.sleep(0.5)
                        elif v == 'q':  # 退出
                            break
                        else:
                            print("输入错误，请重新输入")
                            time.sleep(0.5)
                elif v == '2':  # 进入期货账户管理
                    while True:
                        print_user_manager()
                        v = input()
                        if v == '1':  # 查看期货账户
                            print("请输入要查看的期货账号，查看所有请直接回车")
                            v = input()
                            print(MultiUserTradeSys.DBM.get_user(v))
                            time.sleep(0.5)
                        elif v == '2':  # 创建期货账户
                            print(
                                "请输入期货账户信息：{'trader_id': 'xxx', 'user_id': 'xxx', 'user_name': 'xxx', 'password': 'xxx', 'front_address': 'xxx'}")
                            try:
                                v = eval(input())  # 控制台输入的格式str转换为dict
                                MultiUserTradeSys.DBM.create_user(v)
                            except SyntaxError as e:
                                print("输入错误，请重新输入，错误信息：", e)
                            time.sleep(0.5)
                        elif v == '3':  # 删除期货账户
                            print("请输入期货账号")
                            v = input()
                            MultiUserTradeSys.DBM.delete_user(v)
                            time.sleep(0.5)
                        elif v == '4':  # 修改期货账户
                            print(
                                "请输入期货账户信息：{'trader_id': 'xxx', 'user_id': 'xxx', 'user_name': 'xxx', 'password': 'xxx', 'front_address': 'xxx'}")
                            try:
                                v = eval(input())  # 控制台输入的格式str转换为dict
                                MultiUserTradeSys.DBM.update_user(v)
                            except SyntaxError as e:
                                print("输入错误，请重新输入，错误信息：", e)
                            time.sleep(0.5)
                        elif v == 'q':  # 退出
                            break
                        else:
                            print("输入错误，请重新输入")
                            time.sleep(0.5)
                elif v == 'q':  # 退出
                    break
                else:
                    print("输入错误，请重新输入")
                    time.sleep(0.5)
        elif v == '2':  # 交易员登录
            # 验证交易员账号密码
            print("请输入交易员账号")
            v_trader_id = input()
            print("请输入交易员密码")
            v_password = input()
            if not MultiUserTradeSys.DBM.check_trader(v_trader_id, v_password):
                continue
            time.sleep(0.5)
            # 将交易员登录日志信息写入到数据库集合TraderLoginLog
            MultiUserTradeSys.DBM.update_trader_login_status(v_trader_id)
            while True:
                print_trader_menu()  # 打印交易员操作菜单，非管理员权限
                v = input()
                if v == '1':  # 查看交易员名下的所有期货账户
                    # MultiUserTradeSys.DBM.get_user_id(trader)  # 传入参数为Trader类的实例
                    pass
                elif v == '2':  # 账户查询
                    pass
                elif v == '3':  # 持仓查询
                    pass
                elif v == '4':  # 报单查询
                    pass
                elif v == '5':  # 成交查询
                    pass
                elif v == '6':  # 报单
                    pass
                elif v == '7':  # 撤单
                    pass
                elif v == '8':  # 订阅行情
                    pass
                elif v == '9':  # 退订行情
                    pass
                elif v == '10':  # 创建交易策略
                    pass
                elif v == 'q':  # 退出
                    break
                else:
                    print("输入错误，请重新输入")
                    time.sleep(0.5)
        elif v == 'q':  # 退出
            break
        else:
            print("输入错误，请重新输入")
            time.sleep(0.5)

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


# 流文件路劲管理
def make_dirs(path):
    is_exists = os.path.exists(path)  # 判断路劲是否存在，存在True，不存在False
    if not is_exists:
        # print("make_dirs()文件路劲不存在，新创建，", path)
        os.makedirs(path)
        return True
    else:
        # print("make_dirs()文件路劲已存在，不用创建，", path)
        return False

