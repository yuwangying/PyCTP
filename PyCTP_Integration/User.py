# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


from PyCTP_Trade import PyCTP_Trader_API
import Utils


class User:
    # 初始化参数BrokerID\UserID\Password\front_address，参数格式为二进制字符串
    def __init__(self, dict_arguments):
        # 形参{'trader_id': '', 'broker_id': '', 'front_address': '', 'user_id': '', 'password': '', 'trader': ''}
        self.__trader_id = dict_arguments['trader_id'].encode()
        self.__user_id = dict_arguments['user_id'].encode()
        self.__BrokerID = dict_arguments['broker_id'].encode()
        self.__Password = dict_arguments['password'].encode()
        self.__FrontAddress = dict_arguments['front_address'].encode()

        self.__list_OnRtnOrder = []  # 保存单账户所有的OnRtnOrder回调数据
        self.__list_OnRtnTrade = []  # 保存单账户所有的OnRtnTrade回调数据
        self.__list_order_ing = []  # 以OrderRef为单个交易单元，还未执行完成的订单列表，临时存放较少的数据
        self.__list_SendOrder = []  # 保存单账户所有调用OrderInsert的记录
        self.__list_strategy = []  # 期货账户下面的所有交易策略实例列表
        # self.__list_InstrumentId = []  # 合约列表，记录撤单次数，在创建策略的时候添加合约，
        self.__dict_instrument_action_counter = dict()  # 记录合约撤单次数的字典,撤单操作时添加次数，交易日换日时初始化值
        self.__order_ref_part2 = 0  # 所有策略共用报单引用编号

        # 为每个user创建独立的流文件夹
        s_path = b'conn/td/' + self.__user_id + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__trade = PyCTP_Trader_API.CreateFtdcTraderApi(s_path)
        self.__trade.set_user(self)  # 将该类设置为trade的属性
        print('===========================')
        print(self.__user_id, '连接交易前置', Utils.code_transform(self.__trade.Connect(self.__FrontAddress)))
        print(self.__user_id, '登陆交易账号', Utils.code_transform(self.__trade.Login(self.__BrokerID, self.__user_id, self.__Password)))
        print(self.__user_id, '交易日', Utils.code_transform(self.__trade.GetTradingDay()))
        print(self.__user_id, '投资者代码', Utils.code_transform(self.__trade.setInvestorID(self.__user_id)))
        self.__front_id = self.__trade.get_front_id()  # 获取前置编号
        self.__session_id = self.__trade.get_session_id()  # 获取会话编号
        self.__instrument_info = Utils.code_transform(self.qry_instrument())  # 查询合约，所有交易所的所有合约
        print("User.__init__.self.__instrument_info=", self.__instrument_info)
    # 获取期货账号
    def get_user_id(self):
        return self.__user_id

    # 获取交易员id
    def get_trader_id(self):
        return self.__trader_id

    # 获取trade实例(TD)
    def get_trade(self):
        return self.__trade

    # 获取self.__instrument_info
    def get_instrument_info(self):
        return self.__instrument_info

    # 获取报单引用part2
    def add_order_ref_part2(self):
        self.__order_ref_part2 += 1
        return self.__order_ref_part2

    # 添加交易策略实例，到self.__list_strategy
    def add_strategy(self, obj_strategy):
        self.__list_strategy.append(obj_strategy)  # 将交易策略实例添加到本类的交易策略列表
        self.__trade.set_list_strategy(self.__list_strategy)  # 将本类的交易策略列表转发给trade
        obj_strategy.set_user(self)  # 将user设置为strategy属性

    # 添加合约代码到user类的self.__dict_instrument_action_counter
    def add_instrument_id_action_counter(self, list_instrument_id):
        for i in list_instrument_id:
            if i not in self.__dict_instrument_action_counter:
                self.__dict_instrument_action_counter[i] = 0

    # 撤单计数
    def action_counter(self, instrument_id):
        if instrument_id in self.__dict_instrument_action_counter:
            self.__dict_instrument_action_counter[instrument_id] += 1

    # 删除交易策略实例，从self.__list_strategy
    def del_strategy(self, strategy_id):
        for i in self.__list_strategy:
            if i.get_strategy_id() == strategy_id:
                self.__list_strategy.remove(i)

    # 获取list_strategy
    def get_list_strategy(self):
        return self.__list_strategy

    # 获取合约撤单次数的字典
    def get_dict_instrument_action_counter(self):
        return self.__dict_instrument_action_counter

    # 查询行情
    def qry_depth_market_data(self, instrument_id):
        return self.__trade.QryDepthMarketData(instrument_id)

    # 查询合约
    def qry_instrument(self):
        return self.__trade.QryInstrument()

    # 转PyCTP_Market_API类中回调函数OnRtnOrder
    def OnRtnTrade(self, Trade):
        # print("User.OnRtnTrade()", 'OrderRef:', Trade['OrderRef'], 'Trade:', Trade)
        pass

    #     转PyCTP_Market_API类中回调函数OnRtnOrder
    def OnRtnOrder(self, Order):
        # print("User.OnRtnOrder()", 'OrderRef:', Order['OrderRef'], 'Order:', Order)
        pass

if __name__ == '__main__':
    print("User.py, if __name__ == '__main__':")
    pass
        




