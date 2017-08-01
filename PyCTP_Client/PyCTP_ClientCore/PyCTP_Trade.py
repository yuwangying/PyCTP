# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 00:31:14 2016

@author: Zhuolin
"""

import sys
from datetime import datetime
import threading
import pandas as pd
from pandas import Series, DataFrame
import Utils
import PyCTP
import copy
# from MessageBox import MessageBox


class PyCTP_Trader_API(PyCTP.CThostFtdcTraderApi):

    TIMEOUT = 300

    __RequestID = 0
    __isLogined = False
    # __df_order = DataFrame()  # 保存该期货账户的所有OnRtnOrder来的记录
    # __df_trade = DataFrame()  # 保存该期货账户的所有OnRtnTrade来的记录
    __df_qry_order = DataFrame()  # 保存该期货账户的所有QryOrder返回的记录
    __df_qry_trade = DataFrame()  # 保存该期货账户的所有QryTrade返回的记录

    def __IncRequestID(self):
        """ 自增并返回请求ID """
        self.__RequestID += 1
        return self.__RequestID

    # ywy新增加
    def __IncOrderRef(self):
        """ 递增报单引用 """
        OrderRef = bytes('%012d' % self.__OrderRef, 'gb2312')
        self.__OrderRef += 1
        return OrderRef

    def __IncOrderActionRef(self):
        """ 递增报单操作引用 """
        OrderActionRef = bytes('%012d' % self.__OrderActionRef, 'gb2312')
        self.__OrderActionRef += 1
        return OrderActionRef

    def setInvestorID(self, InvestorID):
        self.__InvestorID = InvestorID

    def Connect(self, frontAddr, model):
        """ 连接前置服务器 """
        self.RegisterSpi(self)
        self.SubscribePrivateTopic(model)  # 从本次连线之后开始发送数据
        self.SubscribePublicTopic(PyCTP.THOST_TERT_QUICK)
        self.RegisterFront(frontAddr.encode())
        self.Init()
        self.__rsp_Connect = dict(event=threading.Event())
        self.__rsp_Connect['event'].clear()
        return 0 if self.__rsp_Connect['event'].wait(self.TIMEOUT) else -4

    def UnConnect(self):
        """ywy：断开连接，释放TradeApi"""
        self.RegisterSpi(None)
        self.Release()

    def Login(self, BrokerID, UserID, Password):
        """ 用户登录请求 """
        reqUserLogin = dict(BrokerID=BrokerID,
                            UserID=UserID,
                            Password=Password)
        self.__rsp_Login = dict(event=threading.Event(),
                                RequestID=self.__IncRequestID())
        ret = self.ReqUserLogin(reqUserLogin, self.__rsp_Login['RequestID'])
        if ret == 0:
            self.__rsp_Login['event'].clear()
            if self.__rsp_Login['event'].wait(self.TIMEOUT):
                if self.__rsp_Login['ErrorID'] == 0:
                    self.__isLogined = True
                    self.__Password = Password
                else:
                    sys.stderr.write(str(self.__rsp_Login['ErrorMsg'], encoding='gb2312'))
                return self.__rsp_Login['ErrorID']
            else:
                return -4
        return ret

    # 获取登录状态
    def get_isLogined(self):
        return self.__isLogined

    def Logout(self):
        """ 登出请求 """
        reqUserLogout = dict(BrokerID=self.__BrokerID, UserID=self.__UserID)
        self.__rsp_Logout = dict(event=threading.Event(), RequestID=self.__IncRequestID())
        ret = self.ReqUserLogout(reqUserLogout, self.__rsp_Logout['RequestID'])
        if ret == 0:
            self.__rsp_Logout['event'].clear()
            if self.__rsp_Logout['event'].wait(self.TIMEOUT):
                if self.__rsp_Logout['ErrorID'] == 0:
                    self.__isLogined = False
                return self.__rsp_Logout['ErrorID']
            else:
                return -4
        return ret

    def QryInstrument(self, ExchangeID=b'', InstrumentID=b''):
        """ 查询和约 """
        QryInstrument = dict(ExchangeID=ExchangeID, InstrumentID=InstrumentID)
        self.__rsp_QryInstrument = dict(event=threading.Event()
                                        , RequestID=self.__IncRequestID()
                                        , results=[]
                                        , ErrorID=0)
        ret = self.ReqQryInstrument(QryInstrument, self.__rsp_QryInstrument['RequestID'])
        if ret == 0:
            # if self.__rsp_QryInstrument['ErrorID'] != 0:
            #     return self.__rsp_QryInstrument['ErrorID']
            # else:
            #     return self.__rsp_QryInstrument['results']
            self.__rsp_QryInstrument['event'].clear()
            if self.__rsp_QryInstrument['event'].wait(30.0):
                if self.__rsp_QryInstrument['ErrorID'] != 0:
                    return self.__rsp_QryInstrument['ErrorID']
                return self.__rsp_QryInstrument['results']
            else:
                print('PyCTP_Trade_API.QryInstrument() -4')
                return -4
        return ret

    def QryInstrumentMarginRate(self, InstrumentID):
        """ 请求查询合约保证金率 """
        QryInstrumentMarginRate = dict(BrokerID         = self.__BrokerID
                                       , InvestorID     = self.__InvestorID
                                       , InstrumentID   = InstrumentID)
        self.__rsp_QryInstrumentMarginRate = dict(results       =  []
                                                  , RequestID   = self.__IncRequestID()
                                                  , ErrorID     = 0
                                                  , event       = threading.Event())
        ret = self.ReqQryInstrumentMarginRate(QryInstrumentMarginRate, self.__rsp_QryInstrumentMarginRate['RequestID'])
        if ret == 0:
            self.__rsp_QryInstrumentMarginRate['event'].clear()
            if self.__rsp_QryInstrumentMarginRate['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInstrumentMarginRate['ErrorID'] != 0:
                    return self.__rsp_QryInstrumentMarginRate['ErrorID']
                return self.__rsp_QryInstrumentMarginRate['results']
            else:
                return -4
        return ret

    def QryInstrumentCommissionRate(self, InstrumentID):
        """ 请求查询合约手续费率 """
        QryInstrumentCommissionRate = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, InstrumentID=InstrumentID)
        self.__rsp_QryInstrumentCommissionRate = dict(results=[],
                                                      RequestID=self.__IncRequestID(),
                                                      ErrorID=0,
                                                      event=threading.Event())
        ret = self.ReqQryInstrumentCommissionRate(QryInstrumentCommissionRate, self.__rsp_QryInstrumentCommissionRate['RequestID'])
        if ret == 0:
            self.__rsp_QryInstrumentCommissionRate['event'].clear()
            if self.__rsp_QryInstrumentCommissionRate['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInstrumentCommissionRate['ErrorID'] != 0:
                    return self.__rsp_QryInstrumentCommissionRate['ErrorID']
                return self.__rsp_QryInstrumentCommissionRate['results']
            else:
                return -4
        return ret

    def QryOrder(self, InstrumentID=b'', OrderSysID=b'', InsertTimeStart=b'', InsertTimeEnd=b''):
        """请求查询报单"""
        QryOrderField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, OrderSysID=OrderSysID, InsertTimeStart=InsertTimeStart, InsertTimeEnd=InsertTimeEnd, InstrumentID=InstrumentID)
        self.__rsp_QryOrder = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryOrder(QryOrderField, self.__rsp_QryOrder['RequestID'])
        if ret == 0:
            self.__rsp_QryOrder['event'].clear()
            if self.__rsp_QryOrder['event'].wait(60.0):
                if self.__rsp_QryOrder['ErrorID'] != 0:
                    # self.__user.QryOrder(self.__rsp_QryOrder['ErrorID'])  # 转到user类的回调函数
                    return self.__rsp_QryOrder['ErrorID']
                # self.__user.QryOrder(self.__rsp_QryOrder['results'])  # 转到user类的回调函数
                return Utils.code_transform(self.__rsp_QryOrder['results'])
            else:
                # self.__user.QryOrder(-4)  # 转到user类的回调函数
                print(" PyCTP_Trade.QryTrade() user_id=", self.__UserID, "请求查询报单异常，-4")
                return -4
        # self.__user.QryOrder(ret)  # 转到user类的回调函数
        return ret

    def QryTrade(self, InstrumentID=b'', ExchangeID=b'', TradeID=b''):
        """请求查询成交单"""
        QryTradeField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, InstrumentID=InstrumentID, ExchangeID=ExchangeID, TradeID=TradeID)
        self.__rsp_QryTrade = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryTrade(QryTradeField, self.__rsp_QryTrade['RequestID'])
        if ret == 0:
            self.__rsp_QryTrade['event'].clear()
            if self.__rsp_QryTrade['event'].wait(60.0):  # (self.TIMEOUT):  # 成交记录多，传输等待时间需要延长
                if self.__rsp_QryTrade['ErrorID'] != 0:
                    # self.__user.QryTrade(self.__rsp_QryTrade['ErrorID'])  # 转到user类的回调函数
                    return self.__rsp_QryTrade['ErrorID']
                # self.__user.QryTrade(self.__rsp_QryTrade['results'])  # 转到user类的回调函数
                return self.__rsp_QryTrade['results']
            else:
                # self.__user.QryTrade(-4)  # 转到user类的回调函数
                print(" PyCTP_Trade.QryTrade() user_id=", self.__UserID, "请求查询成交单异常，-4")
                return -4
        # self.__user.QryTrade(ret)  # 转到user类的回调函数
        return ret

    def QryInvestorPosition(self, InstrumentID=b''):
        """ 请求查询投资者持仓 """
        QryInvestorPositionField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, InstrumentID=InstrumentID)
        self.__rsp_QryInvestorPosition = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryInvestorPosition(QryInvestorPositionField, self.__rsp_QryInvestorPosition['RequestID'])
        if ret == 0:
            self.__rsp_QryInvestorPosition['event'].clear()
            if self.__rsp_QryInvestorPosition['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInvestorPosition['ErrorID'] != 0:
                    return self.__rsp_QryInvestorPosition['ErrorID']
                return self.__rsp_QryInvestorPosition['results']
            else:
                return -4
        return ret

    def QryInvestorPositionDetail(self, InstrumentID=b''):
        """ 请求查询投资者持仓明细 """
        # ywy 20170120
        QryInvestorPositionFieldDetail = dict(BrokerID=self.__BrokerID, 
                                              InvestorID=self.__InvestorID,
                                              InstrumentID=InstrumentID)
        self.__rsp_QryInvestorPositionDetail = dict(results=[], 
                                                    RequestID=self.__IncRequestID(),
                                                    ErrorID=0,
                                                    event=threading.Event())
        ret = self.ReqQryInvestorPositionDetail(QryInvestorPositionFieldDetail, self.__rsp_QryInvestorPositionDetail['RequestID'])
        if ret == 0:
            self.__rsp_QryInvestorPositionDetail['event'].clear()
            if self.__rsp_QryInvestorPositionDetail['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInvestorPositionDetail['ErrorID'] != 0:
                    return self.__rsp_QryInvestorPositionDetail['ErrorID']
                return self.__rsp_QryInvestorPositionDetail['results']
            else:
                return -4
        return ret

    def QryTradingAccount(self):
        """ 请求查询资金账户 """
        QryTradingAccountField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID)
        self.__rsp_QryTradingAccount = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryTradingAccount(QryTradingAccountField, self.__rsp_QryTradingAccount['RequestID'])
        if ret == 0:
            self.__rsp_QryTradingAccount['event'].clear()
            if self.__rsp_QryTradingAccount['event'].wait(self.TIMEOUT):
                if self.__rsp_QryTradingAccount['ErrorID'] != 0:
                    return self.__rsp_QryTradingAccount['ErrorID']
                return self.__rsp_QryTradingAccount['results']
            else:
                return -4
        return ret

    def QryInvestor(self):
        """ 请求查询投资者 """
        InvestorField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID)
        self.__rsp_QryInvestor = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryInvestor(InvestorField, self.__rsp_QryInvestor['RequestID'])
        if ret == 0:
            self.__rsp_QryInvestor['event'].clear()
            if self.__rsp_QryInvestor['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInvestor['ErrorID'] != 0:
                    return self.__rsp_QryInvestor['ErrorID']
                return self.__rsp_QryInvestor['results']
            else:
                return -4
        return ret

    def QryTradingCode(self, exchangeid):
        """请求查询交易编码"""
        QryTradingCodeField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID,
                                   ExchangeID=exchangeid)
        self.__rsp_QryTradingCode = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryTradingCode(QryTradingCodeField, self.__rsp_QryTradingCode['RequestID'])
        if ret == 0:
            self.__rsp_QryTradingCode['event'].clear()  # set event flag False
            if self.__rsp_QryTradingCode['event'].wait(self.TIMEOUT):
                if self.__rsp_QryTradingCode['ErrorID'] != 0:
                    return self.__rsp_QryTradingCode['ErrorID']
                return self.__rsp_QryTradingCode['results']
            else:
                return -4
        return ret

    def OnRtnInstrumentStatus(self, InstrumentStatus):
        pass

    def QryExchange(self, ExchangeID=b''):
        """ 请求查询交易所 """
        QryExchangeField = dict(ExchangeID=ExchangeID)
        self.__rsp_QryExchange = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryExchange(QryExchangeField, self.__rsp_QryExchange['RequestID'])
        if ret == 0:
            self.__rsp_QryExchange['event'].clear()
            if self.__rsp_QryExchange['event'].wait(self.TIMEOUT):
                if self.__rsp_QryExchange['ErrorID'] != 0:
                    return self.__rsp_QryExchange['ErrorID']
                return self.__rsp_QryExchange['results']
            else:
                return -4
        return ret

    def QryDepthMarketData(self, InstrumentID):
        """ 请求查询行情 """
        QryDepthMarketData = dict(InstrumentID=InstrumentID)
        self.__rsp_QryDepthMarketData = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryDepthMarketData(QryDepthMarketData, self.__rsp_QryDepthMarketData['RequestID'])
        if ret == 0:
            self.__rsp_QryDepthMarketData['event'].clear()
            if self.__rsp_QryDepthMarketData['event'].wait(self.TIMEOUT):
                if self.__rsp_QryDepthMarketData['ErrorID'] != 0:
                    return self.__rsp_QryDepthMarketData['ErrorID']
                return self.__rsp_QryDepthMarketData['results']
            else:
                return -4
        return ret

    def OrderInsert(self, dict_arguments):
        # InstrumentID, CombOffsetFlag, Direction, VolumeTotalOriginal, LimitPrice, OrderRef):
        print(">>> PyCTP_Trade.OrderInser() dict_arguments =", dict_arguments)
        """报单录入请求:开平仓(限价挂单)申报"""
        InputOrder = {'BrokerID': self.__BrokerID,  # 经纪公司代码
                      'InvestorID': self.__InvestorID,  # 投资者代码
                      'UserID': self.__UserID,  # 用户代码
                      'OrderPriceType': PyCTP.THOST_FTDC_OPT_LimitPrice,  # 报单价格条件:限价
                      'TimeCondition': PyCTP.THOST_FTDC_TC_GFD,  # 有效期类型:当日有效
                      'VolumeCondition': PyCTP.THOST_FTDC_VC_AV,  # 成交量类型:任意数量
                      'ContingentCondition': PyCTP.THOST_FTDC_CC_Immediately,  # 触发条件:立即
                      'ForceCloseReason': PyCTP.THOST_FTDC_FCC_NotForceClose,  # 强平原因:非强平
                      'MinVolume': 1,  # 最小成交量
                      'InstrumentID': dict_arguments['InstrumentID'],  # 合约代码
                      'LimitPrice': dict_arguments['LimitPrice'],  # 价格
                      'VolumeTotalOriginal': dict_arguments['VolumeTotalOriginal'],  # 数量
                      'Direction': dict_arguments['Direction'],  # 方向
                      'CombOffsetFlag': dict_arguments['CombOffsetFlag'],  # 组合开平标志，上期所3平今、4平昨，其他交易所1平仓
                      'CombHedgeFlag': dict_arguments['CombHedgeFlag'],  # 组合投机套保标志:投机
                      'OrderRef': dict_arguments['OrderRef'],  # 报单引用
                      }
        self.__rsp_OrderInsert = dict(FrontID=self.__FrontID,
                                      SessionID=self.__SessionID,
                                      InputOrder=InputOrder,
                                      RequestID=self.__IncRequestID(),
                                      event=threading.Event())
        ret = self.ReqOrderInsert(InputOrder, self.__rsp_OrderInsert['RequestID'])
        if ret == 0:
            # self.__rsp_OrderInsert['event'].clear()
            if True:  # self.__rsp_OrderInsert['event'].wait(self.TIMEOUT):
                if 'ErrorID' in self.__rsp_OrderInsert.keys():
                    if self.__rsp_OrderInsert['ErrorID'] != 0:
                        # print("PyCTP_Trade.OrderInsert()", self.__rsp_OrderInsert['ErrorMsg'])
                        # sys.stderr.write(str(self.__rsp_OrderInsert['ErrorMsg'], encoding='gb2312'))  # 错误代码，用上一行代替
                        return self.__rsp_OrderInsert['ErrorID']
                return self.__rsp_OrderInsert.copy()
            else:
                return -4
        return ret

    def OrderInsertDict(self, InstrumentID):
        """报单录入请求:开平仓(限价挂单)申报"""

        InputOrder = {}
        InputOrder.update(InstrumentID)

        self.__rsp_OrderInsert = dict(FrontID=self.__FrontID
                                      , SessionID=self.__SessionID
                                      , InputOrder=InputOrder
                                      , RequestID=self.__IncRequestID()
                                      , event=threading.Event())
        print('ReqOrderInsert的传入参数', InputOrder)
        ret = self.ReqOrderInsert(InputOrder, self.__rsp_OrderInsert['RequestID'])
        if ret == 0:
            # self.__rsp_OrderInsert['event'].clear()
            if True:  # self.__rsp_OrderInsert['event'].wait(self.TIMEOUT):
                if self.__rsp_OrderInsert['ErrorID'] != 0:
                    sys.stderr.write(str(self.__rsp_OrderInsert['ErrorMsg'], encoding='gb2312'))
                    return self.__rsp_OrderInsert['ErrorID']
                return self.__rsp_OrderInsert.copy()
            else:
                return -4
        return ret

    def OrderAction(self, dict_arguments):
        # ExchangeID, OrderRef, OrderSysID):
        """报单操作请求"""
        """ 报单操作请求(撤单), 注意,这是异步指令 """
        InputOrderAction = {'BrokerID': self.__BrokerID,  # 经纪公司代码
                            'UserID': self.__UserID,  # 用户代码
                            'InvestorID': self.__InvestorID,  # 投资者代码
                            'RequestID': self.__IncRequestID(),  # 请求编号
                            'ActionFlag': PyCTP.THOST_FTDC_AF_Delete,  # 操作标志:撤单
                            'OrderActionRef': int(self.__IncOrderActionRef()),  # 报单操作引用
                            'OrderRef': dict_arguments['OrderRef'],  # 报单引用（未成交挂单的报单引用）
                            'ExchangeID': dict_arguments['ExchangeID'],  # 交易所代码
                            'OrderSysID': dict_arguments['OrderSysID'],  # 报单编号（未成交挂单的报单编号）
                            }
        self.__rsp_OrderAction = dict(FrontID=self.__FrontID,  # 前置编号
                                      SessionID=self.__SessionID,  # 会话编号
                                      InputOrderAction=InputOrderAction,
                                      event=threading.Event())
        ret = self.ReqOrderAction(InputOrderAction, InputOrderAction['RequestID'])
        if ret == 0:
            # self.__rsp_OrderAction['event'].clear()
            if True:  # self.__rsp_OrderAction['event'].wait(self.TIMEOUT):
                print("PyCTP_Trade.OrderAction().self.__rsp_OrderAction=", self.__rsp_OrderAction)
                if 'ErrorID' in self.__rsp_OrderAction:
                    if self.__rsp_OrderAction['ErrorID'] != 0:
                        sys.stderr.write(str(self.__rsp_OrderInsert['ErrorMsg'], encoding='gb2312'))
                        return self.__rsp_OrderAction['ErrorID']
                    return self.__rsp_OrderAction.copy()
                else:
                    print("PyCTP_Trade.OrderAction() ErrorID is not in self.__rsp_OrderAction")
            else:
                return -4
        return ret
        pass

    # def OrderActionDelete(self, order):
    #     """ 撤销报单 """
    #     # OrderAction的再封装
    #     return super().OrderAction(PyCTP.THOST_FTDC_AF_Delete, order['FrontID'], order['SessionID'], order['OrderRef'],
    #                                order['ExchangeID'], order['OrderSysID'])
    def OnFrontConnected(self):
        """ 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。 """
        self.__rsp_Connect['event'].set()

    def OnFrontDisconnected(self, nReason):
        """ 当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
        nReason 错误原因
        0x1001 网络读失败
        0x1002 网络写失败
        0x2001 接收心跳超时
        0x2002 发送心跳失败
        0x2003 收到错误报文
        """
        sys.stderr.write('前置连接中断: %s' % hex(nReason))
        # 登陆状态时掉线, 自动重登陆
        # if self.__isLogined:
        # self.__Inst_Interval()
        # sys.stderr.write('自动登陆: %d' % self.Login(self.__BrokerID, self.__UserID, self.__Password))

    def OnRspUserLogin(self, RspUserLogin, RspInfo, RequestID, IsLast):
        """ 登录请求响应 """
        if RequestID == self.__rsp_Login['RequestID'] and IsLast:
            self.__BrokerID = RspUserLogin['BrokerID']
            self.__UserID = RspUserLogin['UserID']
            self.__InvestorID = RspUserLogin['UserID']
            self.__SystemName = RspUserLogin['SystemName']
            self.__TradingDay = RspUserLogin['TradingDay']
            self.__SessionID = RspUserLogin['SessionID']
            self.__MaxOrderRef = RspUserLogin['MaxOrderRef']
            # print(">>> PyCTP_Trade.OnRspUserLogin() RspUserLogin['MaxOrderRef'] =", type(RspUserLogin['MaxOrderRef']), RspUserLogin['MaxOrderRef'], "RspUserLogin =", RspUserLogin)
            print(">>> PyCtp_Trade.OnRspUserLogin() self.__MaxOrderRef =", self.__MaxOrderRef, type(self.__MaxOrderRef))
            self.__OrderRef = int(self.__MaxOrderRef)  # 初始化报单引用
            # self.__OrderRef = 0  # 初始化报单引用
            self.__OrderActionRef = int(self.__MaxOrderRef)
            # self.__OrderActionRef = 0
            self.__LoginTime = RspUserLogin['LoginTime']
            self.__FrontID = RspUserLogin['FrontID']
            self.__FFEXTime = RspUserLogin['FFEXTime']
            self.__CZCETime = RspUserLogin['CZCETime']
            self.__SHFETime = RspUserLogin['SHFETime']
            self.__DCETime = RspUserLogin['DCETime']
            self.__INETime = RspUserLogin['INETime']
            # print("PyCTP_Trade_API.OnRspUserLogin() user_id=", self.__UserID, "TradingDay=", self.__TradingDay, RspUserLogin)
            self.__rsp_Login.update(RspInfo)
            self.__rsp_Login['event'].set()

    def OnRspUserLogout(self, RspUserLogout, RspInfo, RequestID, IsLast):
        """ 登出请求响应 """
        if RequestID == self.__rsp_Logout['RequestID'] and IsLast:
            self.__rsp_Logout.update(RspInfo)
            self.__rsp_Logout['event'].set()

    def OnRspQryInstrument(self, Instrument, RspInfo, RequestID, IsLast):
        """ 请求查询合约响应 """
        # print('OnRspQryInstrument:', Instrument, IsLast)
        if RequestID == self.__rsp_QryInstrument['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInstrument.update(RspInfo)
            if Instrument is not None:
                self.__rsp_QryInstrument['results'].append(Instrument)
            if IsLast:
                self.__rsp_QryInstrument['event'].set()

    def OnRspQryInstrumentMarginRate(self, InstrumentMarginRate, RspInfo, RequestID, IsLast):
        """ 请求查询合约保证金率响应 """
        if RequestID == self.__rsp_QryInstrumentMarginRate['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInstrumentMarginRate.update(RspInfo)
            if InstrumentMarginRate is not None:
                self.__rsp_QryInstrumentMarginRate['results'].append(InstrumentMarginRate)
            if IsLast:
                self.__rsp_QryInstrumentMarginRate['event'].set()

    def OnRspQryInstrumentCommissionRate(self, InstrumentCommissionRate, RspInfo, RequestID, IsLast):
        """ 请求查询合约手续费率响应 """
        if RequestID == self.__rsp_QryInstrumentCommissionRate['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInstrumentCommissionRate.update(RspInfo)
            if InstrumentCommissionRate is not None:
                self.__rsp_QryInstrumentCommissionRate['results'].append(InstrumentCommissionRate)
            if IsLast:
                self.__rsp_QryInstrumentCommissionRate['event'].set()

    def OnRspQryOrder(self, Order, RspInfo, RequestID, IsLast):
        """请求查询报单响应"""
        # self.__user.OnRspQryOrder(Order, RspInfo, RequestID, IsLast)  # 转到user回调函数
        if RequestID == self.__rsp_QryOrder['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryOrder.update(RspInfo)
            if Order is not None:
                self.__rsp_QryOrder['results'].append(Order)
            if IsLast:
                self.__rsp_QryOrder['event'].set()
        Order = Utils.code_transform(Order)
        series_order = Series(Order)
        self.__df_qry_order = DataFrame.append(self.__df_qry_order, other=series_order, ignore_index=True)

    def OnRspQryTrade(self, Trade, RspInfo, RequestID, IsLast):
        """请求查询成交单响应"""
        # self.__user.OnRspQryTrade(Trade, RspInfo, RequestID, IsLast)  # 转到user回调函数
        if RequestID == self.__rsp_QryTrade['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryTrade.update(RspInfo)
            if Trade is not None:
                self.__rsp_QryTrade['results'].append(Trade)
            if IsLast:
                self.__rsp_QryTrade['event'].set()
        Trade = Utils.code_transform(Trade)
        series_trade = Series(Trade)
        self.__df_qry_trade = DataFrame.append(self.__df_qry_trade, other=series_trade, ignore_index=True)

    def OnRspQryInvestorPosition(self, InvestorPosition, RspInfo, RequestID, IsLast):
        """ 请求查询投资者持仓响应 """
        # self.__user.write_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'OnRspQryInvestorPosition', '查询投资者持仓响应', str(InvestorPosition))
        if RequestID == self.__rsp_QryInvestorPosition['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInvestorPosition.update(RspInfo)
            if InvestorPosition is not None:
                self.__rsp_QryInvestorPosition['results'].append(InvestorPosition)
            if IsLast:
                self.__rsp_QryInvestorPosition['event'].set()

    def OnRspQryInvestorPositionDetail(self, InvestorPositionDetail, RspInfo, RequestID, IsLast):
        """ 请求查询投资者持仓明细响应 """
        # self.__user.write_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'OnRspQryInvestorPositionDetail', '查询投资者持仓明细响应', str(InvestorPositionDetail))
        if RequestID == self.__rsp_QryInvestorPositionDetail['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInvestorPositionDetail.update(RspInfo)
            if InvestorPositionDetail is not None:
                self.__rsp_QryInvestorPositionDetail['results'].append(InvestorPositionDetail)
            if IsLast:
                self.__rsp_QryInvestorPositionDetail['event'].set()

    def OnRspQryTradingAccount(self, TradingAccount, RspInfo, RequestID, IsLast):
        """ 请求查询资金账户响应 """
        # self.__user.write_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'OnRspQryTradingAccount', '查询资金账户响应', str(TradingAccount))
        if RequestID == self.__rsp_QryTradingAccount['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryTradingAccount.update(RspInfo)
            if TradingAccount is not None:
                self.__rsp_QryTradingAccount['results'].append(TradingAccount)
            if IsLast:
                self.__rsp_QryTradingAccount['event'].set()

    def OnRspQryInvestor(self, Investor, RspInfo, RequestID, IsLast):
        """ 请求查询投资者响应 """
        if RequestID == self.__rsp_QryInvestor['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInvestor.update(RspInfo)
            if Investor is not None:
                self.__rsp_QryInvestor['results'].append(Investor)
            if IsLast:
                self.__rsp_QryInvestor['event'].set()

    def OnRspQryExchange(self, Exchange, RspInfo, RequestID, IsLast):
        """ 请求查询交易所响应 """
        if RequestID == self.__rsp_QryExchange['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryExchange.update(RspInfo)
            if Exchange is not None:
                self.__rsp_QryExchange['results'].append(Exchange)
            if IsLast:
                self.__rsp_QryExchange['event'].set()

    def OnRspQryDepthMarketData(self, DepthMarketData, RspInfo, RequestID, IsLast):
        """ 请求查询交易所响应 """
        if RequestID == self.__rsp_QryDepthMarketData['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryDepthMarketData.update(RspInfo)
            if DepthMarketData is not None:
                self.__rsp_QryDepthMarketData['results'].append(DepthMarketData)
            if IsLast:
                self.__rsp_QryDepthMarketData['event'].set()

    def OnRspQryTradingCode(self, TradingCode, RspInfo, RequestID, IsLast):
        """查询交易编码响应"""
        if RequestID == self.__rsp_QryTradingCode['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryTradingCode.update(RspInfo)
            if TradingCode is not None:
                self.__rsp_QryTradingCode['results'].append(TradingCode)
            if IsLast:
                self.__rsp_QryTradingCode['event'].set()

    def OnRspOrderInsert(self, InputOrder, RspInfo, RequestID, IsLast):
        """ 报单录入请求响应 """
        # 报单错误时响应
        # print('PyCTP_Trade.OnRspOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo, 'RequestID:', RequestID, 'IsLast:', IsLast)
        InputOrder = Utils.code_transform(InputOrder)
        RspInfo = Utils.code_transform(RspInfo)
        RequestID = Utils.code_transform(RequestID)
        IsLast = Utils.code_transform(IsLast)
        if self.__rsp_OrderInsert['RequestID'] == RequestID \
                and self.__rsp_OrderInsert['InputOrder']['OrderRef'].decode() == InputOrder['OrderRef']:
            if RspInfo is not None and RspInfo['ErrorID'] != 0:
                for i in self.__user.get_list_strategy():  # 转到strategy回调函数
                    if InputOrder['OrderRef'][-2:] == i.get_strategy_id():
                        i.OnRspOrderInsert(InputOrder, RspInfo, RequestID, IsLast)
                self.__rsp_OrderInsert.update(RspInfo)
                self.__rsp_OrderInsert['event'].set()

    def OnRspOrderAction(self, InputOrderAction, RspInfo, RequestID, IsLast):
        """报单操作请求响应:撤单操作响应"""
        InputOrderAction = Utils.code_transform(InputOrderAction)
        RspInfo = Utils.code_transform(RspInfo)
        RequestID = Utils.code_transform(RequestID)
        IsLast = Utils.code_transform(IsLast)
        print('PyCTP_Trade.OnRspOrderAction()', 'OrderRef:', InputOrderAction['OrderRef'], 'InputOrderAction:', InputOrderAction, 'RspInfo:', RspInfo, 'RequestID:', RequestID, 'IsLast:', IsLast)
        # if hasattr(self, '_PyCTP_Trader_API__rsp_OrderInsert'):
        # if self.__rsp_OrderAction['InputOrder']['OrderRef'] == InputOrderAction['OrderRef']:
        #     self.__rsp_OrderInsert['event'].set()
        for i in self.__user.get_list_strategy():  # 转到strategy回调函数
            if InputOrderAction['OrderRef'][-2:] == i.get_strategy_id():
                i.OnRspOrderAction(InputOrderAction, RspInfo, RequestID, IsLast)

    def OnRtnOrder(self, Order_input):
        """报单回报"""
        Order = copy.deepcopy(Order_input)
        print(">>>PyCTP_Trade.OnRtnOrder() Order =", Order)
        Order = Utils.code_transform(Order)
        # t = datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")
        # Order['time'] = t
        self.__user.OnRtnOrder(Order)  # 转回调给User类的OnRtnOrder
        # 未调用API OrderInsert之前还未生成属性_PyCTP_Trader_API__rsp_OrderInsert
        # if hasattr(self, '_PyCTP_Trader_API__rsp_OrderInsert'):
        # 报单回报过滤1、套利系统的服务端或客户端发送的委托；2、字段SystemID不为空
        # self.__user.OnRtnOrder(Order)  # 转到user回调函数
        # for i in self.__user.get_list_strategy():  # 转到strategy回调函数
        #     if Order['OrderRef'][-2:] == i.get_strategy_id():
        #         i.OnRtnOrder(Order)
        # series_order = Series(Order)
        # self.__df_order = DataFrame.append(self.__df_order, other=series_order, ignore_index=True)

    def OnRtnTrade(self, Trade_input):
        """成交回报"""
        Trade = copy.deepcopy(Trade_input)
        print(">>>PyCTP_Trade.OnRtnTrade() Trade =", Trade)
        Trade = Utils.code_transform(Trade)
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")
        # Trade['time'] = t
        if Utils.PyCTP_Trade_API_print:
            print('PyCTP_Trade.OnRtnTrade()', 'OrderRef:', Trade['OrderRef'], 'Time:', t, 'Trade:', Trade)
        self.__user.OnRtnTrade(Trade)  # 转到user回调函数
        # for i in self.__user.get_list_strategy():  # 转到strategy回调函数
        #     if Trade['OrderRef'][-2:] == i.get_strategy_id():
        #         i.OnRtnTrade(Trade)
        # series_trade = Series(Trade)
        # self.__df_trade = DataFrame.append(self.__df_trade, other=series_trade, ignore_index=True)

    # 将order和trade记录保存到本地
    def save_df_order_trade(self):
        str_user_id = self.__UserID.decode()
        str_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
        order_file_path = "data/order_" + str_user_id + "_" + str_time + '.csv'
        trade_file_path = "data/trade_" + str_user_id + "_" + str_time + '.csv'
        qry_order_file_path = "data/qry_order_" + str_user_id + "_" + str_time + '.csv'
        qry_trade_file_path = "data/qry_trade_" + str_user_id + "_" + str_time + '.csv'
        print(">>> PyCTP_Trade.save_df_order_trade() order_file_path =", order_file_path)
        print(">>> PyCTP_Trade.save_df_order_trade() trade_file_path =", trade_file_path)
        # self.__df_order.to_csv(order_file_path)
        # self.__df_trade.to_csv(trade_file_path)
        self.__df_qry_order.to_csv(qry_order_file_path)
        self.__df_qry_trade.to_csv(qry_trade_file_path)

    def OnErrRtnOrderAction(self, OrderAction, RspInfo):
        """ 报单操作错误回报 """
        if RspInfo is not None:
            RspInfo = Utils.code_transform(RspInfo)
        if OrderAction is not None:
            OrderAction = Utils.code_transform(OrderAction)
            dict_strategy = self.__user.get_dict_strategy()
            for strategy_id in dict_strategy:  # 转到strategy回调函数
                if OrderAction['OrderRef'][-2:] == dict_strategy[strategy_id].get_strategy_id():
                    dict_strategy[strategy_id].OnErrRtnOrderAction(OrderAction, RspInfo)
        if RspInfo is not None:
            RspInfo = Utils.code_transform(RspInfo)
        if Utils.PyCTP_Trade_API_print:
            print('PyCTP_Trade.OnErrRtnOrderAction()', 'OrderAction:', OrderAction, 'RspInfo:', RspInfo)
        #if not self.__rsp_OrderInsert['event'].is_set() and OrderAction['OrderActionStatus'] == PyCTP.THOST_FTDC_OST_Canceled:
        #    self.__rsp_OrderInsert['ErrorID'] = 79
        #    self.__rsp_OrderInsert['ErrorMsg'] = bytes('CTP:发送报单操作失败', 'gb2312')
        #    self.__rsp_OrderInsert['event'].set()

    def OnErrRtnOrderInsert(self, InputOrder, RspInfo):
        """报单录入错误回报"""
        # print('PyCTP_Trade.OnErrRtnOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo)
        if InputOrder is not None:
            InputOrder = Utils.code_transform(InputOrder)
        if RspInfo is not None:
            RspInfo = Utils.code_transform(RspInfo)
        if Utils.PyCTP_Trade_API_print:
            print('PyCTP_Trade.OnErrRtnOrderInsert()', 'InputOrder:', InputOrder, 'RspInfo:', RspInfo)
        self.__user.OnErrRtnOrderInsert(InputOrder, RspInfo)  # 转到user回调函数
        # for i in self.__user.get_list_strategy():  # 转到strategy回调函数
        #     if InputOrder['OrderRef'][-2:] == i.get_strategy_id():
        #         i.OnErrRtnOrderInsert(InputOrder, RspInfo)

    def OnRtnTradingNotice(self, TradingNoticeInfo):
        """ 交易通知 """
        print('PyCTP_Trade.OnRtnTradingNotice()', Utils.code_transform(TradingNoticeInfo))
        pass

    dfInstrumentStatus = DataFrame()  # 保存InstrumentStatus的全局变量
    dfInstrument = DataFrame()  # 保存Instrument的全局变量

    def OnRtnExecOrder(self, ExecOrder):
        """执行宣告通知"""
        print('OnRtnExecOrder()', ExecOrder)

    def OnRtnInstrumentStatus(self, InstrumentStatus):
        # """合约交易状态通知"""
        # 将查询结果用df保存
        series_InstrumentStatus = Series(InstrumentStatus)
        PyCTP_Trader_API.dfInstrumentStatus = pd.DataFrame.append(PyCTP_Trader_API.dfInstrumentStatus,
                                                                  other=series_InstrumentStatus,
                                                                  ignore_index=True)

    # 设置user为成员变量
    def set_user(self, user):
        self.__user = user

    # 将strategy实例的list设置为本类属性，在strategy实例中实现OnRtnXxx的回调函数
    def set_list_strategy(self, list_strategy):
        self.__list_strategy = list_strategy

    # 获取前置编号
    def get_front_id(self):
        return self.__FrontID

    # 获取会话编号
    def get_session_id(self):
        return self.__SessionID

    # 获取交易日
    def get_TradingDay(self):
        return self.__TradingDay

    # 为了解决错误而实现的函数
    # AttributeError: 'PyCTP_Trader_API' object has no attribute 'OnRspError'
    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        print("PyCTP_Trade.OnRspError() pRspInfo=", Utils.code_transform(pRspInfo), "nRequestID=", nRequestID, "bIsLast=", bIsLast)
        return None

