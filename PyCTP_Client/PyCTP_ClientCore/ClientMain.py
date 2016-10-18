import sys
from CTPManager import CTPManager
from PyQt4 import QtGui
from PyQt4 import QtCore
import QLogin  # from QLogin import QLoginForm
from QCTP import QCTP
from QAccountWidget import QAccountWidget
from SocketManager import SocketManager
import json
import time
import threading
from MarketManager import MarketManager
from Trader import Trader
from User import User
from Strategy import Strategy


class ClientMain(QtCore.QObject):
    def __init__(self, parent=None):
        super(ClientMain, self).__init__(parent) #显示调用父类初始化方法，使用其信号槽机制

    def set_SocketManager(self, obj_sm):
        self.__sm = obj_sm
        obj_sm.signal_send_message.connect(self.slot_output_message)

    def set_QLoginForm(self, qloginform):
        self.__QLoginForm = qloginform

    def set_QCTP(self, obj_QCTP):
        self.__QCTP = obj_QCTP

    def set_QAccountWidget(self, obj_QAccountWidget):
        self.__QAccoutWidget = obj_QAccountWidget

    def set_dict_QAccountWidget(self, dict_QAccountWidget):
        self.__dict_QAccountWidget = dict_QAccountWidget

    def set_QOrderWidget(self, obj_QOrderWidget):
        self.__QOrderWidget = obj_QOrderWidget

    def set_CTPManager(self, obj_CTPManager):
        self.__CTPManager = obj_CTPManager

    def get_SocketManager(self):
        return self.__sm

    def get_QLoginForm(self):
        return self.__QLoginForm

    def get_QCTP(self):
        return self.__QCTP

    def get_QAccoutWidget(self):
        return self.__QAccoutWidget

    def get_QOrderWidget(self):
        return self.__QOrderWidget

    def get_CTPManager(self):
        return self.__CTPManager

    """
    # 创建行情管理器
    def create_market_manager(self, dict_args):
        pass

    # 创建user
    def create_user(self, dict_args):
        pass

    # 创建trader
    def create_trader(self, args):
        self.__trader = Trader(args)

    # 创建strategy
    def create_strategy(self, dict_args):
        pass
    """

    # 处理socket_manager发来的消息
    @QtCore.pyqtSlot(dict)
    def slot_output_message(self, buff):
        print("ClientMain.slot_output_message()", buff)
        if buff['MsgType'] == 1:  # TraderInfo
            # print("ClientMain.slot_output_message() buff['MsgType'] == 1, TraderInfo")
            # 单个trader：将收到的数据存入数据库，存入之前清空数据库文档
            self.__CTPManager.get_mdb().get_col_trader().remove()  # 从数据库删除数据
            self.__CTPManager.get_mdb().get_col_trader().insert({buff['Info']})  # 存入数据到数据库，是一个dict
            self.__CTPManager.create_trader(buff['Info'])  # 创建一个交易员实例

        elif buff['MsgType'] == 2:  # UserInfo
            # print("ClientMain.slot_output_message() buff['MsgType'] == 2, UserInfo")
            # user集合：将收到的数据存入数据库，存入之前清空数据库文档
            self.__CTPManager.get_mdb().get_col_user().remove()  # 从数据库删除数据
            for i in buff['Info']:
                self.__CTPManager.get_mdb().get_col_user().insert(i)  # 存入数据到数据库，是一个list，内含多个dict
                self.__CTPManager.create_user(i)  # 创建交易员实例
                self.__dict_QAccountWidget = {i['user_id']: QAccountWidget()}  # 创建单个账户的QAccountWidget()
                for j in self.__CTPManager.get_list_user():
                    if j.get_user_id().decode() == i['user_id']:
                        self.__dict_QAccountWidget[i['user_id']].set_user(j)  # user对象设置为对应窗口对象的属性
                        self.__dict_QAccountWidget[i['user_id']].set_widget_name(i['user_id'])  # 设置窗口属性"widget_name"
                self.get_QLoginForm().set_dict_QAccountWidget(self.__dict_QAccountWidget)  # dict_QAccountWidget设置为QLoginForm属性
                self.__QCTP.tab_accounts.addTab(self.__dict_QAccountWidget[i['user_id']], i['user_id'])  # 账户窗口添加到QCTP窗口的tab
            self.__dict_QAccountWidget = {'总账户': QAccountWidget()}  # 创建总账户的QAccountWidget()，存放到dict
            self.__QCTP.tab_accounts.insertTab(0, self.__dict_QAccountWidget['总账户'], '总账户')  # 总账户窗口插入到tab，位置0
            self.__dict_QAccountWidget['总账户'].set_widget_name('总账户')  # 设置窗口属性"widget_name"

        elif buff['MsgType'] == 3:  # StrategyInfo，创建Strategy实例
            # print("ClientMain.slot_output_message() buff['MsgType'] == 3, StrategyInfo")
            # 更新数据库，将StraetgyInfo消息转给对应的user
            # self.__CTPManager.get_mdb().get_col_strategy().remove()  # 从数据库删除数据
            for i in buff['Info']:
                # buff['Info']是list，内包含多个strategy信息，一批限制为30k个，可以分批发送，总数无限大
                self.__CTPManager.create_strategy(i)  # 创建策略实例
                for j in self.__CTPManager.get_list_user():  # 遍历user实例列表
                    if j.get_user_id() == i['user_id']:  # 找到对应的user实例
                        j.get_col_strategy.insert(i)  # 将strategy参数存入到本地数据库

        elif buff['MsgType'] == 7:  # StrategyInfo，更新Strategy参数
            for i in buff['Info']:
                # buff['Info']是list，内包含多个strategy信息，总数限制为30k个
                # 将策略更新到数据库中的集合col_strategy，通过user类的数据库连接实例操作
                for j in self.__CTPManager.get_list_user():  # 遍历ctp管理类的user实例列表
                    if j.get_user_id() == i['user_id']:  # 找到对应的user
                        j.get_col_strategy.update({'user_id': i['user_id']}, i)  # 更新本地数据库中策略参数文档
                        for k in j.get_list_strategy():  # 遍历user的策略实例列表
                            if k.get_strategy_id == i['strategy_id']:  # 找到对应的strategy
                                k.set_arguments(i)  # 更新strategy类的参数

        elif buff['MsgType'] == 4:  # trader登录
            if buff['MsgResult'] == 0:  # 登录结果为成功
                # print("ClientMain.slot_output_message() buff['MsgType'] == 4, trader登录")
                self.__QLoginForm.hide()
                self.__QCTP.show()

                # 模拟登陆成功之后服务端给客户端发送信息，客户端用来初始化

                # 发送MarketInfo
                dict_MarketInfo = {'MsgRef': self.__sm.msg_ref_add(),
                                   'MsgSendFlag': 0,  # 0:c2s、1:s2c
                                   'MsgType': 6,  # 消息类型为PositionInfo
                                   'MsgResult': 0,  # 0：成功、1：失败
                                   'MsgErrorReason': 'None',
                                   'Info':
                                       [
                                           {'front_address': 'tcp://180.168.146.187:10010',
                                            'broker_id': '9999',
                                            'user_id': '',
                                            'password': ''
                                            }
                                       ]
                                   }
                json_PositionInfo = json.dumps(dict_MarketInfo)
                self.__sm.send_msg(json_PositionInfo)

                # 发送UserInfo
                dict_UserInfo = {'MsgRef': self.__sm.msg_ref_add(),
                                 'MsgSendFlag': 0,
                                 'MsgType': 2,  # 消息类型为UserInfo
                                 'MsgResult': 0,  # 0：成功、1：失败
                                 'MsgErrorReason': 'ID or password error',
                                 'Info':
                                     [
                                         {'user_id': '063802',
                                          'password': '123456',
                                          'front_address': 'tcp://180.168.146.187:10000',
                                          'broker_id': '9999',
                                          'trader_id': '1601'
                                          },
                                         {'user_id': '058176',
                                          'password': '669822',
                                          'front_address': 'tcp://180.168.146.187:10000',
                                          'broker_id': '9999',
                                          'trader_id': '1601'
                                          }
                                     ]
                                 }
                json_UserInfo = json.dumps(dict_UserInfo)
                self.__sm.send_msg(json_UserInfo)

                # 发送StrategyInfo
                dict_StrategyInfo = {'MsgRef': 1,  # self.__sm.msg_ref_add(),
                                     'MsgSendFlag': 0,
                                     'MsgType': 3,  # 消息类型为StrategyInfo
                                     'MsgResult': 0,  # 0：成功、1：失败
                                     'MsgErrorReason': 'ID or password error',
                                     'Info':
                                         [
                                             {"position_a_sell_today": 0,
                                              "position_b_sell": 0,
                                              "spread_shift": 0,
                                              "position_b_sell_today": 0,
                                              "position_b_buy_today": 0,
                                              "position_a_sell": 0,
                                              "buy_close": 9000,
                                              "stop_loss": 0,
                                              "position_b_buy_yesterday": 0,
                                              "is_active": 1,
                                              "position_b_sell_yesterday": 0,
                                              "strategy_id": "02",
                                              "position_b_buy": 0,
                                              "lots_batch": 1,
                                              "position_a_buy": 0,
                                              "sell_open": -9000,
                                              "order_algorithm": "01",
                                              "trader_id": "1601",
                                              "order_action_limit": 400,
                                              "sell_close": 9000,
                                              "buy_open": -9000,
                                              "only_close": 0,
                                              "list_instrument_id": ["rb1705", "rb1701"],
                                              "position_a_buy_yesterday": 0,
                                              "user_id": "063802",
                                              "position_a_buy_today": 0,
                                              "position_a_sell_yesterday": 0,
                                              "lots": 10,
                                              "a_wait_price_tick": 1,
                                              "b_wait_price_tick": 0,
                                              "trade_model": "boll_reversion",
                                              "on_off": 0,  # 策略交易开关，0关、1开
                                              "trade_date": "2016-10-11",  # 交易日
                                              "today_profit": 0,  # 平仓盈利
                                              "today_commission": 0,  # 手续费
                                              "today_trade_volume": 0,  # 成交量
                                              "today_sum_slippage": 0,  # 总滑价
                                              "today_average_slippage": 0,  # 平均滑价
                                              },
                                             {"position_a_sell_today": 0,
                                              "position_b_sell": 0,
                                              "spread_shift": 0,
                                              "position_b_sell_today": 0,
                                              "position_b_buy_today": 0,
                                              "position_a_sell": 0,
                                              "buy_close": 9000,
                                              "stop_loss": 0,
                                              "position_b_buy_yesterday": 0,
                                              "is_active": 1,
                                              "position_b_sell_yesterday": 0,
                                              "strategy_id": "01",
                                              "position_b_buy": 0,
                                              "lots_batch": 1,
                                              "position_a_buy": 0,
                                              "sell_open": -9000,
                                              "order_algorithm": "01",
                                              "trader_id": "1601",
                                              "order_action_limit": 400,
                                              "sell_close": 9000,
                                              "buy_open": -9000,
                                              "only_close": 0,
                                              "list_instrument_id": ["ni1705", "ni1701"],
                                              "position_a_buy_yesterday": 0,
                                              "user_id": "063802",
                                              "position_a_buy_today": 0,
                                              "position_a_sell_yesterday": 0,
                                              "lots": 10,
                                              "a_wait_price_tick": 1,
                                              "b_wait_price_tick": 0,
                                              "trade_model": "boll_reversion",
                                              "on_off": 0,  # 策略交易开关，0关、1开
                                              "trade_date": "2016-10-11",  # 交易日
                                              "today_profit": 0,  # 平仓盈利
                                              "today_commission": 0,  # 手续费
                                              "today_trade_volume": 0,  # 成交量
                                              "today_sum_slippage": 0,  # 总滑价
                                              "today_average_slippage": 0,  # 平均滑价
                                              }
                                         ]
                                     }
                json_StrategyInfo = json.dumps(dict_StrategyInfo)
                self.__sm.send_msg(json_StrategyInfo)

                # 发送PositionInfo
                dict_PositionInfo = {'MsgRef': self.__sm.msg_ref_add(),
                                     'MsgSendFlag': 0,
                                     'MsgType': 5,  # 消息类型为PositionInfo
                                     'MsgResult': 0,  # 0：成功、1：失败
                                     'MsgErrorReason': 'None',
                                     'Info':
                                         [
                                             {'trader_id': '1601',  # 交易员id
                                              'user_id': '063802',  # user_id等于投资者代码
                                              'strategy_id': '01',  # 策略编号
                                              'InstrumentID': 'cu1611',  # 合约代码
                                              'BrokerID': '9999',  # 经纪公司代码
                                              'InvestorID': '063802',  # 投资者代码
                                              'Direction': '0',  # 持仓多空方向：0买、1卖
                                              'HedgeFlag': '1',  # 投机套保标志：1投机、2套利、3保值
                                              'CreatePositionDate': '20160926',  # 开仓日期
                                              'CreatePositionPrice': '38000',  # 开仓价格
                                              'YesterdayPosition': '1',  # 上日持仓
                                              'TodayPosition': '0',  # 今日持仓
                                              'MarginRateByMoney': 0,  # 保证金率
                                              'PositionFrozen': 0,  # 持仓冻结资金
                                              'PositionProfit': 0,  # 持仓盈亏
                                              'PreSettlementPrice': 0,  # 上次结算价
                                              },
                                             {'trader_id': '1601',  # 交易员id
                                              'user_id': '063802',  # user_id等于投资者代码
                                              'strategy_id': '01',  # 策略编号
                                              'InstrumentID': 'cu1612',  # 合约代码
                                              'BrokerID': '9999',  # 经纪公司代码
                                              'InvestorID': '063802',  # 投资者代码
                                              'Direction': '1',  # 持仓多空方向
                                              'HedgeFlag': '1',  # 投机套保标志
                                              'CreatePositionDate': '20160926',  # 开仓日期
                                              'CreatePositionPrice': '38050',  # 开仓价格
                                              'YesterdayPosition': '1',  # 上日持仓
                                              'TodayPosition': '0',  # 今日持仓
                                              'MarginRateByMoney': 0,  # 保证金率
                                              'PositionFrozen': 0,  # 持仓冻结资金
                                              'PositionProfit': 0,  # 持仓盈亏
                                              'PreSettlementPrice': 0,  # 上次结算价
                                              },
                                         ]
                                     }
                json_PositionInfo = json.dumps(dict_PositionInfo)
                self.__sm.send_msg(json_PositionInfo)

        elif buff['MsgType'] == 5:  # PositionInfo
            pass

        elif buff['MsgType'] == 6:  # MarketManagerInfo
            for i in buff['Info']:
                self.__CTPManager.create_md(i)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    q_client_main = ClientMain()  # 创建客户端界面实例
    ctp_manager = CTPManager()  # 创建客户端内核管理实例
    ctp_manager.set_ClientMain(q_client_main)  # 客户端界面实例与内核管理实例相互设置为对方的属性
    q_client_main.set_CTPManager(ctp_manager)

    q_login_form = QLogin.QLoginForm()  # 创建登录窗口
    q_login_form.set_QClientMain(q_client_main)
    q_client_main.set_QLoginForm(q_login_form)
    q_login_form.show()

    q_ctp = QCTP()  # 创建最外围的大窗口
    q_login_form.set_QCTP(q_ctp)
    q_client_main.set_QCTP(q_ctp)

    # dict_QAccountWidget = {'总账户': QAccountWidget()}  # 创建总账户QAccountWidget
    # q_login_form.set_dict_QAccountWidget(dict_QAccountWidget)  # 账户窗口字典设置为LoginForm的属性
    # q_client_main.set_dict_QAccountWidget(dict_QAccountWidget)  # 账户窗口字典设置为ClientMain的属性
    # q_ctp.tab_accounts.addTab(dict_QAccountWidget['总账户'], '总账户')  # 账户窗口添加到QCTP窗口的tab
    # print('>>>>>>>>>>>len(ctp_manager.get_list_user()=', len(ctp_manager.get_list_user()))
    # for i in ctp_manager.get_list_user():
    #     tmp = QAccountWidget()
    #     print(">>>>>>>>>>>>>", i.get_user_id(), tmp)
    #     dict_QAccountWidget = {i.get_user_id(): tmp}  # 创建单个账户QAccountWidget，键名为user_id
    #     q_ctp.tab_accounts.addTab(dict_QAccountWidget[i.get_user_id()], i.get_user_id())  # 账户窗口添加到QCTP窗口的tab

    print("if __name__ == '__main__'")
    sys.exit(app.exec_())


