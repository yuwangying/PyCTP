# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


from PyCTP_Trade import PyCTP_Trader_API
import Utils


class User:
    # 初始化参数BrokerID\UserID\Password\FrontAddress，参数格式为二进制字符串
    def __init__(self, operator_id, BrokerID, FrontAddress, user_id, password, trader):
        print('创建User: operator_id=', operator_id, 'BrokerID=', BrokerID, 'user_id=', user_id)
        self.__operator_id = operator_id
        self.__BrokerID = BrokerID
        self.__UserID = user_id
        self.__Password = password
        self.__FrontAddress = FrontAddress
        self.__list_OnRtnOrder = []  # 保存单账户所有的OnRtnOrder回调
        self.__list_OnRtnTrade = []  # 保存单账户所有的OnRtnTrade回调
        self.__list_order_ing = []  # 以OrderRef为单个交易单元，还未执行完成的订单列表，临时存放较少的数据
        self.__list_SendOrder = []  # 保存单账户所有调用OrderInsert的记录
        self.__trader = trader  # 期货账户所属的交易员对象
        # 为每个user创建独立的流文件夹
        s_path = b'conn/td/' + self.__UserID + b'/'
        Utils.make_dirs(s_path)  # 创建流文件路劲
        self.__trader = PyCTP_Trader_API.CreateFtdcTraderApi(s_path)
        self.__trader.set_user(self)
        print('===========================')
        print(self.__UserID, '连接交易前置', Utils.code_transform(self.__trader.Connect(self.__FrontAddress)))
        print(self.__UserID, '交易账号登陆', Utils.code_transform(self.__trader.Login(self.__BrokerID, self.__UserID, self.__Password)))
        print(self.__UserID, '交易日', Utils.code_transform(self.__trader.GetTradingDay()))
        print(self.__UserID, '设置投资者代码', Utils.code_transform(self.__trader.setInvestorID(self.__UserID)))

    # 删除operator_id下面的某个期货账户
    # 参数说明： user=实例名称
    def del_user(self, operator_id, BrokerID, FrontAddress, user_id):
        print('del_user(): operator_id=', operator_id, 'BrokerID=', BrokerID, 'user_id=', user_id)
        del_user_arguments = {'operator_id': operator_id,
                              'BrokerID': BrokerID,
                              'UserID': user_id,
                              'FrontAddress': FrontAddress}
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
        print("on_rtn_order()", order)
        self.__order = Utils.code_transform(order)  # 回调函数字段
        self.__order['SendOrderTime'] = None  # 用户添加字段：发送报单时间
        self.__order['SendOrderMicrosecond'] = None  # 用户添加字段：发送报单微妙
        self.__order['CtpRtnOrderTime'] = None
        self.__order['CtpRtnOrderMicrosecond'] = None
        self.__order['ExchRtnOrderTime'] = None
        self.__order['ExchRtnOrderMicrosecond'] = None
        self.__order['OperatorID'] = None  # 客户端账号（也能区分用户身份或交易员身份）
        self.__order['StrategyID'] = None  # 交易策略编号
        print("on_rtn_order()", self.__order)

if __name__ == '__main__':
    print("User.py, if __name__ == '__main__':")
    pass
        




