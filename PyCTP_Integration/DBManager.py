# -*- coding: utf-8 -*-
"""
Created on 2016年8月3日09:54:47

@author: YuWanying
"""
from PyCTP_Market import PyCTP_Market_API
from pymongo import MongoClient
import datetime


class DBManger:
    def __init__(self):
        '''Create Mongodb Connection'''
        # client = MongoClient() #Default Connection
        self.__client = MongoClient('localhost', 27017)
        self.__db = self.__client.CTP
        self.__col_admin = self.__db.admin
        self.__col_trader = self.__db.trader
        self.__col_user = self.__db.user
        self.__col_trader_login_log = self.__db.trader_login_log
        # client = MongoClient('mongodb://localhost:27017/')

    '''验证管理员'''
    def check_admin(self, admin_id, password):
        if self.__col_admin.count({'admin_id': admin_id}) == 0:
            print("check_admin()不存在的管理员")
            return False
        if self.__col_admin.count({'admin_id': admin_id, 'password': password}) == 1:
            print("check_admin()验证管理员成功")
            return True
        else:
            print("check_admin()管理员密码错误")
            return False

    '''管理交易员'''
    # 创建交易员
    # 形参trader类型为 dict，{'trader_id': 'xxx', 'trader_name': 'xxxx', 'password': 'xxxx', 'is_active': '1'}
    def create_trader(self, trader):
        print("trader=", trader, type(trader))
        # print(self.__col_trader.find({"trader_id": trader['trader_id']}).count() )
        # print("trader['trader_id']=", trader['trader_id'])
        if self.__col_trader.count({"trader_id": trader['trader_id']}) > 0:
            print('create_trader()已存在该交易员', trader['trader_id'])
            return False
        elif self.__col_trader.count({"trader_id": trader['trader_id']}) == 0:
            trader['create_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            trader['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.__col_trader.insert_one(trader)
            print('create_trader()创建交易员', trader['trader_id'], '成功')
            return True

    # 删除交易员
    def delete_trader(self, trader_id):
        if self.__col_trader.count({"trader_id": trader_id}) == 0:
            print('create_trader()不存在交易员', trader_id)
            return False
        if self.__col_trader.count({"trader_id": trader_id}) == 1:
            d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.__col_trader.update_one({"trader_id": trader_id}, {"$set": {"is_active": "0", "update_time": d}})
            print('create_trader()删除交易员成功', trader_id)
            return True

    # 更新交易员
    def update_trader(self, trader):
        if self.__col_trader.count({"trader_id": trader['trader_id']}) == 0:
            print('create_trader()不存在交易员', trader['trader_id'])
            return False
        if self.__col_trader.count({"trader_id": trader['trader_id']}) == 1:
            trader['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # dict_trader = trader.pop('trader_id')
            self.__col_trader.update_one({"trader_id": trader['trader_id']}, {"$set": trader})
            print('create_trader()更新交易员成功', self.__col_trader.find_one({"trader_id": trader['trader_id']}))
            return True

    # 查找交易员(trader_id)，返回交易员信息，返回交易员信息列表，格式为list
    def get_trader(self, trader_id=''):
        # 形参trader_name为空时返回所有交易员
        list_trader = []
        if trader_id == '':
            for i in self.__col_trader.find({}):
                list_trader.append(i)
            # return self.__col_trader.find_one()
        # 形参trader_name不为空时，条件查找并返回交易员
        else:
            list_trader = [self.__col_trader.find_one({"trader_id": trader_id})]

        if len(list_trader) == 0:
            print("不存在交易员", list_trader)
            return None
        else:
            return list_trader

    # 验证交易员
    def check_trader(self, trader_id, password):
        if self.__col_trader.count({"trader_id": trader_id}) == 0:
            print("check_trader()不存在的交易员")
            return False
        if self.__col_trader.count({"trader_id": trader_id, "password": password}) == 1:
            print("check_trader()验证交易员成功")
            return True
        else:
            print("check_trader()交易员密码错误")
            return False

    '''管理期货账户'''
    # 创建期货账户,形参user类型为字典
    # {'trader_id': 'XXX', 'user_id': 'XXX', 'user_name': 'XXX', 'password': 'XXX', 'front_address': 'XXX'}
    def create_user(self, user):
        # 只能往已经存在的trader_id（交易员）中添加user_id（期货账户）
        number = self.__col_trader.count({'trader_id': user['trader_id']})
        if number != 1:
            print("create_user(),不存在该交易员", user['trader_id'])
            return False

        # 不允许重复添加user_id（期货账户）
        number = self.__col_user.count({'user_id': user['user_id']})
        if number == 1:
            print('create_user()已存在该期货账户', user['user_id'])
            return False
        elif number == 0:
            print('create_user()创建期货账户', user['user_id'], '成功')
            user['create_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.__col_user.insert_one(user)
            return True
        else:
            print('create_user()创建期货账户错误')

    # 删除期货账户
    def delete_user(self, user_id):
        if self.__col_user.count({"user_id": user_id}) == 0:
            print('create_user()不存在期货账户', user_id)
            return False
        if self.__col_user.count({"user_id": user_id}) == 1:
            print('create_user()删除期货账户成功', user_id)
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__col_user.update_one({"user_id": user_id}, {"$set": {"is_active": "0", "update_time": d}})

    # 更新期货账户
    def update_user(self, user):
        if self.__col_user.count({"user_id": user['user_id']}) == 0:
            print('create_user()不存在期货账户', user['user_id'])
            return False
        elif self.__col_user.count({"user_id": user['user_id']}) == 1:
            user['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.__col_user.update_one({"user_id": user['user_id']}, {"$set": user})
            print('create_user()更新期货账户成功', self.__col_user.find_one({"user_id": user['user_id']}))

    # 查找期货账户，返回期货账户信息
    def get_user(self, user_id=''):
        # 形参trader_name为空时返回所有交易员
        list_user = []
        if user_id == '':
            for i in self.__col_user.find({}):
                list_user.append(i)
        # 形参trader_name不为空时，条件查找并返回交易员
        else:
            list_user = [self.__col_user.find_one({"user_id": user_id})]

        if len(list_user) == 0:
            print("不存在期货账户", user_id)
            return None
        else:
            return list_user

    # 更新交易员login信息
    def update_trader_login_status(self, trader_id):
        trader_login_status = dict()
        trader_login_status['trader_id'] = trader_id
        trader_login_status['login_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("trader_login_status['login_time']=", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        trader_login_status['trading_day'] = PyCTP_Market_API.TradingDay.decode('utf-8')
        print("trader_login_status['trading_day']=", PyCTP_Market_API.TradingDay.decode('utf-8'))
        # 从交易员集合里查询是否存在该交易员
        number = self.__col_trader.count({'trader_id': trader_id})
        if number == 0:
            print("update_trader_login_status(),不存在该交易员", trader_id)
            return False
        # 交易员登录日志中已经存在该交易员记录，则修改日志信息
        elif number == 1:
            number2 = self.__col_trader_login_log.count({'trader_id': trader_id})
            # 交易员登录状态记录表里面不存在该交易员，则创建文档
            if number2 == 0:
                self.__col_trader_login_log.insert_one(trader_login_status)
            # 交易员登录状态记录表里面已存在该交易员，则修改文档
            elif number2 == 1:
                self.__col_trader_login_log.update_one({'trader_id': trader_id}, {"$set": trader_login_status})
            return True

    '''交易员查询名下所有期货账户信息，非管理员权限'''
    def get_user_id(self, trader_id):
        list_user = list()
        for i in self.__col_user.find({'trader_id': trader_id}):
            list_user.append(i)
        return list_user


if __name__ == '__main__':
    db = DBManger()
    # trader = {"tradername": "ypf", "trader_id": "800901", "password": "119991", "is_active": "1"}
    # db.create_trader({"tradername": "ypf", "trader_id": "800901", "password": "111111", "is_active": "1"})
    # db.delete_trader(trader)
    # db.update_trader(trader)
    # print(db.SearchTraderByName())
    db.check_admin('ywy', '123')  # 验证管理员
    db.check_trader('1601', '123456')  # 验证交易员
    trader1 = {"trader_id": "1601", "trader_name": "余汪应", "password": "123456", "is_active": "1"}
    trader2 = {"trader_id": "1602", "trader_name": "尹家兴", "password": "123456", "is_active": "1"}
    # db.create_trader(trader1)
    # db.create_trader(trader2)
    # db.delete_trader('1601')
    # db.update_trader(trader1)
    # print(db.get_trader())
    print(db.get_trader())
    print(db.get_user())

