# -*- coding: utf-8 -*-

"""
Module implementing QAccountWidget.
"""
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import QPoint
from Ui_QAccountWidget import Ui_Form
import json
import Strategy


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class QAccountWidget(QWidget, Ui_Form):
    """
    Class documentation goes here.
    """
    Signal_SendMsg = QtCore.pyqtSignal(str)  # 自定义信号
    signal_update_groupBox_trade_args_for_query = QtCore.pyqtSignal(Strategy.Strategy)  # 定义信号：更新界面参数框

    def __init__(self, str_widget_name, obj_user=None, list_user=None, parent=None, ClientMain=None):
        print("QAccountWidget.__init__() obj_user=", obj_user, "list_user=", list_user)
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QAccountWidget, self).__init__(parent)
        self.setupUi(self)

        self.popMenu = QtGui.QMenu(self.tableWidget_Trade_Args)

        # 添加策略菜单
        self.action_add = QtGui.QAction("添加策略", self)
        self.action_add.triggered.connect(self.slot_action_add_strategy)
        self.popMenu.addAction(self.action_add)

        # 删除策略菜单
        self.action_del = QtGui.QAction("删除策略", self)
        self.action_del.triggered.connect(self.slot_action_del_strategy)
        self.popMenu.addAction(self.action_del)

        # 绑定信号、槽函数
        self.Signal_SendMsg.connect(self.slot_SendMsg)

        # 设置user或list_user属性
        if obj_user is not None:
            self.__user = obj_user
        if list_user is not None:
            self.__list_user = list_user
            for i in self.__list_user:
                i.set_QAccountWidgetTotal(self)  # 将总账户窗口分别设置为user的属性
        self.__widget_name = str_widget_name

        # 设置ClientMain属性
        self.__ClientMain = ClientMain

        # 设置table行数
        row_number = 0
        if self.__widget_name == "总账户":
            for i in self.__list_user:
                row_number += len(i.get_list_strategy())
            print(">>> QAccountWidget.__init__() 总账户", "row_number=", row_number)
        else:
            row_number = len(self.__user.get_list_strategy())
            print(">>> QAccountWidget.__init__() 单账户", self.__user.get_user_id(), "row_number=", row_number)
        self.tableWidget_Trade_Args.setRowCount(row_number)
        self.tableWidget_Trade_Args.setColumnCount(16)
        self.tableWidget_Trade_Args.setCurrentCell(0, 0)

        # self.on_tableWidget_Trade_Args_cellClicked(0, 0)
        self.init_groupBox_trade_args_trade_algorithm(self.__ClientMain.get_listAlgorithmInfo())

        self.__signal_pushButton_set_position_setEnabled_connected = False  # 信号槽绑定标志，初始值为False

    # 自定义槽
    @pyqtSlot(str)
    def slot_SendMsg(self, msg):
        print("QAccountWidget.slot_SendMsg()", msg)
        # send json to server
        self.__ClientMain.get_SocketManager().send_msg(msg)

    def showEvent(self, QShowEvent):
        # print(">>> showEvent()", self.objectName(), "widget_name=", self.__widget_name)
        self.__ClientMain.set_show_widget(self)  # 显示在最前端的窗口设置为ClientMain的属性，全局唯一
        self.__ClientMain.set_show_widget_name(self.__widget_name)  # 显示在最前端的窗口名称设置为ClientMain的属性，全局唯一
        self.__ClientMain.set_showEvent(True)  # 是否有任何窗口显示了
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            i_strategy.set_show_widget_name(self.__widget_name)  # 前端窗口名称设置为strategy的属性
        self.__ClientMain.set_showQAccountWidget(self)  # 将当前显示在最前端窗口对象设置为ClienMain类的属性

    def hideEvent(self, QHideEvent):
        # print(">>> hideEvent()", self.objectName(), "widget_name=", self.__widget_name)
        self.__ClientMain.set_hideQAccountWidget(self)  # 将当前隐藏的窗口对象设置为ClienMain类的属性

    def set_ClientMain(self, obj_ClientMain):
        print(">>> QAccountWidget.set_ClientMain() ")
        self.__ClientMain = obj_ClientMain

    def set_user(self, obj_user):
        print(">>> QAccountWidget.set_user()")
        self.__user = obj_user

    def get_user(self):
        print(">>> QAccountWidget.get_user() widget_name=", self.__widget_name)
        return self.__user

    def get_widget_name(self):
        # print(">>> QAccountWidget.get_widget_name() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        return self.__widget_name

    # 设置窗口名称
    def set_widget_name(self, str_name):
        # print(">>> QAccountWidget.set_widget_name() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        self.__widget_name = str_name

    # 设置鼠标点击状态，信息包含:item所在行、item所在列、widget_name、user_id、strategy_id
    def set_clicked_status(self, in_dict):
        self.__clicked_status = in_dict
        # print(">>> QAccountWidget.set_clicked_status() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])

    def get_clicked_status(self):
        print(">>> QAccountWidget.get_clicked_status() widget_name=", self.__widget_name, 'user_id=',
              self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        return self.__clicked_status

    # 传入形参：table对象和字符串，返回同名的表头所在的列标
    def getHeaderItemColumn(self, obj_tableWidget, str_column_name):
        print(">>> QAccountWidget.getHeaderItemColumn() widget_name=", self.__widget_name, 'user_id=',
              self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        for i in range(obj_tableWidget.rowCount()):
            if obj_tableWidget.horizontalHeaderItem(i).text() == str_column_name:
                return i
        return -1

    # 设置信号槽连接状态的标志位
    def set_signal_pushButton_set_position_setEnabled_connected(self, bool_input):
        self.__signal_pushButton_set_position_setEnabled_connected = bool_input
        # print(">>> QAccountWidget.set_signal_pushButton_set_position_setEnabled_connected() widget_name=", self.__widget_name, "信号槽连接状态设置为", self.__signal_pushButton_set_position_setEnabled_connected)

    def get_signal_pushButton_set_position_setEnabled_connected(self):
        return self.__signal_pushButton_set_position_setEnabled_connected

    # 判断当前窗口是否单账户
    def is_single_user(self):
        if self.__widget_name == "总账户":
            return False
        else:
            return True

    # 初始化界面：策略列表，tableWidget_Trade_Args
    def init_table_widget(self):
        print(">>> QAccountWidget.init_table_widget()")
        if self.is_single_user():  # 单账户窗口
            print(">>> len(self.__user.get_list_strategy())=", len(self.__user.get_list_strategy()))
            if len(self.__user.get_list_strategy()) != 0:
                i_row = -1  # table的行标
                for i_strategy in self.__user.get_list_strategy():
                    i_row += 1  # table的行标
                    item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
                    if i_strategy.get_arguments()['strategy_on_off'] == 0:
                        item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
                        item_strategy_on_off.setText('关')
                    elif i_strategy.get_arguments()['strategy_on_off'] == 1:
                        item_strategy_on_off.setCheckState(QtCore.Qt.Checked)
                        item_strategy_on_off.setText('开')
                    item_strategy_only_close = QtGui.QTableWidgetItem()  # 只平
                    if i_strategy.get_arguments()['only_close'] == 0:
                        item_strategy_only_close.setCheckState(QtCore.Qt.Unchecked)
                        item_strategy_only_close.setText('关')
                    elif i_strategy.get_arguments()['only_close'] == 1:
                        item_strategy_only_close.setCheckState(QtCore.Qt.Checked)
                        item_strategy_only_close.setText('开')
                    item_user_id = QtGui.QTableWidgetItem(i_strategy.get_user_id())  # 期货账号
                    item_strategy_id = QtGui.QTableWidgetItem(i_strategy.get_strategy_id())  # 策略编号
                    str_tmp = ''
                    for j in i_strategy.get_list_instrument_id():
                        str_tmp += j
                        if j != i_strategy.get_list_instrument_id()[-1]:
                            str_tmp += ','
                    item_instrument_id = QtGui.QTableWidgetItem(str_tmp)  # 交易合约
                    item_position = QtGui.QTableWidgetItem(str(
                        i_strategy.get_position()['position_a_buy'] + i_strategy.get_position()['position_a_sell']))  # 总持仓
                    item_position_buy = QtGui.QTableWidgetItem(str(i_strategy.get_position()['position_a_buy']))  # 买持仓
                    item_position_sell = QtGui.QTableWidgetItem(str(i_strategy.get_position()['position_a_sell']))  # 卖持仓
                    item_hold_profit = QtGui.QTableWidgetItem('0')  # 持仓盈亏
                    item_close_profit = QtGui.QTableWidgetItem('0')  # 平仓盈亏
                    item_commission = QtGui.QTableWidgetItem('0')  # 手续费
                    item_trade_volume = QtGui.QTableWidgetItem('0')  # 成交量
                    item_amount = QtGui.QTableWidgetItem('0')  # 成交金额
                    item_average_shift = QtGui.QTableWidgetItem('0')  # 平均滑点
                    item_trade_model = QtGui.QTableWidgetItem(i_strategy.get_arguments()['trade_model'])  # 交易模型
                    item_order_algorithm = QtGui.QTableWidgetItem(i_strategy.get_arguments()['order_algorithm'])  # 下单算法
                    self.tableWidget_Trade_Args.setItem(i_row, 0, item_strategy_on_off)  # 开关
                    self.tableWidget_Trade_Args.setItem(i_row, 1, item_strategy_only_close)  # 只平
                    self.tableWidget_Trade_Args.setItem(i_row, 2, item_user_id)  # 期货账号
                    self.tableWidget_Trade_Args.setItem(i_row, 3, item_strategy_id)  # 策略编号
                    self.tableWidget_Trade_Args.setItem(i_row, 4, item_instrument_id)  # 交易合约
                    self.tableWidget_Trade_Args.setItem(i_row, 5, item_position)  # 总持仓
                    self.tableWidget_Trade_Args.setItem(i_row, 6, item_position_buy)  # 买持仓
                    self.tableWidget_Trade_Args.setItem(i_row, 7, item_position_sell)  # 卖持仓
                    self.tableWidget_Trade_Args.setItem(i_row, 8, item_hold_profit)  # 持仓盈亏
                    self.tableWidget_Trade_Args.setItem(i_row, 9, item_close_profit)  # 平仓盈亏
                    self.tableWidget_Trade_Args.setItem(i_row, 10, item_commission)  # 手续费
                    self.tableWidget_Trade_Args.setItem(i_row, 11, item_trade_volume)  # 成交量
                    self.tableWidget_Trade_Args.setItem(i_row, 12, item_amount)  # 成交金额
                    self.tableWidget_Trade_Args.setItem(i_row, 13, item_average_shift)  # 平均滑点
                    self.tableWidget_Trade_Args.setItem(i_row, 14, item_trade_model)  # 交易模型
                    self.tableWidget_Trade_Args.setItem(i_row, 15, item_order_algorithm)  # 下单算法
                self.on_tableWidget_Trade_Args_cellClicked(0, 0)
        else:  # 总账户窗口
            i_row = -1  # table的行标
            for i_user in self.__list_user:
                if len(i_user.get_list_strategy()) != 0:
                    for i_strategy in i_user.get_list_strategy():
                        i_row += 1  # table的行标
                        item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
                        if i_strategy.get_arguments()['strategy_on_off'] == 0:
                            item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
                            item_strategy_on_off.setText('关')
                        elif i_strategy.get_arguments()['strategy_on_off'] == 1:
                            item_strategy_on_off.setCheckState(QtCore.Qt.Checked)
                            item_strategy_on_off.setText('开')
                        item_strategy_only_close = QtGui.QTableWidgetItem()  # 只平
                        if i_strategy.get_arguments()['only_close'] == 0:
                            item_strategy_only_close.setCheckState(QtCore.Qt.Unchecked)
                            item_strategy_only_close.setText('关')
                        elif i_strategy.get_arguments()['only_close'] == 1:
                            item_strategy_only_close.setCheckState(QtCore.Qt.Checked)
                            item_strategy_only_close.setText('开')
                        item_user_id = QtGui.QTableWidgetItem(i_strategy.get_user_id())  # 期货账号
                        item_strategy_id = QtGui.QTableWidgetItem(i_strategy.get_strategy_id())  # 策略编号
                        str_tmp = ''
                        for j in i_strategy.get_list_instrument_id():
                            str_tmp += j
                            if j != i_strategy.get_list_instrument_id()[-1]:
                                str_tmp += ','
                        item_instrument_id = QtGui.QTableWidgetItem(str_tmp)  # 交易合约
                        item_position = QtGui.QTableWidgetItem(str(i_strategy.get_position()['position_a_buy'] + i_strategy.get_position()['position_a_sell']))  # 总持仓
                        item_position_buy = QtGui.QTableWidgetItem(str(i_strategy.get_position()['position_a_buy']))  # 买持仓
                        item_position_sell = QtGui.QTableWidgetItem(str(i_strategy.get_position()['position_a_sell']))  # 卖持仓
                        item_hold_profit = QtGui.QTableWidgetItem('0')  # 持仓盈亏
                        item_close_profit = QtGui.QTableWidgetItem('0')  # 平仓盈亏
                        item_commission = QtGui.QTableWidgetItem('0')  # 手续费
                        item_trade_volume = QtGui.QTableWidgetItem('0')  # 成交量
                        item_amount = QtGui.QTableWidgetItem('0')  # 成交金额
                        item_average_shift = QtGui.QTableWidgetItem('0')  # 平均滑点
                        item_trade_model = QtGui.QTableWidgetItem(i_strategy.get_arguments()['trade_model'])  # 交易模型
                        item_order_algorithm = QtGui.QTableWidgetItem(i_strategy.get_arguments()['order_algorithm'])  # 下单算法
                        self.tableWidget_Trade_Args.setItem(i_row, 0, item_strategy_on_off)  # 开关
                        self.tableWidget_Trade_Args.setItem(i_row, 1, item_strategy_only_close)  # 只平
                        self.tableWidget_Trade_Args.setItem(i_row, 2, item_user_id)  # 期货账号
                        self.tableWidget_Trade_Args.setItem(i_row, 3, item_strategy_id)  # 策略编号
                        self.tableWidget_Trade_Args.setItem(i_row, 4, item_instrument_id)  # 交易合约
                        self.tableWidget_Trade_Args.setItem(i_row, 5, item_position)  # 总持仓
                        self.tableWidget_Trade_Args.setItem(i_row, 6, item_position_buy)  # 买持仓
                        self.tableWidget_Trade_Args.setItem(i_row, 7, item_position_sell)  # 卖持仓
                        self.tableWidget_Trade_Args.setItem(i_row, 8, item_hold_profit)  # 持仓盈亏
                        self.tableWidget_Trade_Args.setItem(i_row, 9, item_close_profit)  # 平仓盈亏
                        self.tableWidget_Trade_Args.setItem(i_row, 10, item_commission)  # 手续费
                        self.tableWidget_Trade_Args.setItem(i_row, 11, item_trade_volume)  # 成交量
                        self.tableWidget_Trade_Args.setItem(i_row, 12, item_amount)  # 成交金额
                        self.tableWidget_Trade_Args.setItem(i_row, 13, item_average_shift)  # 平均滑点
                        self.tableWidget_Trade_Args.setItem(i_row, 14, item_trade_model)  # 交易模型
                        self.tableWidget_Trade_Args.setItem(i_row, 15, item_order_algorithm)  # 下单算法
                    self.on_tableWidget_Trade_Args_cellClicked(0, 0)

    # 往策略列表中添加新建的策略
    @QtCore.pyqtSlot()
    def insert_row_table_widget(self):
        if self.is_single_user():  # 单账户窗口
            # 新建策略不属于该窗口，跳过
            if self.__ClientMain.get_obj_new_strategy().get_user_id() != self.__widget_name:
                return

            i_row = self.tableWidget_Trade_Args.rowCount()  # 行标
            self.tableWidget_Trade_Args.insertRow(i_row)  # 插入指定行
            item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
            if self.__ClientMain.get_obj_new_strategy().get_arguments()['strategy_on_off'] == 0:
                item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
                item_strategy_on_off.setText('关')
            elif self.__ClientMain.get_obj_new_strategy().get_arguments()['strategy_on_off'] == 1:
                item_strategy_on_off.setCheckState(QtCore.Qt.Checked)
                item_strategy_on_off.setText('开')
            item_strategy_only_close = QtGui.QTableWidgetItem()  # 只平
            if self.__ClientMain.get_obj_new_strategy().get_arguments()['only_close'] == 0:
                item_strategy_only_close.setCheckState(QtCore.Qt.Unchecked)
                item_strategy_only_close.setText('关')
            elif self.__ClientMain.get_obj_new_strategy().get_arguments()['only_close'] == 1:
                item_strategy_only_close.setCheckState(QtCore.Qt.Checked)
                item_strategy_only_close.setText('开')
            item_user_id = QtGui.QTableWidgetItem(self.__ClientMain.get_obj_new_strategy().get_user_id())  # 期货账号
            item_strategy_id = QtGui.QTableWidgetItem(
                self.__ClientMain.get_obj_new_strategy().get_strategy_id())  # 策略编号
            str_tmp = ''
            for j in self.__ClientMain.get_obj_new_strategy().get_list_instrument_id():
                str_tmp += j
                if j != self.__ClientMain.get_obj_new_strategy().get_list_instrument_id()[-1]:
                    str_tmp += ','
            item_instrument_id = QtGui.QTableWidgetItem(str_tmp)  # 交易合约
            item_position = QtGui.QTableWidgetItem(str(
                self.__ClientMain.get_obj_new_strategy().get_position()['position_a_buy'] +
                self.__ClientMain.get_obj_new_strategy().get_position()['position_a_sell']))  # 总持仓
            item_position_buy = QtGui.QTableWidgetItem(
                str(self.__ClientMain.get_obj_new_strategy().get_position()['position_a_buy']))  # 买持仓
            item_position_sell = QtGui.QTableWidgetItem(
                str(self.__ClientMain.get_obj_new_strategy().get_position()['position_a_sell']))  # 卖持仓
            item_hold_profit = QtGui.QTableWidgetItem('0')  # 持仓盈亏
            item_close_profit = QtGui.QTableWidgetItem('0')  # 平仓盈亏
            item_commission = QtGui.QTableWidgetItem('0')  # 手续费
            item_trade_volume = QtGui.QTableWidgetItem('0')  # 成交量
            item_amount = QtGui.QTableWidgetItem('0')  # 成交金额
            item_average_shift = QtGui.QTableWidgetItem('0')  # 平均滑点
            item_trade_model = QtGui.QTableWidgetItem(
                self.__ClientMain.get_obj_new_strategy().get_arguments()['trade_model'])  # 交易模型
            item_order_algorithm = QtGui.QTableWidgetItem(
                self.__ClientMain.get_obj_new_strategy().get_arguments()['order_algorithm'])  # 下单算法
            self.tableWidget_Trade_Args.setItem(i_row, 0, item_strategy_on_off)  # 开关
            self.tableWidget_Trade_Args.setItem(i_row, 1, item_strategy_only_close)  # 只平
            self.tableWidget_Trade_Args.setItem(i_row, 2, item_user_id)  # 期货账号
            self.tableWidget_Trade_Args.setItem(i_row, 3, item_strategy_id)  # 策略编号
            self.tableWidget_Trade_Args.setItem(i_row, 4, item_instrument_id)  # 交易合约
            self.tableWidget_Trade_Args.setItem(i_row, 5, item_position)  # 总持仓
            self.tableWidget_Trade_Args.setItem(i_row, 6, item_position_buy)  # 买持仓
            self.tableWidget_Trade_Args.setItem(i_row, 7, item_position_sell)  # 卖持仓
            self.tableWidget_Trade_Args.setItem(i_row, 8, item_hold_profit)  # 持仓盈亏
            self.tableWidget_Trade_Args.setItem(i_row, 9, item_close_profit)  # 平仓盈亏
            self.tableWidget_Trade_Args.setItem(i_row, 10, item_commission)  # 手续费
            self.tableWidget_Trade_Args.setItem(i_row, 11, item_trade_volume)  # 成交量
            self.tableWidget_Trade_Args.setItem(i_row, 12, item_amount)  # 成交金额
            self.tableWidget_Trade_Args.setItem(i_row, 13, item_average_shift)  # 平均滑点
            self.tableWidget_Trade_Args.setItem(i_row, 14, item_trade_model)  # 交易模型
            self.tableWidget_Trade_Args.setItem(i_row, 15, item_order_algorithm)  # 下单算法
        else:  # 总账户窗口
            i_row = self.tableWidget_Trade_Args.rowCount()  # 行标
            self.tableWidget_Trade_Args.insertRow(i_row)  # 插入指定行
            item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
            if self.__ClientMain.get_obj_new_strategy().get_arguments()['strategy_on_off'] == 0:
                item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
                item_strategy_on_off.setText('关')
            elif self.__ClientMain.get_obj_new_strategy().get_arguments()['strategy_on_off'] == 1:
                item_strategy_on_off.setCheckState(QtCore.Qt.Checked)
                item_strategy_on_off.setText('开')
            item_strategy_only_close = QtGui.QTableWidgetItem()  # 只平
            if self.__ClientMain.get_obj_new_strategy().get_arguments()['only_close'] == 0:
                item_strategy_only_close.setCheckState(QtCore.Qt.Unchecked)
                item_strategy_only_close.setText('关')
            elif self.__ClientMain.get_obj_new_strategy().get_arguments()['only_close'] == 1:
                item_strategy_only_close.setCheckState(QtCore.Qt.Checked)
                item_strategy_only_close.setText('开')
            item_user_id = QtGui.QTableWidgetItem(self.__ClientMain.get_obj_new_strategy().get_user_id())  # 期货账号
            item_strategy_id = QtGui.QTableWidgetItem(self.__ClientMain.get_obj_new_strategy().get_strategy_id())  # 策略编号
            str_tmp = ''
            for j in self.__ClientMain.get_obj_new_strategy().get_list_instrument_id():
                str_tmp += j
                if j != self.__ClientMain.get_obj_new_strategy().get_list_instrument_id()[-1]:
                    str_tmp += ','
            item_instrument_id = QtGui.QTableWidgetItem(str_tmp)  # 交易合约
            item_position = QtGui.QTableWidgetItem(str(
                self.__ClientMain.get_obj_new_strategy().get_position()['position_a_buy'] + self.__ClientMain.get_obj_new_strategy().get_position()['position_a_sell']))  # 总持仓
            item_position_buy = QtGui.QTableWidgetItem(str(self.__ClientMain.get_obj_new_strategy().get_position()['position_a_buy']))  # 买持仓
            item_position_sell = QtGui.QTableWidgetItem(str(self.__ClientMain.get_obj_new_strategy().get_position()['position_a_sell']))  # 卖持仓
            item_hold_profit = QtGui.QTableWidgetItem('0')  # 持仓盈亏
            item_close_profit = QtGui.QTableWidgetItem('0')  # 平仓盈亏
            item_commission = QtGui.QTableWidgetItem('0')  # 手续费
            item_trade_volume = QtGui.QTableWidgetItem('0')  # 成交量
            item_amount = QtGui.QTableWidgetItem('0')  # 成交金额
            item_average_shift = QtGui.QTableWidgetItem('0')  # 平均滑点
            item_trade_model = QtGui.QTableWidgetItem(self.__ClientMain.get_obj_new_strategy().get_arguments()['trade_model'])  # 交易模型
            item_order_algorithm = QtGui.QTableWidgetItem(self.__ClientMain.get_obj_new_strategy().get_arguments()['order_algorithm'])  # 下单算法
            self.tableWidget_Trade_Args.setItem(i_row, 0, item_strategy_on_off)  # 开关
            self.tableWidget_Trade_Args.setItem(i_row, 1, item_strategy_only_close)  # 只平
            self.tableWidget_Trade_Args.setItem(i_row, 2, item_user_id)  # 期货账号
            self.tableWidget_Trade_Args.setItem(i_row, 3, item_strategy_id)  # 策略编号
            self.tableWidget_Trade_Args.setItem(i_row, 4, item_instrument_id)  # 交易合约
            self.tableWidget_Trade_Args.setItem(i_row, 5, item_position)  # 总持仓
            self.tableWidget_Trade_Args.setItem(i_row, 6, item_position_buy)  # 买持仓
            self.tableWidget_Trade_Args.setItem(i_row, 7, item_position_sell)  # 卖持仓
            self.tableWidget_Trade_Args.setItem(i_row, 8, item_hold_profit)  # 持仓盈亏
            self.tableWidget_Trade_Args.setItem(i_row, 9, item_close_profit)  # 平仓盈亏
            self.tableWidget_Trade_Args.setItem(i_row, 10, item_commission)  # 手续费
            self.tableWidget_Trade_Args.setItem(i_row, 11, item_trade_volume)  # 成交量
            self.tableWidget_Trade_Args.setItem(i_row, 12, item_amount)  # 成交金额
            self.tableWidget_Trade_Args.setItem(i_row, 13, item_average_shift)  # 平均滑点
            self.tableWidget_Trade_Args.setItem(i_row, 14, item_trade_model)  # 交易模型
            self.tableWidget_Trade_Args.setItem(i_row, 15, item_order_algorithm)  # 下单算法

    # 从策略列表中删除策略
    @QtCore.pyqtSlot()
    def remove_row_table_widget(self):
        print(">>> QAccountWidget.remove_row_table_widget() called, widget_name=", self.__widget_name)
        if self.is_single_user():  # 单账户窗口
            # 要删除的策略属于该窗口
            # if self.__clicked_status['widget_name'] == self.__widget_name:
            # if self.__ClientMain.get_clicked_status()['widget_name'] == self.__widget_name:
            # 找到将要删除的策略在本窗口table_widget中的行标
            for i_row in range(self.tableWidget_Trade_Args.rowCount()):  # 遍历行
                if self.tableWidget_Trade_Args.item(i_row, 2).text() == self.__ClientMain.get_clicked_status()['user_id'] \
                        and self.tableWidget_Trade_Args.item(i_row, 3).text() == self.__ClientMain.get_clicked_status()['strategy_id']:
                    print(">>> QAccountWidget.remove_row_table_widget() 从单账户窗口中删除策略行")
                    self.tableWidget_Trade_Args.removeRow(i_row)
                    break
        if self.is_single_user() is False:  # 总账户窗口
            # 找到将要删除的策略在本窗口table_widget中的行标
            for i_row in range(self.tableWidget_Trade_Args.rowCount()):  # 遍历行
                if self.tableWidget_Trade_Args.item(i_row, 2).text() == self.__ClientMain.get_clicked_status()['user_id'] \
                        and self.tableWidget_Trade_Args.item(i_row, 3).text() == self.__ClientMain.get_clicked_status()['strategy_id']:
                    print(">>> QAccountWidget.remove_row_table_widget() 从总账户窗口中删除策略行")
                    self.tableWidget_Trade_Args.removeRow(i_row)
                    break

    # 初始化界面：策略统计类指标（统计代码在Strategy类中实现，界面层的类仅负责显示）
    def init_table_widget_statistics(self):
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():  # 遍历所有策略
            for i_row in range(self.tableWidget_Trade_Args.rowCount()):  # 遍历行
                # 策略与行对应
                if self.tableWidget_Trade_Args.item(i_row, 2).text() == i_strategy.get_user_id() and self.tableWidget_Trade_Args.item(i_row, 3).text() == i_strategy.get_strategy_id():
                    position = i_strategy.get_position()['position_a_buy'] + i_strategy.get_position()['position_a_sell']
                    self.tableWidget_Trade_Args.item(i_row, 7).setText(str(position))

    # 初始化界面：策略参数框中的下单算法选项
    def init_groupBox_trade_args_trade_algorithm(self, list_algorithm):
        i_row = -1
        for i in range(len(list_algorithm)):
            i_row += 1
            self.comboBox_xiadansuanfa.insertItem(i_row, list_algorithm[i]['name'])

    # 更新“策略列表”（tableWidget_Trade_Args）
    def update_tableWidget_Trade_Args(self, obj_strategy):
        for i_row in range(self.tableWidget_Trade_Args.rowCount()):  # 遍历行
            if self.tableWidget_Trade_Args.item(i_row, 2).text() == obj_strategy.get_user_id() and self.tableWidget_Trade_Args.item(i_row, 3).text() == obj_strategy.get_strategy_id():
                position = obj_strategy.get_position()['position_a_buy'] + obj_strategy.get_position()['position_a_sell']
                self.tableWidget_Trade_Args.item(i_row, 5).setText(str(position))  # 总持仓
                self.tableWidget_Trade_Args.item(i_row, 6).setText(str(obj_strategy.get_position()['position_a_buy']))  # 买持仓
                self.tableWidget_Trade_Args.item(i_row, 7).setText(str(obj_strategy.get_position()['position_a_sell']))  # 卖持仓
                self.tableWidget_Trade_Args.item(i_row, 8).setText('shouxufei')  # 持仓盈亏
                self.tableWidget_Trade_Args.item(i_row, 9).setText('shouxufei')  # 平仓盈亏
                self.tableWidget_Trade_Args.item(i_row, 10).setText('shouxufei')  # 手续费
                self.tableWidget_Trade_Args.item(i_row, 11).setText('chengjiaoliang')  # 成交量
                self.tableWidget_Trade_Args.item(i_row, 12).setText("chengjiaojin'e")  # 成交金额
                self.tableWidget_Trade_Args.item(i_row, 13).setText('pingjunhuadian')  # 平均滑点

    # 更新界面：“策略参数”框（groupBox_trade_args），更新策略参数框-鼠标点击策略列表中策略事件，一次最多更新一个窗口的groupBox
    def update_groupBox(self):
        # print(">>> QAccountWidget.update_groupBox_trade_args() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        # 设置期货账号选项
        if self.is_single_user():  # 单账户页面
            if self.comboBox_qihuozhanghao.findText(self.__clicked_status['user_id'], QtCore.Qt.MatchExactly) == -1:
                self.comboBox_qihuozhanghao.insertItem(0, self.__clicked_status['user_id'])
        else:  # 总账户页面
            # 插入所有user_id到item
            i_row = -1
            for i_user in self.__list_user:
                if self.comboBox_qihuozhanghao.findText(i_user.get_user_id().decode(), QtCore.Qt.MatchExactly) == -1:
                    i_row += 1
                    self.comboBox_qihuozhanghao.insertItem(i_row, i_user.get_user_id().decode())
            # item中显示当前鼠标所选中的user_id
            for i_row in range(self.comboBox_qihuozhanghao.count()):
                if self.comboBox_qihuozhanghao.itemText(i_row) == self.__clicked_status['user_id']:
                    self.comboBox_qihuozhanghao.setCurrentIndex(i_row)

        # 设置策略编号选项
        if self.is_single_user():  # 单账户页面
            # 插入所有strategy_id到item
            i_row = -1
            for i_strategy in self.__user.get_list_strategy():
                # 插入时除重
                if self.comboBox_celuebianhao.findText(i_strategy.get_strategy_id(), QtCore.Qt.MatchExactly) == -1:
                    i_row += 1
                    self.comboBox_celuebianhao.insertItem(i_row, i_strategy.get_strategy_id())
            # item中显示当前鼠标所选中的strategy_id
            for i_row in range(self.comboBox_celuebianhao.count()):
                if self.comboBox_celuebianhao.itemText(i_row) == self.__clicked_status['strategy_id']:
                    self.comboBox_celuebianhao.setCurrentIndex(i_row)
        else:  # 总账户页面
            # 清空item
            self.comboBox_celuebianhao.clear()
            # 插入所有strategy_id到item
            i_row = -1
            for i_user in self.__list_user:
                if i_user.get_user_id().decode() == self.__clicked_status['user_id']:
                    for i_strategy in i_user.get_list_strategy():
                        # 插入时除重
                        if self.comboBox_celuebianhao.findText(i_strategy.get_strategy_id(), QtCore.Qt.MatchExactly) == -1:
                            i_row += 1
                            self.comboBox_celuebianhao.insertItem(i_row, i_strategy.get_strategy_id())
            # item中显示当前鼠标所选中的strategy_id
            for i_row in range(self.comboBox_celuebianhao.count()):
                if self.comboBox_celuebianhao.itemText(i_row) == self.__clicked_status['strategy_id']:
                    self.comboBox_celuebianhao.setCurrentIndex(i_row)

        # 显示下单算法编号
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            if i_strategy.get_user_id() == self.__clicked_status['user_id'] and i_strategy.get_strategy_id() == self.__clicked_status['strategy_id']:
                # item中显示当前鼠标所选中的strategy_id
                for i_row in range(self.comboBox_xiadansuanfa.count()):
                    if self.comboBox_xiadansuanfa.itemText(i_row) == i_strategy.get_arguments()['order_algorithm']:
                        self.comboBox_xiadansuanfa.setCurrentIndex(i_row)
                break

        # 交易参数和持仓
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            if self.__clicked_status['user_id'] == i_strategy.get_user_id() and self.__clicked_status['strategy_id'] == i_strategy.get_strategy_id():
                # print(">>> QAccountWidget.update_groupBox_trade_args() widget_name=", self.__widget_name, "user_id=", i_strategy.get_user_id(), "strategy_id=", i_strategy.get_strategy_id(), "刷新策略参数框的参数")
                # 更新交易参数
                dict_args = i_strategy.get_arguments()
                self.lineEdit_zongshou.setText(str(dict_args['lots']))  # 总手
                self.lineEdit_meifen.setText(str(dict_args['lots_batch']))  # 每份
                self.spinBox_zhisun.setValue(dict_args['stop_loss'])  # 止损
                self.spinBox_rangjia.setValue(dict_args['spread_shift'])  # 超价触发
                self.spinBox_Adengdai.setValue(dict_args['a_wait_price_tick'])  # A等待
                self.spinBox_Bdengdai.setValue(dict_args['b_wait_price_tick'])  # B等待
                self.lineEdit_Achedanxianzhi.setText(str(dict_args['a_order_action_limit']))  # A限制（撤单次数）
                self.lineEdit_Bchedanxianzhi.setText(str(dict_args['b_order_action_limit']))  # B限制（撤单次数）
                self.doubleSpinBox_kongtoukai.setValue(dict_args['sell_open'])  # 空头开（卖开价差）
                self.doubleSpinBox_kongtouping.setValue(dict_args['buy_close'])  # 空头平（买平价差）   
                self.doubleSpinBox_duotoukai.setValue(dict_args['buy_open'])  # 多头开（买开价差）
                self.doubleSpinBox_duotouping.setValue(dict_args['sell_close'])  # 多头平（卖平价差）
                if dict_args['sell_open_on_off'] == 0:
                    self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)  # 空头开-开关
                elif dict_args['sell_open_on_off'] == 1:
                    self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)  # 空头开-开关
                if dict_args['buy_close_on_off'] == 0:
                    self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)  # 空头平-开关
                elif dict_args['buy_close_on_off'] == 1:
                    self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)  # 空头平-开关
                if dict_args['buy_open_on_off'] == 0:
                    self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)  # 多头开-开关
                elif dict_args['buy_open_on_off'] == 1:
                    self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)  # 多头开-开关
                if dict_args['sell_close_on_off'] == 0:
                    self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)  # 多头平-开关
                elif dict_args['sell_close_on_off'] == 1:
                    self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)  # 多头平-开关
                # 更新持仓
                dict_position = i_strategy.get_position()
                self.lineEdit_Azongsell.setText(str(dict_position['position_a_sell']))  # A总卖
                self.lineEdit_Ajinsell.setText(str(dict_position['position_a_sell_today']))  # A今卖
                self.lineEdit_Bzongbuy.setText(str(dict_position['position_b_buy']))  # B总买
                self.lineEdit_Bjinbuy.setText(str(dict_position['position_b_buy_today']))  # B今买
                self.lineEdit_Azongbuy.setText(str(dict_position['position_a_buy']))  # A总买
                self.lineEdit_Ajinbuy.setText(str(dict_position['position_a_buy_today']))  # A今买
                self.lineEdit_Bzongsell.setText(str(dict_position['position_b_sell']))  # B总卖
                self.lineEdit_Bjinsell.setText(str(dict_position['position_b_sell_today']))  # B今卖

    # 点击“发送”按钮后的参数更新，要更新的策略为goupBox中显示的user_id、strategy_id对应的
    def update_groupBox_trade_args_for_set(self):
        # 遍历策略列表，找到与界面显示相同的策略对象实例
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            if i_strategy.get_user_id() == self.comboBox_qihuozhanghao.currentText() and i_strategy.get_strategy_id() == self.comboBox_celuebianhao.currentText():
                dict_args = i_strategy.get_arguments()
                self.lineEdit_zongshou.setText(str(dict_args['lots']))  # 总手
                self.lineEdit_meifen.setText(str(dict_args['lots_batch']))  # 每份
                self.spinBox_zhisun.setValue(dict_args['stop_loss'])  # 止损
                self.spinBox_rangjia.setValue(dict_args['spread_shift'])  # 超价触发
                self.spinBox_Adengdai.setValue(dict_args['a_wait_price_tick'])  # A等待
                self.spinBox_Bdengdai.setValue(dict_args['b_wait_price_tick'])  # B等待
                self.lineEdit_Achedanxianzhi.setText(str(dict_args['a_order_action_limit']))  # A限制（撤单次数）
                self.lineEdit_Bchedanxianzhi.setText(str(dict_args['b_order_action_limit']))  # B限制（撤单次数）
                self.doubleSpinBox_kongtoukai.setValue(dict_args['sell_open'])  # 空头开（卖开价差）
                self.doubleSpinBox_kongtouping.setValue(dict_args['buy_close'])  # 空头平（买平价差）
                self.doubleSpinBox_duotoukai.setValue(dict_args['buy_open'])  # 多头开（买开价差）
                self.doubleSpinBox_duotouping.setValue(dict_args['sell_close'])  # 多头平（卖平价差）
                if dict_args['sell_open_on_off'] == 0:
                    self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)  # 空头开-开关
                elif dict_args['sell_open_on_off'] == 1:
                    self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)  # 空头开-开关
                if dict_args['buy_close_on_off'] == 0:
                    self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)  # 空头平-开关
                elif dict_args['buy_close_on_off'] == 1:
                    self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)  # 空头平-开关
                if dict_args['buy_open_on_off'] == 0:
                    self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)  # 多头开-开关
                elif dict_args['buy_open_on_off'] == 1:
                    self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)  # 多头开-开关
                if dict_args['sell_close_on_off'] == 0:
                    self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)  # 多头平-开关
                elif dict_args['sell_close_on_off'] == 1:
                    self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)  # 多头平-开关

                # dict_position = i_strategy.get_position()
                # self.lineEdit_Azongsell.setText(str(dict_position['position_a_sell']))  # A总卖
                # self.lineEdit_Ajinsell.setText(str(dict_position['position_a_sell_today']))  # A今卖
                # self.lineEdit_Bzongbuy.setText(str(dict_position['position_b_buy']))  # B总买
                # self.lineEdit_Bjinbuy.setText(str(dict_position['position_b_buy_today']))  # B今买
                # self.lineEdit_Azongbuy.setText(str(dict_position['position_a_buy']))  # A总买
                # self.lineEdit_Ajinbuy.setText(str(dict_position['position_a_buy_today']))  # A今买
                # self.lineEdit_Bzongsell.setText(str(dict_position['position_b_sell']))  # B总卖
                # self.lineEdit_Bjinsell.setText(str(dict_position['position_b_sell_today']))  # B今卖
                break

    # 更新界面：“策略参数”框（groupBox_trade_args），点击界面“查询”操作
    @pyqtSlot(Strategy.Strategy)
    def update_groupBox_trade_args_for_query(self, obj_strategy):
        dict_arguments = obj_strategy.get_arguments()
        dict_position = obj_strategy.get_position()
        print("QAccountWidget.update_groupBox_trade_args_for_query() called")
        # 显示交易模型
        index_jiaoyimoxing = self.comboBox_jiaoyimoxing.findText(dict_arguments['trade_model'], QtCore.Qt.MatchExactly)
        if index_jiaoyimoxing != -1:
            self.comboBox_jiaoyimoxing.setCurrentIndex(index_jiaoyimoxing)
        elif index_jiaoyimoxing == -1:
            print("QAccountWidget.update_groupBox_trade_args_for_query() 更新界面时出错，comboBox_jiaoyimoxing组件中不存在交易模型", dict_arguments['trade_model'])
        # 显示交易算法
        index_xiadansuanfa = self.comboBox_xiadansuanfa.findText(dict_arguments['order_algorithm'], QtCore.Qt.MatchExactly)
        if index_xiadansuanfa != -1:
            self.comboBox_xiadansuanfa.setCurrentIndex(index_xiadansuanfa)
        elif index_xiadansuanfa == -1:
            print("QAccountWidget.update_groupBox_trade_args_for_query() 更新界面时出错，comboBox_xiadansuanfa组件中不存在策略编号", dict_arguments['order_algorithm'])
        self.lineEdit_zongshou.setText(str(dict_arguments['lots']))  # 总手
        self.lineEdit_meifen.setText(str(dict_arguments['lots_batch']))  # 每份
        self.spinBox_zhisun.setValue(dict_arguments['stop_loss'])  # 止损
        self.spinBox_rangjia.setValue(dict_arguments['spread_shift'])  # 超价触发
        self.spinBox_Adengdai.setValue(dict_arguments['a_wait_price_tick'])  # A等待
        self.spinBox_Bdengdai.setValue(dict_arguments['b_wait_price_tick'])  # B等待
        self.lineEdit_Achedanxianzhi.setText(str(dict_arguments['a_order_action_limit']))  # A限制（撤单次数）
        self.lineEdit_Bchedanxianzhi.setText(str(dict_arguments['b_order_action_limit']))  # B限制（撤单次数）
        self.doubleSpinBox_kongtoukai.setValue(dict_arguments['sell_open'])  # 空头开（卖开价差）
        self.doubleSpinBox_kongtouping.setValue(dict_arguments['buy_close'])  # 空头平（买平价差）
        self.doubleSpinBox_duotoukai.setValue(dict_arguments['buy_open'])  # 多头开（买开价差）
        self.doubleSpinBox_duotouping.setValue(dict_arguments['sell_close'])  # 多头平（卖平价差）
        if dict_arguments['sell_open_on_off'] == 0:
            self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)  # 空头开-开关
        elif dict_arguments['sell_open_on_off'] == 1:
            self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)  # 空头开-开关
        if dict_arguments['buy_close_on_off'] == 0:
            self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)  # 空头平-开关
        elif dict_arguments['buy_close_on_off'] == 1:
            self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)  # 空头平-开关
        if dict_arguments['buy_open_on_off'] == 0:
            self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)  # 多头开-开关
        elif dict_arguments['buy_open_on_off'] == 1:
            self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)  # 多头开-开关
        if dict_arguments['sell_close_on_off'] == 0:
            self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)  # 多头平-开关
        elif dict_arguments['sell_close_on_off'] == 1:
            self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)  # 多头平-开关

        self.lineEdit_Azongsell.setText(str(dict_position['position_a_sell']))  # A总卖
        self.lineEdit_Ajinsell.setText(str(dict_position['position_a_sell_today']))  # A今卖
        self.lineEdit_Bzongbuy.setText(str(dict_position['position_b_buy']))  # B总买
        self.lineEdit_Bjinbuy.setText(str(dict_position['position_b_buy_today']))  # B今买
        self.lineEdit_Azongbuy.setText(str(dict_position['position_a_buy']))  # A总买
        self.lineEdit_Ajinbuy.setText(str(dict_position['position_a_buy_today']))  # A今买
        self.lineEdit_Bzongsell.setText(str(dict_position['position_b_sell']))  # B总卖
        self.lineEdit_Bjinsell.setText(str(dict_position['position_b_sell_today']))  # B今卖

    # 更新界面：“账户资金”框，panel_show_account
    def update_panel_show_account(self, dict_args):
        pass

    # 鼠标右击弹出菜单中的“添加策略”
    @pyqtSlot()
    def slot_action_add_strategy(self):
        # print(">>> QAccountWidget.slot_action_add_strategy() called")
        self.__ClientMain.get_QNewStrategy().update_comboBox_user_id_menu()  # 更新新建策略框中的期货账号可选项菜单
        self.__ClientMain.get_QNewStrategy().show()
        # todo...

    # 鼠标右击弹出菜单中的“删除策略”
    @pyqtSlot()
    def slot_action_del_strategy(self):
        print(">>> QAccountWidget.slot_action_del_strategy() called")
        # 找到将要删除的策略对象
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            print(">>> QAccountWidget.slot_action_del_strategy() i_strategy.get_user_id()=", i_strategy.get_user_id(), "i_strategy.get_strategy_id()=", i_strategy.get_strategy_id(), "self.__clicked_status['user_id']=", self.__clicked_status['user_id'], "self.__clicked_status['strategy_id']=", self.__clicked_status['strategy_id'])
            if i_strategy.get_user_id() == self.__clicked_status['user_id'] and i_strategy.get_strategy_id() == self.__clicked_status['strategy_id']:
                # print(">>> QAccountWidget.slot_action_del_strategy() 将要删除的策略user_id=", i_strategy.get_user_id(), "strategy_id=", i_strategy.get_strategy_id())
                # 判断持仓：有持仓，跳出
                dict_position = i_strategy.get_position()
                for i in dict_position:
                    if dict_position[i] != 0:
                        print("QAccountWidgetslot_action_del_strategy() 策略有持仓，不允许删除")
                        return
                # 策略开关的状态为开，跳过
                if self.__ClientMain.get_CTPManager().get_on_off() == 1 and i_strategy.get_on_off() == 1:
                    print("QAccountWidgetslot_action_del_strategy() 策略开关为开，不允许删除")
                    return

                # 向服务端发送删除策略指令
                dict_delete_strategy = {'MsgRef': self.__ClientMain.get_SocketManager().msg_ref_add(),
                                        'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                        'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                        'MsgType': 7,  # 删除策略
                                        'TraderID': i_strategy.get_trader_id(),
                                        'UserID': i_strategy.get_user_id(),
                                        'StrategyID': i_strategy.get_strategy_id()
                                        }
                json_delete_strategy = json.dumps(dict_delete_strategy)
                # print(">>> QAccountWidget.slot_action_del_strategy() json_delete_strategy=", json_delete_strategy)
                self.Signal_SendMsg.emit(json_delete_strategy)

                break
        # todo...

    @pyqtSlot()
    def on_pushButton_query_account_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot()
    def on_pushButton_only_close_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot()
    def on_pushButton_start_strategy_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        print("QAccountWidget.on_pushButton_start_strategy_clicked() widget_name=", self.__widget_name)
        if self.is_single_user():  # 单账户窗口
            print(">>> QAccountWidget.on_pushButton_start_strategy_clicked()", self.pushButton_start_strategy.text(), self.__user.get_on_off())
            if self.pushButton_start_strategy.text() == '开始策略' and self.__user.get_on_off() == 0:
                self.pushButton_start_strategy.setEnabled(False)  # 将按钮禁用
                # 发送命令：将期货账户开关修改为开，值为1
                self.__ClientMain.SendUserOnoff({'on_off': 1, 'user_id': self.__widget_name})
            elif self.pushButton_start_strategy.text() == '停止策略' and self.__user.get_on_off() == 1:
                self.pushButton_start_strategy.setEnabled(False)  # 将按钮禁用
                # 发送命令：将期货账户开关修改为关，值为0
                self.__ClientMain.SendUserOnoff({'on_off': 0, 'user_id': self.__widget_name})
        else:  # 总账户窗口
            if self.pushButton_start_strategy.text() == '开始策略' and self.__ClientMain.get_CTPManager().get_on_off() == 0:
                self.pushButton_start_strategy.setEnabled(False)  # 将按钮禁用
                # 发送命令：将交易员开关修改为开，值为1
                self.__ClientMain.SendTraderOnoff({'on_off': 1})
            elif self.pushButton_start_strategy.text() == '停止策略' and self.__ClientMain.get_CTPManager().get_on_off() == 1:
                self.pushButton_start_strategy.setEnabled(False)  # 将按钮禁用
                # 发送命令：将交易员开关修改为关，值为0
                self.__ClientMain.SendTraderOnoff({'on_off': 0})

    
    @pyqtSlot()
    def on_pushButton_liandongjia_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot()
    def on_pushButton_liandongjian_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot()
    def on_pushButton_set_strategy_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        dict_args = {
            "MsgRef": self.__ClientMain.get_SocketManager().msg_ref_add(),
            "MsgSendFlag": 0,  # 发送标志，客户端发出0，服务端发出1
            "MsgType": 5,  # 修改单条策略持仓
            "TraderID": self.__ClientMain.get_TraderID(),  # trader_id
            "UserID": self.comboBox_qihuozhanghao.currentText(),  # user_id
            "StrategyID": self.comboBox_celuebianhao.currentText(),  # strategy_id
            "MsgSrc": 0,
            "Info": [{
                "trader_id": self.__ClientMain.get_TraderID(),  # trader_id
                "user_id": self.comboBox_qihuozhanghao.currentText(),  # user_id
                "strategy_id": self.comboBox_celuebianhao.currentText(),  # strategy_id
                "trade_model": self.comboBox_jiaoyimoxing.currentText(),  # 交易模型
                "order_algorithm": self.comboBox_xiadansuanfa.currentText(),  # 下单算法
                "lots": int(self.lineEdit_zongshou.text()),  # 总手
                "lots_batch": int(self.lineEdit_meifen.text()),  # 每份
                "stop_loss": float(self.spinBox_zhisun.text()),  # 止损跳数
                "spread_shift": float(self.spinBox_rangjia.text()),  # 超价发单跳数
                "a_wait_price_tick": float(self.spinBox_Adengdai.text()),  # A撤单等待跳数
                "b_wait_price_tick": float(self.spinBox_Bdengdai.text()),  # B撤单等待跳数
                "a_order_action_limit": int(self.lineEdit_Achedanxianzhi.text()),  # A撤单限制
                "b_order_action_limit": int(self.lineEdit_Bchedanxianzhi.text()),  # B撤单限制
                "sell_open": self.doubleSpinBox_kongtoukai.value(),  # 价差卖开触发参数
                "buy_close": self.doubleSpinBox_kongtouping.value(),  # 价差买平触发参数
                "sell_close": self.doubleSpinBox_duotouping.value(),  # 价差卖平触发参数
                "buy_open": self.doubleSpinBox_duotoukai.value(),  # 价差买开触发参数
                "sell_open_on_off": (1 if self.checkBox_kongtoukai.isChecked() else 0),  # 价差卖开触发开关
                "buy_close_on_off": (1 if self.checkBox_kongtouping.isChecked() else 0),  # 价差买平触发开关
                "sell_close_on_off": (1 if self.checkBox_duotouping.isChecked() else 0),  # 价差卖平触发开关
                "buy_open_on_off": (1 if self.checkBox_duotoukai.isChecked() else 0)  # 价差买开触发开关
            }]
        }
        json_StrategyEditWithoutPosition = json.dumps(dict_args)
        self.__ClientMain.signal_send_msg.emit(json_StrategyEditWithoutPosition)

    @pyqtSlot()
    def on_pushButton_set_position_clicked(self):
        # print(">>> QAccountWidget.on_pushButton_set_position_clicked() widget_name=", self.__widget_name, "self.pushButton_set_position.text()=", self.pushButton_set_position.text())
        if self.pushButton_set_position.text() == "设置持仓":
            self.pushButton_set_position.setText("发送持仓")  # 修改按钮显示的字符
            # 解禁仓位显示lineEdit，允许编辑
            self.lineEdit_Azongbuy.setEnabled(True)  # 文本框允许编辑
            self.lineEdit_Ajinbuy.setEnabled(True)
            self.lineEdit_Azongsell.setEnabled(True)
            self.lineEdit_Ajinsell.setEnabled(True)
            self.lineEdit_Bzongbuy.setEnabled(True)
            self.lineEdit_Bjinbuy.setEnabled(True)
            self.lineEdit_Bzongsell.setEnabled(True)
            self.lineEdit_Bjinsell.setEnabled(True)
        elif self.pushButton_set_position.text() == "发送持仓":
            self.lineEdit_Azongbuy.setEnabled(False)  # 禁用文本框
            self.lineEdit_Ajinbuy.setEnabled(False)
            self.lineEdit_Azongsell.setEnabled(False)
            self.lineEdit_Ajinsell.setEnabled(False)
            self.lineEdit_Bzongbuy.setEnabled(False)
            self.lineEdit_Bjinbuy.setEnabled(False)
            self.lineEdit_Bzongsell.setEnabled(False)
            self.lineEdit_Bjinsell.setEnabled(False)
            # self.pushButton_set_position.setEnabled(False)  # 禁用按钮
            dict_setPosition = {
                "MsgRef": self.__ClientMain.get_SocketManager().msg_ref_add(),
                "MsgSendFlag": 0,  # 发送标志，客户端发出0，服务端发出1
                "MsgType": 12,  # 修改单条策略持仓
                "TraderID": self.__ClientMain.get_TraderID(),  # trader_id
                "UserID": self.comboBox_qihuozhanghao.currentText(),  # user_id
                "StrategyID": self.comboBox_celuebianhao.currentText(),  # strategy_id
                "MsgSrc": 0,
                "Info": [{
                    "trader_id": self.__ClientMain.get_TraderID(),  # trader_id
                    "user_id": self.comboBox_qihuozhanghao.currentText(),  # user_id
                    "strategy_id": self.comboBox_celuebianhao.currentText(),  # strategy_id
                    "position_a_buy": int(self.lineEdit_Azongbuy.text()),  # A总买
                    "position_a_buy_today": int(self.lineEdit_Ajinbuy.text()),  # A今买
                    "position_a_buy_yesterday": int(self.lineEdit_Azongbuy.text()) - int(self.lineEdit_Ajinbuy.text()), # A昨买
                    "position_a_sell": int(self.lineEdit_Azongsell.text()),  # A总卖
                    "position_a_sell_today": int(self.lineEdit_Ajinsell.text()),  # A今卖
                    "position_a_sell_yesterday": int(self.lineEdit_Azongsell.text()) - int(self.lineEdit_Ajinsell.text()), # A昨卖
                    "position_b_buy": int(self.lineEdit_Bzongbuy.text()),  # B总买
                    "position_b_buy_today": int(self.lineEdit_Bjinbuy.text()),  # B今买
                    "position_b_buy_yesterday": int(self.lineEdit_Bzongbuy.text()) - int(self.lineEdit_Bjinbuy.text()), # B昨买
                    "position_b_sell": int(self.lineEdit_Bzongsell.text()),  # B总卖
                    "position_b_sell_today": int(self.lineEdit_Bjinsell.text()),  # B今卖
                    "position_b_sell_yesterday": int(self.lineEdit_Bzongsell.text()) - int(self.lineEdit_Bjinsell.text()), # B昨卖
                }]
            }
            json_setPosition = json.dumps(dict_setPosition)
            self.__ClientMain.signal_send_msg.emit(json_setPosition)

    # 激活设置持仓按钮，禁用仓位输入框
    @QtCore.pyqtSlot()
    def on_pushButton_set_position_active(self):
        print(">>> QAccountWidget.on_pushButton_set_position_active() called, widget_name=", self.__widget_name)
        self.pushButton_set_position.setText("设置持仓")
        self.pushButton_set_position.setEnabled(True)  # 激活按钮

    @pyqtSlot()
    def on_pushButton_query_strategy_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        # 获取界面参数框里显示的期货账号的策略编号
        self.pushButton_query_strategy.setEnabled(False)  # 点击按钮之后禁用，等收到消息后激活
        self.__ClientMain.QryStrategyInfo()
        # UserID = self.comboBox_qihuozhanghao.currentText(), StrategyID=self.comboBox_celuebianhao.currentText()

    @pyqtSlot(bool)
    def on_checkBox_kongtoukai_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(int)
    def on_checkBox_kongtoukai_stateChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(bool)
    def on_checkBox_duotouping_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(int)
    def on_checkBox_duotouping_stateChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(bool)
    def on_checkBox_duotoukai_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(int)
    def on_checkBox_duotoukai_stateChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(bool)
    def on_checkBox_kongtouping_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(int)
    def on_checkBox_kongtouping_stateChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    #@pyqtSlot(QPoint)
    #def on_tablewidget_tableWidget_Trade_Args_customContextMenuRequested(self, pos):
        """
        Slot documentation goes here.
        
        @param pos DESCRIPTION
        @type QPoint
        """
        # TODO: not implemented yet
        ## raise NotImplementedError

    
    @pyqtSlot(int)
    def on_comboBox_qihuozhanghao_currentIndexChanged(self, index):
        """
        Slot documentation goes here.
        
        @param index DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(str)
    def on_comboBox_qihuozhanghao_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(int)
    def on_comboBox_jiaoyimoxing_currentIndexChanged(self, index):
        """
        Slot documentation goes here.
        
        @param index DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError
    
    @pyqtSlot(str)
    def on_comboBox_jiaoyimoxing_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        # TODO: not implemented yet
        print("currentindex string %s" % p0)
    
    @pyqtSlot(int)
    def on_comboBox_celuebianhao_currentIndexChanged(self, index):
        """
        Slot documentation goes here.
        
        @param index DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        print("currentindex %d" % index)
    
    @pyqtSlot(str)
    def on_comboBox_celuebianhao_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        # TODO: not implemented yet
        # raise NotImplementedError

    # 鼠标右击捕获事件
    @pyqtSlot(QPoint)
    def on_tableWidget_Trade_Args_customContextMenuRequested(self, pos):
        print("QAccountWidget.on_tableWidget_Trade_Args_customContextMenuRequested() called 鼠标右击捕获事件")
        """
        Slot documentation goes here.
        
        @param pos DESCRIPTION
        @type QPoint
        """
        # TODO: not implemented yet
        self.popMenu.exec_(QtGui.QCursor.pos())
    
    @pyqtSlot(int, int)
    def on_tableWidget_Trade_Args_cellClicked(self, row, column):
        """
        Slot documentation goes here.
        
        @param row DESCRIPTION
        @type int
        @param column DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        item = self.tableWidget_Trade_Args.item(row, column)
        print("QAccountWidget.on_tableWidget_Trade_Args_cellClicked() widget_name=", self.__widget_name, "鼠标点击位置=row %d, column %d" % (row, column), "值=", item.text())
        # 设置鼠标点击状态，信息包含:item所在行、item所在列、widget_name、user_id、strategy_id
        clicked_item_info = {'row': row, 'column': column, 'widget_name': self.__widget_name, 'user_id': self.tableWidget_Trade_Args.item(row, 2).text(), 'strategy_id': self.tableWidget_Trade_Args.item(row, 3).text()}
        self.set_clicked_status(clicked_item_info)  # 保存鼠标点击状态到本类属性，每个窗口保存各自的鼠标点击位置
        self.__ClientMain.set_clicked_status(clicked_item_info)  # 保存鼠标点击状态到ClientMain的属性，保存全局唯一一个鼠标最后点击位置
        self.__ClientMain.set_clicked_item(item)  # 鼠标点击的item设置为ClientMain的属性，全局唯一
        # 将鼠标选中的策略对象设置为ClientMain的属性，全局唯一
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            if i_strategy.get_user_id() == clicked_item_info['user_id'] and i_strategy.get_strategy_id() == clicked_item_info['strategy_id']:
                self.__ClientMain.set_clicked_strategy(i_strategy)
        # 分别设置“总账户”、“单账户窗口”被选中的状态到每个策略
        if self.is_single_user():  # 单账户窗口
            for i_user in self.__ClientMain.get_CTPManager().get_list_user():
                if i_user.get_user_id().decode() == clicked_item_info['user_id']:
                    for i_strategy in i_user.get_list_strategy():
                        if i_strategy.get_strategy_id() == clicked_item_info['strategy_id']:
                            i_strategy.set_clicked(True)  # 策略在单账户窗口中被鼠标选中
                        else:
                            i_strategy.set_clicked(False)  # 策略在单账户窗口中未被鼠标选中
        else:  # 总账户窗口
            for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
                if i_strategy.get_user_id() == clicked_item_info['user_id'] and i_strategy.get_strategy_id() == clicked_item_info['strategy_id']:
                    i_strategy.set_clicked_total(True)  # 策略在总账户窗口中被鼠标选中
                else:
                    i_strategy.set_clicked_total(False)  # 策略在总账户窗口中未被鼠标选中
        self.update_groupBox()  # 更新策略参数框-鼠标点击策略列表中策略事件，一次最多更新一个窗口的groupBox

        # 窗口初始化完成
        if self.__ClientMain.get_create_QAccountWidget_finished():
            self.tableWidget_Trade_Args.setCurrentItem(item)
            # 判断策略开关item的checkState()状态变化
            if column == 0:
                # checkState值与前值不同，则发送指令
                on_off_checkState = 0 if item.checkState() == 0 else 1
                if on_off_checkState != self.__ClientMain.get_clicked_strategy().get_on_off():
                    item.setFlags(item.flags() & (~QtCore.Qt.ItemIsEnabled))  # 设置当前item的状态属性(与操作)
                    dict_args = {'user_id': self.__ClientMain.get_clicked_strategy().get_user_id(),
                                 'strategy_id': self.__ClientMain.get_clicked_strategy().get_strategy_id(),
                                 'on_off': on_off_checkState}
                    self.__ClientMain.SendStrategyOnOff(dict_args)
            # 判断策略只平item的checkState()状态变化
            elif column == 1:
                only_close_checkState = 0 if item.checkState() == 0 else 1
                if only_close_checkState != self.__ClientMain.get_clicked_strategy().get_only_close():
                    item.setFlags(item.flags() & (~QtCore.Qt.ItemIsEnabled))  # 设置当前item的状态属性(与操作)
                    dict_args = {'user_id': self.__ClientMain.get_clicked_strategy().get_user_id(),
                                 'strategy_id': self.__ClientMain.get_clicked_strategy().get_strategy_id(),
                                 'on_off': only_close_checkState}
                    self.__ClientMain.SendStrategyOnlyClose(dict_args)

    @pyqtSlot(int, int)
    def on_tableWidget_Trade_Args_cellDoubleClicked(self, row, column):
        """
        Slot documentation goes here.
        
        @param row DESCRIPTION
        @type int
        @param column DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QAccountWidget()
    Form.show()

    #设置tablewidget的行数
    Form.tableWidget_Trade_Args.setRowCount(5)
    # print("0 header name %s, %d ttttttttt" % (Form.tableWidget_Trade_Args.horizontalHeaderItem(0).text(), 2))

    #创建QTableWidgetItem
    for i in range(13):
        item = QtGui.QTableWidgetItem()
        item.setText("hello: %d你好" % i)
        if i == 0:
            item.setCheckState(False)
        Form.tableWidget_Trade_Args.setItem(0, i, item)



    sys.exit(app.exec_())