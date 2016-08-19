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
        self.__user_id = dict_arguments['user_id'].encode()
        self.__trader_id = dict_arguments['trader_id'].encode()
        self.__BrokerID = dict_arguments['broker_id'].encode()
        self.__Password = dict_arguments['password'].encode()
        self.__FrontAddress = dict_arguments['front_address'].encode()
        # self.__trader = dict_arguments['trader']  # 期货账户所属的交易员对象
        self.__list_OnRtnOrder = []  # 保存单账户所有的OnRtnOrder回调
        self.__list_OnRtnTrade = []  # 保存单账户所有的OnRtnTrade回调
        self.__list_order_ing = []  # 以OrderRef为单个交易单元，还未执行完成的订单列表，临时存放较少的数据
        self.__list_SendOrder = []  # 保存单账户所有调用OrderInsert的记录
        # 为每个user创建独立的流文件夹
        s_path = b'conn/td/' + self.__user_id + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__trader = PyCTP_Trader_API.CreateFtdcTraderApi(s_path)
        self.__trader.set_user(self)
        print('===========================')
        print(self.__user_id, '连接交易前置', Utils.code_transform(self.__trader.Connect(self.__FrontAddress)))
        print(self.__user_id, '交易账号登陆', Utils.code_transform(self.__trader.Login(self.__BrokerID, self.__user_id, self.__Password)))
        print(self.__user_id, '交易日', Utils.code_transform(self.__trader.GetTradingDay()))
        print(self.__user_id, '设置投资者代码', Utils.code_transform(self.__trader.setInvestorID(self.__user_id)))

    def get_user_id(self):
        return self.__user_id

    def get_trader_id(self):
        return self.__trader_id

    def get_trade(self):
        return self.__trader

    # 删除operator_id下面的某个期货账户
    # 参数说明： user=实例名称
    def del_user(self, trader_id, broker_id, front_address, user_id):
        print('del_user(): trader_id=', trader_id, 'broker_id=', broker_id, 'user_id=', user_id)
        del_user_arguments = {'trader_id': trader_id,
                              'broker_id': broker_id,
                              'UserID': user_id,
                              'front_address': front_address}
        # 删除期货账户，释放TradeApi实例
        self.UnConnect()
        # 操作MongoDB，删除Operator下面的user_id（期货账户）

    # 查询行情
    def qry_depth_market_data(self, instrument_id):
        return self.__trader.QryDepthMarketData(instrument_id)

    # 对PyCTP_Market_API类中回调函数OnRtnOrder的间接回调
    def on_rtn_trade(self, trade):
        self.__trade = Utils.code_transform(trade)  # 回调函数字段
        self.__trade['OperatorID'] = None  # 客户端账号（也能区分用户身份或交易员身份）
        self.__trade['StrategyID'] = None  # 交易策略编号
        self.__trade['RecTradeTime'] = None  # 收到成交回报的时间
        self.__trade['RecTradeMicrosecond'] = None  # 收到成交回报的时间
        print("on_rtn_trade()", self.__trade)

    # 对PyCTP_Market_API类中回调函数OnRtnTrade的间接回调
    def on_rtn_order(self, order):
        self.__order = Utils.code_transform(order)  # 回调函数字段
        self.__order['SendOrderTime'] = None  # 用户添加字段：发送报单时间
        self.__order['SendOrderMicrosecond'] = None  # 用户添加字段：发送报单微妙
        self.__order['CtpRtnOrderTime'] = None
        self.__order['CtpRtnOrderMicrosecond'] = None
        self.__order['ExchRtnOrderTime'] = None
        self.__order['ExchRtnOrderMicrosecond'] = None
        self.__order['OperatorID'] = None  # 客户端账号（也能区分用户身份或交易员身份）
        self.__order['StrategyID'] = None  # 交易策略编号

if __name__ == '__main__':
    print("User.py, if __name__ == '__main__':")
    pass
        




