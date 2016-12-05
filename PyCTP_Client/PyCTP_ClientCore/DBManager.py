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
        self.__mongo_client = MongoClient('localhost', 27017)  # 创建数据库连接实例
        self.__db_CTP = self.__mongo_client.CTP  # 总数据库
        self.__col_admin = self.__db_CTP.admin  # 管理员集合
        self.__col_trader = self.__db_CTP.trader  # 交易员集合
        self.__col_user = self.__db_CTP.user  # 期货账户集合
        # 其他集合：策略、持仓、持仓明细、trade、order，在user类里管理

    def set_user(self, obj_user):
        self.__user = obj_user

    # 动态创建结合的方法，传入参数：集合名
    def create_collection(self, collection_name):
        self.__db_CTP.create_collection(collection_name)
    
    # 获取数据库中的集合，传入参数：集合名，返回值：集合
    def get_collection(self, collection_name):
        return self.__db_CTP.get_collection(collection_name)

    # 清空本地数据库
    def clear_db(self):
        self.__col_trader.remove()  # 清空交易员集合中的文档
        self.__col_user.remove()  # 清空user集合中的文档
        # self.__col_strategy.remove()  # 交易策略集合
        # self.__col_position.remove()  # 持仓
        # self.__col_position_detail.remove({'TradingDay': self.__user.GetTradingDay()})

    # 插入order记录到数据库
    # def insert_order(self, order):
    #     pass
    # 
    # 插入trade记录到数据库
    # def insert_trade(self, trade):
    #     self.__col_position_detail.insert(trade)
    #     pass

    def get_col_trader(self):
        return self.__col_trader

    def get_col_user(self):
        return self.__col_user

    # def get_col_strategy(self, str_user_id):
    #     return self.__col_strategy
    # 
    # def get_col_position(self):
    #     return self.__col_position
    # 
    # def get_col_position_detail(self):
    #     return self.__col_position_detail

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
        # 形参trader_name不为空时，条件查找并返回交易员
        else:
            list_trader = [self.__col_trader.find_one({"trader_id": trader_id})]

        if len(list_trader) == 0:
            # print("DBManager.get_trader()数据库中不存在交易员", list_trader)
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
        # 形参user_id为空时返回所有期货账户
        list_user = []
        if user_id == '':
            for i in self.__col_user.find({}):
                list_user.append(i)
            return list_user
        # 形参user_id不为空时，条件查找并返特定期货账户
        else:
            user = self.__col_user.find_one({"user_id": user_id})
            if user is None:
                return None
            else:
                return user  # list_user.append(user)

    '''交易员查询名下所有期货账户信息，非管理员权限'''
    def get_user_id(self, trader_id):
        list_user = list()
        for i in self.__col_user.find({'trader_id': trader_id}):
            list_user.append(i)
        return list_user

    '''strategy管理'''
    # 创建策略
    def create_strategy(self, dict_arguments):
        print("===========================")
        trader_id = dict_arguments['trader_id']
        user_id = dict_arguments['user_id']
        strategy_id = dict_arguments['strategy_id']
        # 检查数据库中是否存在交易员账号
        if self.__col_trader.count({'trader_id': trader_id}) == 0:
            print("DBManager.create_strategy()数据库中不存在交易员账号", trader_id)
            return False
        # 检查数据库中是否存在期货账号
        if self.__col_user.count({'user_id': user_id}) == 0:
            print("DBManager.create_strategy()数据库中不存在期货账号", user_id)
            return False
        # 除重
        if self.__user.get_col_strategy.count({'user_id': user_id, 'strategy_id': strategy_id}) > 0:
            print("DBManager.create_strategy()数据库中已存在期货账号", user_id, '的策略编号', strategy_id)
            return False
        self.__user.get_col_strategy.insert_one(dict_arguments)
        print("DBManager.create_strategy()策略信息存入数据库成功", dict_arguments)
        return True

    # 删除策略
    def delete_strategy(self, user_id, strategy_id):
        # 在数据库strategy集合中查找是否存在将要删除的strategy
        if self.__col_user.count({'user_id': user_id}) == 0:
            print("DBManager.delete_strategy()数据库中不存在期货账户", user_id)
            return False
        if self.__user.get_col_strategy.count({'user_id': user_id, 'strategy_id': strategy_id}) == 0:
            print("DBManager.delete_strategy()数据库中不存在期货账户为", user_id, '的策略编号', strategy_id)
            return False
        self.__user.get_col_strategy.remove({'user_id': user_id, 'strategy_id': strategy_id})
        print("DBManager.create_strategy()成功从数据库删除期货账户为", user_id, '的策略编号', strategy_id)
        return True

    # 修改策略
    def update_strategy(self, dict_arguments):
        trader_id = dict_arguments['trader_id']
        user_id = dict_arguments['user_id']
        strategy_id = dict_arguments['strategy_id']
        # 在数据库strategy集合中查找是否存在将要修改的strategy
        if self.__col_user.count({'trader_id': trader_id}) == 0:
            print("DBManager.delete_strategy()数据库中不存在交易员", trader_id)
            return False
        if self.__col_user.count({'trader_id': trader_id, 'user_id': user_id}) == 0:
            print("DBManager.delete_strategy()数据库中交易员", trader_id, "不存在期货账户", user_id)
            return False
        if self.__user.get_col_strategy().count({'user_id': user_id, 'strategy_id': strategy_id}) == 0:
            print("DBManager.delete_strategy()数据库中不存在期货账户", user_id, '的策略', strategy_id)
            return False
        self.__user.get_col_strategy().update_one({'trader_id': trader_id, 'user_id': user_id, 'strategy_id': strategy_id}, {"$set": dict_arguments})
        print("DBManager.update_strategy() 成功更新期货账户", user_id, '策略编号', strategy_id, '策略参数')
        return True

    # 查询策略
    def get_strategy(self, dict_arguments):
        # 形参{'trader_id': '1601', 'user_id': '800658', 'strategy_id': '01'}
        # 当形参中某键值不存在时，查询该键值所有的策略
        list_strategy = list()
        if len(dict_arguments) == 0:  # 查询所有
            for i in self.__user.get_col_strategy.find({}):
                list_strategy.append(i)
        # 形参中有trader_id
        elif len(dict_arguments) == 1 and 'trader_id' in dict_arguments:
            if self.__col_trader.count({'trader_id': dict_arguments['trader_id']}) == 0:
                print("DBManager.get_strategy()数据库中不存在交易员", dict_arguments['trader_id'])
                return None
            for i in self.__user.get_col_strategy.find({'trader_id': dict_arguments['trader_id']}):
                list_strategy.append(i)
        # 形参中有trader_id、user_id
        elif len(dict_arguments) == 2 and 'trader_id' in dict_arguments and 'user_id' in dict_arguments:
            if self.__col_user.count({'user_id': dict_arguments['user_id']}) == 0:
                print("DBManager.get_strategy()数据库中不存在期货账户", dict_arguments['user_id'])
                return None
            for i in self.__user.get_col_strategy.find({'trader_id': dict_arguments['trader_id'], 'user_id': dict_arguments['user_id']}):
                list_strategy.append(i)
        # 形参中有trader_id、user_id、strategy_id
        elif len(dict_arguments) == 3 and 'trader_id' in dict_arguments and 'user_id' in dict_arguments and 'strategy_id' in dict_arguments:
            trader_id = dict_arguments['trader_id']
            user_id = dict_arguments['user_id']
            strategy_id = dict_arguments['strategy_id']
            if self.__user.get_col_strategy.count({'trader_id': trader_id, 'user_id': user_id, 'strategy_id': strategy_id}) == 0:
                print("DBManager.get_strategy()数据库中不存在期货账户", user_id, "的策略", strategy_id)
                return None
            for i in self.__user.get_col_strategy.find({'trader_id': trader_id, 'user_id': user_id, 'strategy_id': strategy_id}):
                list_strategy.append(i)
        else:
            print("DBManager.get_strategy()参数错误")
            return None
        return list_strategy


