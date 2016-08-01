# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


from PyCTP_Trade import PyCTP_Trader_API
import Utils


class User:
    # 初始化参数BrokerID\UserID\Password\FrontAddress，参数格式为二进制字符串
    def __init__(self, operator_id, BrokerID, FrontAddress, user_id, password):
        print('创建User: operator_id=', operator_id, 'BrokerID=', BrokerID, 'user_id=', user_id)
        self.operator_id = operator_id
        self.BrokerID = BrokerID
        self.UserID = user_id
        self.Password = password
        self.FrontAddress = FrontAddress
        self.list_OnRtnOrder = []  # 保存单账户所有的OnRtnOrder回调
        self.list_OnRtnTrade = []  # 保存单账户所有的OnRtnTrade回调
        self.list_order_ing = []  # 以OrderRef为单个交易单元，还未执行完成的订单列表，临时存放较少的数据
        self.list_SendOrder = []  # 保存单账户所有调用OrderInsert的记录
        # 为每个user创建独立的流文件夹
        self.trader = PyCTP_Trader_API.CreateFtdcTraderApi(b'tmp/'+self.UserID)
        print('del_user(): operator_id=', operator_id, 'BrokerID=', BrokerID, 'user_id=', user_id)
        print('===========================')
        print(self.UserID, '连接交易前置', Utils.code_transform(self.trader.Connect(self.FrontAddress)))
        print(self.UserID, '交易账号登陆', Utils.code_transform(self.trader.Login(self.BrokerID, self.UserID, self.Password)))
        print(self.UserID, '交易日', Utils.code_transform(self.trader.GetTradingDay()))
        print(self.UserID, '设置投资者代码', Utils.code_transform(self.trader.setInvestorID(self.UserID)))
        # Simnow BrokerID='9999'，国贸期货CTP BrokerID='0187'
        # Simnow测试账号058176、669822，姓名：原鹏飞
        # Simnow测试账号063802、123456，姓名：余汪应
        # 国贸期货CTP电信账号，钱海玲，86001878/242169
        # 24小时交易、行情前置：180.168.146.187:10030、180.168.146.187:10031
        # 标准CTP交易、行情前置：180.168.146.187:10000、180.168.146.187:10010
        # CTPMini1：第一组：TradeFront：180.168.146.187:10003，MarketFront：180.168.146.187:10013；【电信】
        # 国贸期货CTP电信：交易：101.95.8.190:41205，行情：101.95.8.190:41213

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



