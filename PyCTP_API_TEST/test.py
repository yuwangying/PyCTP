# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 00:31:14 2016

@author: Zhuolin
"""

import sys
import threading
import chardet
import pandas as pd
from pandas import Series, DataFrame
import FunctionLog
import PyCTP
from Trade import PyCTP_Trader, PyCTP_Trader_API
from Market import PyCTP_Market, PyCTP_Market_API


class Strategy:
    def __init__(self):
        print('新建Strategy类的实例')

    @staticmethod
    def strategy_1(len_ma1=10, len_ma2=20):
        print('strategy_1被调用，参数:', len_ma1, len_ma2)

    def strategy_2(self, len_ma1=10, len_ma2=20):
        print('strategy_2被调用，参数：', len_ma1, len_ma2)

def typetransform(data):
    pass

def __main__():
    # git hub test 2016年7月18日22:05:49
    import os
    import time
    # Simnow BrokerID='9999'，国贸期货CTP BrokerID='0187'
    # Simnow测试账号058176、669822，姓名：原鹏飞
    # Simnow测试账号063802、123456，姓名：余汪应
    # 国贸期货CTP电信账号，钱海玲，86001878/242169
    BrokerID = b'9999'
    UserID = b'063802'  #b'063802'
    Password = b'123456'  # b'123456'
    ExchangeID = b'SHFE'
    listInstrumentID = [b'cu1609', b'cu1610']
    InstrumentID = b'cu1609'
    trader = PyCTP_Trader.CreateFtdcTraderApi(b'tmp/_tmp_t_')
    market = PyCTP_Market.CreateFtdcMdApi(b'tmp/_tmp_m_')
    # 24小时交易、行情前置：180.168.146.187:10030、180.168.146.187:10031
    # 标准CTP交易、行情前置：180.168.146.187:10000、180.168.146.187:10010
    # CTPMini1：第一组：TradeFront：180.168.146.187:10003，MarketFront：180.168.146.187:10013；【电信】
    # 国贸期货CTP电信：交易：101.95.8.190:41205，行情：101.95.8.190:41213
    print('连接交易前置', trader.Connect(b'tcp://180.168.146.187:10000'))
    print('连接行情前置', market.Connect(b'tcp://180.168.146.187:10010'))
    print('交易账号登陆', trader.Login(BrokerID, UserID, Password))
    print('交易账号登陆', market.Login(BrokerID, UserID, Password))
    print('交易日', trader.GetTradingDay())
    print('设置投资者代码', trader.setInvestorID(UserID))
    time.sleep(1.0)
    print('查询交易所', trader.QryExchange())
    time.sleep(1.0)
    print('查询投资者', trader.QryInvestor())
    time.sleep(1.0)
    print('查询资金账户', trader.QryTradingAccount())

    # time.sleep(1.0)
    # print('查询合约', trader.QryInstrument(b'SHFE'))
    # time.sleep(1.0)
    # dictInstrument = trader.QryInstrument(b'')
    # dfInstrument = DataFrame(dictInstrument)
    # dfInstrument['CombinationType'] = dfInstrument['CombinationType'].str.decode('gbk')
    # dfInstrument['CreateDate'] = dfInstrument['CreateDate'].str.decode('gbk')
    # dfInstrument['EndDelivDate'] = dfInstrument['EndDelivDate'].str.decode('gbk')
    # dfInstrument['ExchangeID'] = dfInstrument['ExchangeID'].str.decode('gbk')
    # dfInstrument['ExchangeInstID'] = dfInstrument['ExchangeInstID'].str.decode('gbk')
    # dfInstrument['ExpireDate'] = dfInstrument['ExpireDate'].str.decode('gbk')
    # dfInstrument['InstLifePhase'] = dfInstrument['InstLifePhase'].str.decode('gbk')
    # dfInstrument['InstrumentID'] = dfInstrument['InstrumentID'].str.decode('gbk')
    # dfInstrument['InstrumentName'] = dfInstrument['InstrumentName'].str.decode('gbk')
    # dfInstrument['MaxMarginSideAlgorithm'] = dfInstrument['MaxMarginSideAlgorithm'].str.decode('gbk')
    # dfInstrument['OpenDate'] = dfInstrument['OpenDate'].str.decode('gbk')
    # dfInstrument['OptionsType'] = dfInstrument['OptionsType'].str.decode('gbk')
    # dfInstrument['PositionDateType'] = dfInstrument['PositionDateType'].str.decode('gbk')
    # dfInstrument['PositionType'] = dfInstrument['PositionType'].str.decode('gbk')
    # dfInstrument['PositionType'] = dfInstrument['PositionType'].str.decode('gbk')
    # dfInstrument['ProductClass'] = dfInstrument['ProductClass'].str.decode('gbk')
    # dfInstrument['ProductID'] = dfInstrument['ProductID'].str.decode('gbk')
    # dfInstrument['StartDelivDate'] = dfInstrument['StartDelivDate'].str.decode('gbk')
    # dfInstrument['UnderlyingInstrID'] = dfInstrument['UnderlyingInstrID'].str.decode('gbk')
    # dfInstrument['UnderlyingInstrID'] = dfInstrument['UnderlyingInstrID'].str.decode('gbk')
    # time.sleep(1.0)
    # dfInstrument.to_csv('data/dfInstrument.csv')
    #
    # time.sleep(1.0)
    # print('查询合约', trader.QryInstrument(b'CZCE'))
    # time.sleep(1.0)
    # print('查询合约', trader.QryInstrument(b'DCE'))
    # time.sleep(1.0)
    # print('查询合约', trader.QryInstrument(b'CFFEX'))
    time.sleep(1.0)
    print('查询交易代码', trader.QryTradingCode(ExchangeID))
    time.sleep(1.0)
    print('合约手续费率', trader.QryInstrumentCommissionRate(InstrumentID))
    time.sleep(1.0)
    print('合约保证金率', trader.QryInstrumentMarginRate(InstrumentID))
    time.sleep(1.0)
    print('查询报单', trader.QryOrder())
    time.sleep(1.0)
    print('查询成交单', trader.QryTrade())
    time.sleep(1.0)
    print('投资者持仓', trader.QryInvestorPosition())
    time.sleep(1.0)
    print('查询行情', trader.QryDepthMarketData(InstrumentID))
    time.sleep(1.0)
    print('订阅行情', market.SubMarketData(listInstrumentID))

    # 调试OrderInsert
    while True:
        var = input('select a=OrderAction, i=OrderInsert, b=Break\n')
        # 进入OrderInsert命令模式
        if var == 'i':
            print('please input OrderInsert arguments dict:Instrument, Action, Direction, Volume, Price, OrderRef\n')
            input_params = input()
            input_params = eval(input_params)
            print('输入参数为\n', input_params)
            trader.OrderInsert(InstrumentID=input_params['InstrumentID'],
                               Action=input_params['Action'],
                               Direction=input_params['Direction'],
                               Volume=input_params['Volume'],
                               Price=input_params['Price'],
                               OrderRef=input_params['OrderRef'])
            continue
        # 进入OrderAction命令模式
        elif var == 'a':
            print('please input OrderAction arguments:\n')
            input_params = input()
            input_params = eval(input_params)
            print('输入参数为\n', input_params)
            trader.OrderAction(ExchangeID=input_params['ExchangeID'],
                               OrderRef=input_params['OrderRef'],
                               OrderSysID=input_params['OrderSysID'])
            continue
        # 保存数据到本地
        elif var == 's':
            PyCTP_Market.df_data.to_csv('data/df_data.csv')  # 保存行情到本地csv文件
            PyCTP_Trader.dfInstrumentStatus.to_csv('data/dfInstrumentStatus.csv')  # 保合约状态到本地csv文件
            continue
        # 查询投资者持仓，并输出到控制台
        elif var == 'q':
            print('投资者持仓', trader.QryInvestorPosition(InstrumentID))
        # 退出
        elif var == 'b':
            break
        # 输入错误重新输入
        else:
            print('input error, please inpurt again\n')
            continue

    time.sleep(1.0)
    print('退订行情:', market.UnSubMarketData(listInstrumentID))
    print('交易账号登出', trader.Logout())
    print('行情账号登出', market.Logout())

if __name__ == '__main__':
    __main__()

