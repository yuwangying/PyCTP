# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""

import os
import time
import DBManager

# 打印控制标志
b_print = True

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
    time.sleep(0.5)
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
    time.sleep(0.5)
    print('===========================')
    print('|请输入您的操作编号')
    print('|【1】管理员登录')
    print('|【2】交易员登录')
    print('|【q】退出')
    print('===========================')


def print_select_trader_user_manager():
    time.sleep(0.5)
    print('===========================')
    print('|请输入您的操作编号')
    print('|【1】交易员管理')
    print('|【2】期货账户管理')
    print('|【q】退出')
    print('===========================')


# 打印管理员管理菜单，管理员权限
def print_trader_manager():
    time.sleep(0.5)
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
    time.sleep(0.5)
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
    time.sleep(0.5)
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
    print('|【11】修改交易策略')
    print('|【12】删除交易策略')
    print('|【13】查询交易策略')
    print('|【q】退出')
    print('===========================')


# 判断期货账号是否属于交易员名下
def trader_include_user(ctp_manager, trader_id, user_id):
    if ctp_manager.get_mdb().get_user(user_id) is None:
        print("trader_include_user()数据库中不存在该期货账号", user_id)
        return None
    for i in ctp_manager.get_list_user():
        # print("i.get_user_id().decode() == v", i.get_user_id().decode(), v)
        if i.get_user_id().decode() == user_id and i.get_trader_id().decode() == trader_id:
            return i

