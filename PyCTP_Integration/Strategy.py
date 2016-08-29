# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:46:13 2016

@author: YuWanying
"""


from PyCTP_Trade import PyCTP_Trader_API
from PyCTP_Market import PyCTP_Market_API
from OrderAlgorithm import OrderAlgorithm
import PyCTP


class Strategy:
    # class Strategy功能:接收行情，接收Json数据，触发交易信号，将交易任务交给OrderAlgorithm
    # 形参{'trader_id': '1601', 'user_id': '800658', 'strategy_id': '01', 'order_algorithm':'01', 'list_instrument_id': ['cu1611', 'cu1610']}
    def __init__(self, dict_arguments, obj_user, obj_DBM):
        self.__DBM = obj_DBM  # 数据库连接实例
        self.__user = obj_user  # user实例
        self.__dict_arguments = dict_arguments  # 转存形参到类的私有变量

        self.__trader_id = dict_arguments['trader_id']
        self.__user_id = dict_arguments['user_id']
        self.__strategy_id = dict_arguments['strategy_id']
        self.__order_algorithm = dict_arguments['order_algorithm']  # 下单算法选择标志位
        self.__list_instrument_id = dict_arguments['list_instrument_id']  # 合约列表
        self.__buy_open = dict_arguments['buy_open']  # 触发买开（开多单）
        self.__sell_close = dict_arguments['sell_close']  # 触发卖平（平多单）
        self.__sell_open = dict_arguments['sell_open']  # 触发卖开（开空单）
        self.__buy_close = dict_arguments['buy_close']  # 触发买平（平空单）
        self.__spread_shift = dict_arguments['spread_shift']  # 价差让价
        self.__stop_loss = dict_arguments['stop_loss']  # 止损，单位为最小跳数
        self.__lots = dict_arguments['lots']  # 总手
        self.__lots_batch = dict_arguments['lots_batch']  # 每批下单手数
        self.__is_active = dict_arguments['is_active']  # 策略开关状态
        self.__order_action_tires_limit = dict_arguments['order_action_tires_limit']  # 撤单次数限制
        self.__only_close = dict_arguments['only_close']  # 只能平仓
        self.__position_a_buy_today = dict_arguments['position_a_buy_today']  # A合约买持仓今仓
        self.__position_a_buy_yesterday = dict_arguments['position_a_buy_yesterday']  # A合约买持仓昨仓
        self.__position_a_buy = dict_arguments['position_a_buy']  # A合约买持仓总仓位
        self.__position_a_sell_today = dict_arguments['position_a_sell_today']  # A合约卖持仓今仓
        self.__position_a_sell_yesterday = dict_arguments['position_a_sell_yesterday']  # A合约卖持仓昨仓
        self.__position_a_sell = dict_arguments['position_a_sell']  # A合约卖持仓总仓位
        self.__position_b_buy_today = dict_arguments['position_b_buy_today']  # B合约买持仓今仓
        self.__position_b_buy_yesterday = dict_arguments['position_b_buy_yesterday']  # B合约买持仓昨仓
        self.__position_b_buy = dict_arguments['position_b_buy']  # B合约买持仓总仓位
        self.__position_b_sell_today = dict_arguments['position_b_sell_today']  # B合约卖持仓今仓
        self.__position_b_sell_yesterday = dict_arguments['position_b_sell_yesterday']  # B合约卖持仓昨仓
        self.__position_b_sell = dict_arguments['position_b_sell']  # B合约卖持仓总仓位

        self.__instrument_a_tick = None  # A合约tick（第一腿）
        self.__instrument_b_tick = None  # B合约tick（第二腿）
        self.__spread_long = None  # 市场多头价差：A合约买一价 - B合约买一价
        self.__spread_long_volume = None  # 市场多头价差盘口挂单量min(A合约买一量 - B合约买一量)
        self.__spread_short = None  # 市场空头价差：A合约卖一价 - B合约卖一价
        self.__spread_short_volume = None  # 市场空头价差盘口挂单量：min(A合约买一量 - B合约买一量)
        self.__spread = None  # 市场最新价价差

        self.__order_ref_part2 = 0  # 报单引用，（从第三位到最后一位，[1:]）
        self.__order_ref_last = None  # 最后一次实际使用的报单引用
        self.__order_ref_a = None  # A合约报单引用
        self.__order_ref_b = None  # B合约报单引用

        self.add_dict_instrument_action_counter(dict_arguments['list_instrument_id'])  # 将合约代码添加到user类的合约列表

        # set_arguments()中不存在的私有变量
        self.__trade_tasking = False  # 交易任务进行中
        self.__a_order_insert_args = dict()  # a合约报单参数
        self.__b_order_insert_args = dict()  # b合约报单参数
        self.__list_order_pending = list()  # 挂单列表，报单回报写入，成交回报删除

    # 设置参数
    def set_arguments(self, dict_arguments):
        self.__dict_arguments = dict_arguments  # 将形参转存为私有变量
        self.__DBM.update_strategy(dict_arguments)  # 更新数据库
        self.__dict_arguments = dict_arguments  # 转存形参到类的私有变量

        self.__trader_id = dict_arguments['trader_id']
        self.__user_id = dict_arguments['user_id']
        self.__strategy_id = dict_arguments['strategy_id']
        self.__order_algorithm = dict_arguments['order_algorithm']  # 下单算法选择标志位
        self.__list_instrument_id = dict_arguments['list_instrument_id']  # 合约列表
        self.__buy_open = dict_arguments['buy_open']  # 触发买开（开多单）
        self.__sell_close = dict_arguments['sell_close']  # 触发卖平（平多单）
        self.__sell_open = dict_arguments['sell_open']  # 触发卖开（开空单）
        self.__buy_close = dict_arguments['buy_close']  # 触发买平（平空单）
        self.__spread_shift = dict_arguments['spread_shift']  # 价差让价
        self.__stop_loss = dict_arguments['stop_loss']  # 止损，单位为最小跳数
        self.__lots = dict_arguments['lots']  # 总手
        self.__lots_batch = dict_arguments['lots_batch']  # 每批下单手数
        self.__is_active = dict_arguments['is_active']  # 策略开关状态
        self.__order_action_tires_limit = dict_arguments['order_action_tires_limit']  # 撤单次数限制
        self.__only_close = dict_arguments['only_close']  # 只能平仓
        self.__position_a_buy_today = dict_arguments['position_a_buy_today']  # A合约买持仓今仓
        self.__position_a_buy_yesterday = dict_arguments['position_a_buy_yesterday']  # A合约买持仓昨仓
        self.__position_a_buy = dict_arguments['position_a_buy']  # A合约买持仓总仓位
        self.__position_a_sell_today = dict_arguments['position_a_sell_today']  # A合约卖持仓今仓
        self.__position_a_sell_yesterday = dict_arguments['position_a_sell_yesterday']  # A合约卖持仓昨仓
        self.__position_a_sell = dict_arguments['position_a_sell']  # A合约卖持仓总仓位
        self.__position_b_buy_today = dict_arguments['position_b_buy_today']  # B合约买持仓今仓
        self.__position_b_buy_yesterday = dict_arguments['position_b_buy_yesterday']  # B合约买持仓昨仓
        self.__position_b_buy = dict_arguments['position_b_buy']  # B合约买持仓总仓位
        self.__position_b_sell_today = dict_arguments['position_b_sell_today']  # B合约卖持仓今仓
        self.__position_b_sell_yesterday = dict_arguments['position_b_sell_yesterday']  # B合约卖持仓昨仓
        self.__position_b_sell = dict_arguments['position_b_sell']  # B合约卖持仓总仓位

        self.add_dict_instrument_action_counter(dict_arguments['list_instrument_id'])  # 将合约代码添加到user类的合约列表

        self.__order_ref_part2 = 0  # 报单引用，（从第三位到最后一位，[1:]）
        self.__order_ref_last = None  # 最后一次实际使用的报单引用
        self.__order_ref_a = None  # A合约报单引用
        self.__order_ref_b = None  # B合约报单引用

    # 获取参数
    def get_arguments(self):
        return self.__dict_arguments

    # 设置数据库连接实例
    def set_DBM(self, DBM):
        self.__DBM = DBM

    # 获取数据库连接实例
    def get_DBM(self):
        return self.__DBM

    # 设置user对象
    def set_user(self, user):
        self.__user = user

    # 获取user对象
    def get_user(self, user):
        return self.__user

    # 获取trader_id
    def get_trader_id(self):
        return self.__trader_id

    # 获取user_id
    def get_user_id(self):
        return self.__user_id

    # 获取strategy_id
    def get_strategy_id(self):
        return self.__strategy_id

    # 获取self.__list_instrument_id
    def get_list_instrument_id(self):
        return self.__list_instrument_id

    # 添加合约代码到user类的self.__dict_instrument_action_counter
    def add_dict_instrument_action_counter(self, list_instrument_id):
        for i in list_instrument_id:
            if i not in self.__user.get_dict_instrument_action_counter():
                self.__user.get_dict_instrument_action_counter()[i] = 0

    # 生成报单引用，前两位是策略编号，后面几位递增1
    def add_order_ref(self):
        self.__order_ref_part2 += 1
        return (self.__strategy_id + str(self.__order_ref_part2)).encode()

    # 回调函数：行情推送
    def OnRtnDepthMarketData(self, tick):
        """ 行情推送 """
        # 过滤出B合约的tick
        if tick['InstrumentID'] == self.__list_instrument_id[1]:
            self.__instrument_b_tick = tick
            # print(self.__user_id + self.__strategy_id, "B合约：", self.__instrument_b_tick)
        # 过滤出A合约的tick
        elif tick['InstrumentID'] == self.__list_instrument_id[0]:
            self.__instrument_a_tick = tick
            # print(self.__user_id + self.__strategy_id, "A合约：", self.__instrument_a_tick)
        # 选择下单算法
        self.select_order_algorithm(self.__order_algorithm)
        # 下单任务进行中被行情驱动
        if self.__trade_tasking:
            dict_arguments = {'flag': tick, 'tick': tick}
            self.trade_task(dict_arguments)
        # 打印价差
        # print(self.__user_id + self.__strategy_id, self.__list_instrument_id, self.__spread_long, "(", self.__spread_long_volume, ")", self.__spread_short, "(", self.__spread_short_volume, ")")

    def OnRspOrderInsert(self, InputOrder, RspInfo, RequestID, IsLast):
        """ 报单录入请求响应 """
        # 报单错误时响应
        print('Strategy.OnRspOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo, 'RequestID:', RequestID, 'IsLast:', IsLast)
        dict_arguments = {'flag': 'OnRspOrderInsert',
                          'InputOrder': InputOrder,
                          'RspInfo': RspInfo,
                          'RequestID': RequestID,
                          'IsLast': IsLast}
        self.trade_task(dict_arguments)  # 转到交易任务处理

    def OnRspOrderAction(self, InputOrderAction, RspInfo, RequestID, IsLast):
        """报单操作请求响应:撤单操作响应"""
        print('Strategy.OnRspOrderAction()', 'OrderRef:', InputOrderAction['OrderRef'], 'InputOrderAction:', InputOrderAction, 'RspInfo:', RspInfo, 'RequestID:', RequestID, 'IsLast:', IsLast)
        dict_arguments = {'flag': 'OnRspOrderAction',
                          'InputOrderAction': InputOrderAction,
                          'RspInfo': RspInfo,
                          'RequestID': RequestID,
                          'IsLast': IsLast}
        self.trade_task(dict_arguments)  # 转到交易任务处理

    def OnRtnOrder(self, Order):
        """报单回报"""
        from User import User
        print('Strategy.OnRtnOrder()', 'OrderRef:', Order['OrderRef'], 'Order', Order)
        dict_arguments = {'flag': 'OnRtnOrder',
                          'Order': Order}
        self.trade_task(dict_arguments)  # 转到交易任务处理

    def OnRtnTrade(self, Trade):
        """成交回报"""
        print('Strategy.OnRtnTrade()', 'OrderRef:', Trade['OrderRef'], 'Trade', Trade)
        dict_arguments = {'flag': 'OnRtnTrade',
                          'Trade': Trade}
        self.trade_task(dict_arguments)  # 转到交易任务处理

    def OnErrRtnOrderAction(self, OrderAction, RspInfo):
        """ 报单操作错误回报 """
        print('Strategy.OnErrRtnOrderAction()', 'OrderRef:', OrderAction['OrderRef'], 'OrderAction:', OrderAction, 'RspInfo:', RspInfo)
        dict_arguments = {'flag': 'OnErrRtnOrderAction',
                          'OrderAction': OrderAction,
                          'RspInfo': RspInfo}
        self.trade_task(dict_arguments)  # 转到交易任务处理

    def OnErrRtnOrderInsert(self, InputOrder, RspInfo):
        """报单录入错误回报"""
        print('Strategy.OnErrRtnOrderInsert()', 'OrderRef:', InputOrder['OrderRef'], 'InputOrder:', InputOrder, 'RspInfo:', RspInfo)
        dict_arguments = {'flag': 'OnErrRtnOrderInsert',
                          'InputOrder': InputOrder,
                          'RspInfo': RspInfo}
        self.trade_task(dict_arguments)  # 转到交易任务处理

    def trade_task(self, dict_arguments):
        """"交易任务执行"""
        # 报单
        if dict_arguments['flag'] == 'OrderInsert':
            """交易任务开始入口"""
            print('Strategy.trade_task()下单任务开始，参数：', dict_arguments)
            self.__user.get_trade().OrderInsert(dict_arguments)  # A合约报单
        # 报单录入请求响应
        elif dict_arguments['flag'] == 'OnRspOrderInsert':
            print("Strategy.trade_task()报单录入请求响应")
            pass
        # 报单操作请求响应
        elif dict_arguments['flag'] == 'OnRspOrderAction':
            print("Strategy.trade_task()报单操作请求响应")
            pass
        # 报单回报
        elif dict_arguments['flag'] == 'OnRtnOrder':
            self.__list_order_pending = self.update_list_order_pending(dict_arguments)  # 更新挂单list
            # if len(dict_arguments['Order']['OrderSysID']) == 12 and dict_arguments['Order']['VolumeTraded'] == 0:
            #     self.__list_order_pending.append(dict_arguments['Order'])  # 收到报单交易所发来的已成交量为0的报单回报，将其加入到挂单列表
        # 成交回报
        elif dict_arguments['flag'] == 'OnRtnTrade':
            print('Strategy.trade_task()成交回报：', dict_arguments['Trade'])
            self.__list_order_pending = self.update_list_order_pending(dict_arguments)  # 更新挂单list
            # 从self.__list_order_pending找到OrderRef相同的记录，将挂单量减去已成交量，结果为0的记录删除
            # A成交回报
            if dict_arguments['Trade']['InstrumentID'] == self.__list_instrument_id[0]:
                if dict_arguments['Trade']['OffsetFlag'] == '0':  # A开仓成交回报
                    if dict_arguments['Trade']['Direction'] == '0':  # A买开仓成交回报
                        self.__position_a_buy_today += dict_arguments['Trade']['Volume']  # 更新持仓
                    elif dict_arguments['Trade']['Direction'] == '1':  # A卖开仓成交回报
                        self.__position_a_sell_today += dict_arguments['Trade']['Volume']  # 更新持仓
                elif dict_arguments['Trade']['OffsetFlag'] == '3':  # A平今成交回报
                    if dict_arguments['Trade']['Direction'] == '0':  # A买平今成交回报
                        self.__position_a_sell_today -= dict_arguments['Trade']['Volume']  # 更新持仓
                    elif dict_arguments['Trade']['Direction'] == '1':  # A卖平今成交回报
                        self.__position_a_buy_today -= dict_arguments['Trade']['Volume']  # 更新持仓
                elif dict_arguments['Trade']['OffsetFlag'] == '4':  # A平昨成交回报
                    if dict_arguments['Trade']['Direction'] == '0':  # A买平昨成交回报
                        self.__position_a_sell_yesterday -= dict_arguments['Trade']['Volume']  # 更新持仓
                    elif dict_arguments['Trade']['Direction'] == '1':  # A卖平昨成交回报
                        self.__position_a_buy_yesterday -= dict_arguments['Trade']['Volume']  # 更新持仓
                b_order_insert_args = self.__b_order_insert_args  # B报单参数转存到临时变量维护
                self.__order_ref_b = self.add_order_ref()  # B报单引用
                self.__order_ref_last = self.__order_ref_b  # 实际最后使用的报单引用
                b_order_insert_args['OrderRef'] = self.__order_ref_b  # B报单引用
                b_order_insert_args['VolumeTotalOriginal'] = dict_arguments['Trade']['VolumeTraded']  # B报单手数
                self.__user.get_trade().OrderInsert(b_order_insert_args)  # B合约报单
            # B成交回报
            if dict_arguments['Trade']['InstrumentID'] == self.__list_instrument_id[1]:
                # B开仓成交回报

                # B平仓成交回报

                    # B平今成交回报

                    # B平昨成交回报

                pass
        # 报单录入错误回报
        elif dict_arguments['flag'] == 'OnErrRtnOrderInsert':
            print("Strategy.trade_task()报单录入错误回报")
        # 报单操作错误回报
        elif dict_arguments['flag'] == 'OnErrRtnOrderAction':
            print("Strategy.trade_task()报单操作错误回报")
        # 行情
        elif dict_arguments['flag'] == 'tick':
            """当交易任务进行中时，判断是否需要撤单"""
            # A有挂单，判断是否需要撤单

            # B有挂单，判断是否需要撤单，并重新发单，启动一定成交策略

            pass

        # 若无挂单、无撇退，则交易任务已完成
        # if True:
        #     self.__trade_tasking = False

    # 选择下单算法
    def select_order_algorithm(self, flag):
        # 交易任务进行中则不执行新的交易算法
        if self.__trade_tasking:
            return
        # 选择执行交易算法
        if flag == '01':
            self.order_algorithm_one()
        elif flag == '02':
            self.order_algorithm_two()
        elif flag == '03':
            self.order_algorithm_three()
        else:
            print("Strategy.select_order_algorithm()没有选择下单算法")

    # 下单算法1：A合约以对手价发单，B合约以对手价发单
    def order_algorithm_one(self):
        # 计算市场盘口价差、量
        if self.__instrument_a_tick is not None and self.__instrument_b_tick is not None:
            self.__spread_long = self.__instrument_a_tick['BidPrice1'] - self.__instrument_b_tick['AskPrice1']
            self.__spread_long_volume = min(self.__instrument_a_tick['BidVolume1'],
                                            self.__instrument_b_tick['AskVolume1'])
            self.__spread_short = self.__instrument_a_tick['AskPrice1'] - self.__instrument_b_tick['BidPrice1']
            self.__spread_short_volume = min(self.__instrument_a_tick['AskVolume1'],
                                             self.__instrument_b_tick['BidVolume1'])
        else:
            return None

        # 价差卖平
        if self.__spread_long >= self.__sell_close\
                and self.__position_a_buy > 0 \
                and self.__position_a_buy == self.__position_b_sell \
                and self.__position_a_buy + self.__position_b_buy < self.__lots\
                and False:
            '''
            市场空头价差大于参数
            A合约买持仓大于0
            A合约买持仓等于B合约卖持仓
            A合约买持仓加B合约买小于总仓位
            '''
            print("Strategy.交易信号触发", "价差卖平")
            # 满足交易任务之前的一个tick
            self.__instrument_a_tick_after_tasking = self.__instrument_a_tick
            self.__instrument_b_tick_after_tasking = self.__instrument_b_tick
            # 报单手数：盘口挂单量、每份发单手数中取最小值
            order_volume = min(self.__spread_short_volume, self.__lots_batch)
            self.__order_ref_last = self.add_order_ref()  # 报单引用
            # 优先平昨
            if self.__position_a_buy_yesterday == 0:
                order_volume = min(order_volume, self.__position_a_buy_today)
                CombOffsetFlag = b'3'
            elif self.__position_a_buy_yesterday > 0:
                order_volume = min(order_volume, self.__position_a_buy_yesterday)
                CombOffsetFlag = b'4'
            if order_volume <= 0 or not isinstance(order_volume, int):
                print('Strategy.order_algorithm_one()发单手数错误值', order_volume)

            # 测试部分代码开始，人为赋值
            order_volume = 1  # 发单手数
            CombOffsetFlag = b'0'  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
            # 测试部分代码截止
            a_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                   'OrderRef': self.__order_ref_last,  # 报单引用
                                   'InstrumentID': self.__list_instrument_id[0].encode(),  # 合约代码
                                   'LimitPrice': self.__instrument_a_tick['BidPrice1'],  # 限价
                                   'VolumeTotalOriginal': order_volume,  # 数量
                                   'Direction': b'1',  # 买卖，0买,1卖
                                   'CombOffsetFlag': CombOffsetFlag,  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                   'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                   }
            self.trade_task(a_order_insert_args)  # 执行下单任务
            self.__trade_tasking = True  # 交易任务执行中
        # 价差买平
        elif self.__spread_short <= self.__buy_close\
                and False:
            print("Strategy.交易信号触发", "价差买平")
            pass
        # 价差卖开
        elif True:
            # self.__spread_long >= self.__sell_open\
            # and self.__position_a_buy + self.__position_a_sell < self.__lots:
            '''
            市场多头价差大于触发参数
            A合约买持仓加B合约买小于总仓位
            '''
            print("Strategy.交易信号触发", "价差卖开")
            # 打印价差
            print(self.__user_id + self.__strategy_id, self.__list_instrument_id, self.__spread_long, "(", self.__spread_long_volume, ")", self.__spread_short, "(", self.__spread_short_volume, ")")
            # 满足交易任务之前的一个tick
            self.__instrument_a_tick_after_tasking = self.__instrument_a_tick
            self.__instrument_b_tick_after_tasking = self.__instrument_b_tick
            # 报单手数：盘口挂单量、每份发单手数、剩余可开仓手数中取最小值
            order_volume = min(self.__spread_long_volume,
                               self.__lots_batch,
                               self.__lots - (self.__position_a_buy + self.__position_b_buy))
            if order_volume <= 0 or not isinstance(order_volume, int):
                print('Strategy.order_algorithm_one()发单手数错误值', order_volume)
            self.__order_ref_a = self.add_order_ref()  # 报单引用
            self.__order_ref_last = self.__order_ref_a
            # A合约报单参数，全部确定
            self.__a_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          'OrderRef': self.__order_ref_a,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[0].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_a_tick['BidPrice1'],  # 限价
                                          'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'1',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            # B合约报单参数，部分确定，报单引用和报单数量，根据A合约成交情况确定
            self.__b_order_insert_args = {'flag': 'OrderInsert',  # 标志位：报单
                                          # 'OrderRef': self.__order_ref_b,  # 报单引用
                                          'InstrumentID': self.__list_instrument_id[1].encode(),  # 合约代码
                                          'LimitPrice': self.__instrument_b_tick['AskPrice1'],  # 限价
                                          # 'VolumeTotalOriginal': order_volume,  # 数量
                                          'Direction': b'0',  # 买卖，0买,1卖
                                          'CombOffsetFlag': b'0',  # 组合开平标志，0开仓，上期所3平今、4平昨，其他交易所1平仓
                                          'CombHedgeFlag': b'1',  # 组合投机套保标志:1投机、2套利、3保值
                                          }
            self.trade_task(self.__a_order_insert_args)  # 执行下单任务
            self.__trade_tasking = True  # 交易任务执行中
        # 价差买开
        elif self.__spread_long >= self.__buy_open:
            print("Strategy.交易信号触发", "价差买开")
            pass

    # 下单算法2：A合约以最新成交价发单，B合约以对手价发单
    def order_algorithm_two(self):
        print("Strategy.order_algorithm_two()")
        pass

    # 下单算法3：A合约以挂单价发单，B合约以对手价发单
    def order_algorithm_three(self):
        print("Strategy.order_algorithm_three()")
        pass

    # 更新挂单列表
    def update_list_order_pending(self, dict_arguments):
        # 报单回报和撤单回报
        if dict_arguments['flag'] == 'OnRtnOrder' and len(dict_arguments['OnRtnOrder']['OrderSysID']) == 12:
            # 开仓委托回报，交易所发来，字段OrderSysId有内容

            # 撤单委托回报，交易所发来

            pass
        # 成交回报，从挂单列表中删除记录
        elif dict_arguments['flag'] == 'OnRtnTrade':
            for i in self.__list_order_pending:
                if i['OrderRef'] == dict_arguments['OnRtnTrade']['OrderRef']:  # 从挂单列表中找到OrderRef相同的记录
                    pass
        return self.__list_order_pending

    # 更新持仓量变量，共12个变量
    def update_position(self, dict_arguments):
        if dict_arguments['flag'] == 'OnRtnTrade':
            pass