# 人机交互
def gui(ctp_manager):
    from PyCTP_Market import PyCTP_Market_API
    import MultiUserTradeSys

    # ctp_manager.get_mdb() = DBManager.DBManger()  # 在主程序之前已经创建了DBManager.DBManger()
    while True:
        print_select_admin_trader()
        v = input()

        if v == '1':  # 管理员登录
            print("请输入管理员账号")
            v_admin_id = input()
            print("请输入管理员密码")
            v_password = input()
            if not ctp_manager.get_mdb().check_admin(v_admin_id, v_password):
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
                            print(ctp_manager.get_mdb().get_trader(v))
                            time.sleep(0.5)
                        elif v == '2':  # 创建交易员
                            print("请输入交易员信息：{'trader_id': 'xxx', 'trader_name': 'xxx', 'password': 'xxx', 'is_active': '1'}")
                            try:
                                v = eval(input())  # 控制台输入的格式str转换为dict
                                ctp_manager.get_mdb().create_trader(v)
                            except SyntaxError as e:
                                print("输入错误，请重新输入，错误信息：", e)
                            time.sleep(0.5)
                        elif v == '3':  # 删除交易员
                            print("请输入交易员账号")
                            v = input()
                            ctp_manager.get_mdb().delete_trader(v)
                            time.sleep(0.5)
                        elif v == '4':  # 修改交易员
                            print("请输入交易员信息：{'trader_id': 'xxx', 'trader_name': 'xxx', 'password': 'xxx', 'is_active': '1'}")
                            v = eval(input())  # 控制台输入的格式str转换为dict
                            ctp_manager.get_mdb().update_trader(v)
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
                            print(ctp_manager.get_mdb().get_user(v))
                            time.sleep(0.5)
                        elif v == '2':  # 创建期货账户
                            print(
                                "请输入期货账户信息：{'trader_id': 'xxx', 'user_id': 'xxx', 'user_name': 'xxx', 'password': 'xxx', 'front_address': 'xxx'}")
                            try:
                                v = eval(input())  # 控制台输入的格式str转换为dict
                                ctp_manager.get_mdb().create_user(v)
                            except SyntaxError as e:
                                print("输入错误，请重新输入，错误信息：", e)
                            time.sleep(0.5)
                        elif v == '3':  # 删除期货账户
                            print("请输入期货账号")
                            v = input()
                            ctp_manager.get_mdb().delete_user(v)
                            time.sleep(0.5)
                        elif v == '4':  # 修改期货账户
                            print(
                                "请输入期货账户信息：{'trader_id': 'xxx', 'user_id': 'xxx', 'user_name': 'xxx', 'password': 'xxx', 'front_address': 'xxx'}")
                            try:
                                v = eval(input())  # 控制台输入的格式str转换为dict
                                ctp_manager.get_mdb().update_user(v)
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
            input_trader_id = input()
            print("请输入交易员密码")
            v_password = input()
            if not ctp_manager.get_mdb().check_trader(input_trader_id, v_password):
                continue
            time.sleep(0.5)
            # 将交易员登录日志信息写入到数据库集合TraderLoginLog
            ctp_manager.get_mdb().update_trader_login_status(input_trader_id)
            while True:
                print_trader_menu()  # 打印交易员操作菜单，非管理员权限
                v = input()
                if v == '1':  # 查看交易员名下的所有期货账户
                    print(ctp_manager.get_mdb().get_user_id(input_trader_id))  # 传入参数为Trader类的实例
                    pass
                elif v == '2':  # 账户查询
                    print("请输入期货账号")
                    input_user_id = input()
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is not None:
                        print(obj_user.get_trade().QryTradingAccount())
                        continue
                elif v == '3':  # 持仓查询
                    print("请输入期货账号")
                    input_user_id = input()
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is not None:
                        print(obj_user.get_trade().QryInvestorPosition())
                        continue
                elif v == '4':  # 报单查询
                    print("请输入期货账号")
                    input_user_id = input()
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is not None:
                        print(code_transform(obj_user.get_trade().QryOrder()))
                        continue
                elif v == '5':  # 成交查询
                    print("请输入期货账号")
                    input_user_id = input()
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is not None:
                        print(code_transform(obj_user.get_trade().QryTrade()))
                elif v == '6':  # 报单
                    print("请输入期货账号")
                    input_user_id = input()
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is not None:
                        input_example = {'InstrumentID': b'cu1609',
                                         'CombOffsetFlag': b'0',
                                         'Direction': b'0',
                                         'VolumeTotalOriginal': 2,
                                         'LimitPrice': 39000.00,
                                         'OrderRef': b'101',
                                         'CombHedgeFlag': b'1'}
                        print("请输入报单参数，例：", input_example)
                        try:
                            input_order_insert = eval(input())  # 控制台输入的格式str转换为dict
                            obj_user.get_trade().OrderInsert(input_order_insert)
                        except SyntaxError as e:
                            print("输入错误，请重新输入，错误信息：", e)
                elif v == '7':  # 撤单
                    print("请输入期货账号")
                    input_user_id = input()
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is not None:
                        input_example = {'ExchangeID': b'SHFE',
                                         'OrderRef': b'101',
                                         'OrderSysID': b'          46'}
                        print("请输入撤单参数，例：", input_example)
                        try:
                            input_order_insert = eval(input())  # 控制台输入的格式str转换为dict
                            obj_user.get_trade().OrderAction(input_order_insert)
                        except SyntaxError as e:
                            print("输入错误，请重新输入，错误信息：", e)
                elif v == '8':  # 订阅行情
                    input_example = {'合约列表': [b'cu1610', b'cu1611'], 'user_id': '800658', 'strategy_id': '01'}
                    print("请输入订阅行情参数参数，例：", input_example)
                    input_arguments = input()
                    try:
                        print("input_arguments=", input_arguments)
                        # print("input_arguments['合约列表']=", input_arguments['合约列表'])
                        input_arguments = eval(input_arguments)  # 控制台输入的格式str转换为dict
                    except SyntaxError as e:
                        print("输入错误，请重新输入，错误信息：", e)
                        continue
                    input_list_instrument_id = input_arguments['合约列表']
                    input_user_id = input_arguments['user_id']
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is None:
                        continue
                    input_user_id = input_arguments['user_id']
                    input_strategy_id = input_arguments['strategy_id']
                    ctp_manager.get_md().sub_market(input_list_instrument_id, input_user_id, input_strategy_id)
                elif v == '9':  # 退订行情
                    input_example = {'合约列表': [b'cu1610', b'cu1611'], 'user_id': '800658', 'strategy_id': '01'}
                    print("请输入退订行情参数，例：", input_example)
                    input_arguments = input()
                    try:
                        print("input_arguments=", input_arguments)
                        # print("input_arguments['合约列表']=", input_arguments['合约列表'])
                        input_arguments = eval(input_arguments)  # 控制台输入的格式str转换为dict
                    except SyntaxError as e:
                        print("输入错误，请重新输入，错误信息：", e)
                        continue
                    input_list_instrument_id = input_arguments['合约列表']
                    input_user_id = input_arguments['user_id']
                    obj_user = trader_include_user(ctp_manager, input_trader_id, input_user_id)
                    if obj_user is None:
                        continue
                    input_user_id = input_arguments['user_id']
                    input_strategy_id = input_arguments['strategy_id']
                    ctp_manager.get_md().un_sub_market(input_list_instrument_id, input_user_id, input_strategy_id)
                elif v == '10':  # 创建交易策略
                    input_example = {'trader_id': '1601',
                                     'user_id': '800658',
                                     'strategy_id': '01',
                                     'order_algorithm': '01',
                                     'list_instrument_id': ['cu1611', 'cu1610']}
                    print("请输入创建策略的参数，例：", input_example)
                    input_arguments = input()
                    try:
                        input_arguments = eval(input_arguments)  # 控制台输入的格式str转换为dict
                    except SyntaxError as e:
                        print("输入错误，请重新输入，错误信息：", e)
                        continue
                    ctp_manager.create_strategy(input_arguments)
                    ctp_manager.get_mdb().create_strategy(input_arguments)
                elif v == '11':  # 修改交易策略
                    input_example = {'trader_id': '1601',
                                     'user_id': '800658',
                                     'strategy_id': '01',
                                     'order_algorithm': '01',
                                     'list_instrument_id': ['cu1611', 'cu1610']}
                    print("请输入修改策略的参数，例：", input_example)
                    input_arguments = input()
                    try:
                        input_arguments = eval(input_arguments)  # 控制台输入的格式str转换为dict
                    except SyntaxError as e:
                        print("输入错误，请重新输入，错误信息：", e)
                        continue
                elif v == '12':  # 删除交易策略
                    input_example = {'trader_id': '1601', 'user_id': '063802', 'strategy_id': '01'}
                    print("请输入删除策略的参数，例：", input_example)
                    input_arguments = input()
                    try:
                        input_arguments = eval(input_arguments)  # 控制台输入的格式str转换为dict
                    except SyntaxError as e:
                        print("输入错误，请重新输入，错误信息：", e)
                        continue
                    # 调用管理类实例中删除strategy的方法
                    ctp_manager.delete_strategy(input_arguments)
                    # 从数据库删除该策略记录
                    ctp_manager.get_mdb().delete_strategy(input_arguments['user_id'], input_arguments['strategy_id'])

                elif v == '13':  # 查询交易策略
                    input_example1 = {}  # 查询交易员名下所有的策略
                    input_example2 = {'user_id': '800658'}  # 查询交易员名下的指定期货账户的所有策略
                    input_example3 = {'user_id': '800658', 'strategy_id': '01'}  # 查询交易员名下指定期货账户指定交易策略
                    print("请输入查询策略的参数")
                    print("例：", input_example1, "查询交易员名下所有的策略")
                    print("例：", input_example2, "查询交易员名下指定期货账户的所有策略")
                    print("例：", input_example3, "查询交易员名下指定期货账户的指定交易策略")
                    input_arguments = input()
                    try:
                        input_arguments = eval(input_arguments)  # 控制台输入的格式str转换为dict
                    except SyntaxError as e:
                        print("输入错误，请重新输入，错误信息：", e)
                        continue
                    input_arguments['trader_id'] = input_trader_id
                    output_v = ctp_manager.get_mdb().get_strategy(input_arguments)
                    if not output_v:
                        print("不存在交易策略")
                    else:
                        print("策略数量=", len(output_v))
                        print(output_v)
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

