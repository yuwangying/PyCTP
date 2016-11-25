# -*- coding: utf-8 -*-

"""
Module implementing QAccountWidget.
"""
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import QPoint
from Ui_QAccountWidget import Ui_Form

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

    def __init__(self, str_widget_name, obj_user=None, list_user=None, parent=None):
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

        if obj_user is not None:
            self.__user = obj_user
        if list_user is not None:
            self.__list_user = list_user
            for i in self.__list_user:
                i.set_QAccountWidgetTotal(self)  # 将总账户窗口分别设置为user的属性
        self.__widget_name = str_widget_name

        # 设置table尺寸
        row_number = 0
        if self.__widget_name == "总账户":
            for i in self.__list_user:
                row_number += len(i.get_list_strategy())
        else:
            row_number = len(self.__user.get_list_strategy())
        self.tableWidget_Trade_Args.setRowCount(row_number)
        self.tableWidget_Trade_Args.setColumnCount(16)
        self.tableWidget_Trade_Args.setCurrentCell(0, 0)

        # self.on_tableWidget_Trade_Args_cellClicked(0, 0)

    # 自定义槽
    @pyqtSlot(str)
    def slot_SendMsg(self, msg):
        print("QAccountWidget.slot_SendMsg()", msg)
        # send json to server
        self.__sm.send_msg(msg)

    def showEvent(self, QShowEvent):
        print(">>> showEvent()", self.objectName(), "widget_name=", self.__widget_name)
        self.__ClientMain.set_show_widget_name(self.__widget_name)
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            i_strategy.set_show_widget_name(self.__widget_name)
        pass

    def hideEvent(self, QHideEvent):
        print(">>> hideEvent()", self.objectName(), "widget_name=", self.__widget_name)
        pass
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
        print(">>> QAccountWidget.get_widget_name() widget_name=", self.__widget_name, 'user_id=',
              self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        return self.__widget_name

    # 设置窗口名称
    def set_widget_name(self, str_name):
        print(">>> QAccountWidget.set_widget_name() widget_name=", self.__widget_name, 'user_id=',
              self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        self.__widget_name = str_name

    # 设置鼠标点击状态，信息包含:item所在行、item所在列、widget_name、user_id、strategy_id
    def set_clicked_status(self, in_dict):
        self.__clicked_status = in_dict
        print(">>> QAccountWidget.set_clicked_status() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])

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

    # 判断当前窗口是否单账户
    def is_single_user(self):
        if self.__widget_name == "总账户":
            return False
        else:
            return True

    # 初始化界面：策略列表，tableWidget_Trade_Args
    def init_table_widget(self):
        print(">>> QAccountWidget.init_table_widget()")
        if self.is_single_user():  # 单账户
            i_row = -1  # table的行标
            for i_strategy in self.__user.get_list_strategy():
                i_row += 1  # table的行标
                item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
                if i_strategy.get_arguments()['StrategyOnoff'] == 0:
                    item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
                    item_strategy_on_off.setText('关')
                elif i_strategy.get_arguments()['StrategyOnoff'] == 1:
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
                # self.update_tableWidget_Trade_Args(i_strategy)
        else:  # 总账户
            i_row = -1  # table的行标
            for i_user in self.__list_user:
                for i_strategy in i_user.get_list_strategy():
                    i_row += 1  # table的行标
                    item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
                    if i_strategy.get_arguments()['StrategyOnoff'] == 0:
                        item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
                        item_strategy_on_off.setText('关')
                    elif i_strategy.get_arguments()['StrategyOnoff'] == 1:
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


                    # self.update_tableWidget_Trade_Args(i_strategy)
        self.on_tableWidget_Trade_Args_cellClicked(0, 0)

    """
    # 更新界面：策略列表，tableWidget_Trade_Args（更新一个策略，即一行）
    def update_tableWidget_Trade_Args(self, dict_args):
        # 遍历row，更新已经存在的策略的值，如果不存在，先插入row，然后更新值
        bool_found = False
        for i in range(self.tableWidget_Trade_Args.rowCount()):  # 遍历行
            index_column_user_id = self.getHeaderItemColumn(self.tableWidget_Trade_Args, "期货账号")
            index_column_strategy_id = self.getHeaderItemColumn(self.tableWidget_Trade_Args, "策略编号")
            # 在table中找到已经存在的期货账号和策略编号，item更新值
            if self.tableWidget_Trade_Args.item(i, index_column_user_id).text() == dict_args['user_id']\
                    and self.tableWidget_Trade_Args.item(i, index_column_strategy_id).text() == dict_args['strategy_id']:
                bool_found = True
                for j in range(self.tableWidget_Trade_Args.columnCount()):  # 遍历列
                    column_name = self.tableWidget_Trade_Args.horizontalHeaderItem(i).text()
                    if column_name == '策略开关':
                        # 策略开关单独发送到服务端，CheckState状态发生变化即刻发送到客户端，待收到客户端发送的回报则将参数值存入本地数据库
                        # self.tableWidget_Trade_Args.item(i, j).setCheckState(False)
                        # self.tableWidget_Trade_Args.item(i, j).setText("<font color='#c00'>" + "关" + "</font>")
                        pass
                    # elif column_name == '期货账号':
                    #     self.tableWidget_Trade_Args.item(i, j).setText(dict_args['user_id'])
                    # elif column_name == '策略编号':
                    #     self.tableWidget_Trade_Args.item(i, j).setText(dict_args['strategy_id'])
                    elif column_name == '交易合约':
                        output_text = ""
                        for i in dict_args['strategy_id']:
                            output_text = output_text + i + ","
                        output_text = output_text[:-1]
                        self.tableWidget_Trade_Args.item(i, j).setText(output_text)
                    elif column_name == '交易模型':
                        self.tableWidget_Trade_Args.item(i, j).setText(dict_args['trade_model'])
                    elif column_name == '持仓盈亏':
                        # 如果策略有持仓则调用更新持仓盈亏的方法，如果策略没有持仓，填充0
                        # 收到持仓相关的tick更新，客户端自行计算持仓盈亏
                        if dict_args['position_a_buy'] != 0 or dict_args['position_a_sell'] != 0:
                            # 填充代码
                            pass
                        elif dict_args['position_a_buy'] == 0 and dict_args['position_a_sell'] == 0:
                            self.tableWidget_Trade_Args.item(i, j).setText('0')
                    elif column_name == '总持仓':
                        self.tableWidget_Trade_Args.item(i, j).setText(dict_args['position_a_buy'] + dict_args['position_a_sell'])
                    elif column_name == '买持仓':
                        self.tableWidget_Trade_Args.item(i, j).setText(dict_args['position_a_buy'])
                    elif column_name == '卖持仓':
                        self.tableWidget_Trade_Args.item(i, j).setText(dict_args['position_a_sell'])
                    elif column_name == '手续费':
                        # item.setText(dict_args['strategy_id'])
                        # 从数据库中的trade统计，有成交则刷新
                        # 填充代码
                        pass
                    elif column_name == '成交量':
                        # item.setText(dict_args['strategy_id'])
                        # 从数据库中的trade统计，有成交则刷新
                        # 填充代码
                        pass
                    elif column_name == '成交金额':
                        # item.setText(dict_args['strategy_id'])
                        # 从数据库中的trade统计，有成交则刷新
                        # 填充代码
                        pass
                    elif column_name == '平均滑点':
                        # item.setText(dict_args['strategy_id'])
                        # 从数据库中的trade统计，有成交则刷新
                        # 填充代码
                        pass
        # 在table中未找到期货账号和策略编号，创建item并更新值
        if not bool_found:
            list_column_name = ['策略开关', '期货账号', '策略编号', '交易合约', '交易模型', '持仓盈亏', '总持仓', '买持仓', '卖持仓', '手续费', '成交量', '成交金额', '平均滑点']
            index_row = self.tableWidget_Trade_Args.rowCount()  # 行标
            self.tableWidget_Trade_Args.insertRow(index_row)  # 在最后面插入一行
            item = QtGui.QTableWidgetItem()  # 创建item
            for i in range(self.tableWidget_Trade_Args.columnCount()):  # 遍历列
                column_name = self.tableWidget_Trade_Args.horizontalHeaderItem(i).text()
                if column_name == '策略开关':
                    item.setCheckState(False)
                    item.setText("<font color='#c00'>" + "关" + "</font>")
                    self.tableWidget_Trade_Args.setItem(index_row, i, item)  # 将item插入到指定位置
                elif column_name == '期货账号':
                    item.setText(dict_args['user_id'])
                elif column_name == '策略编号':
                    item.setText(dict_args['strategy_id'])
                elif column_name == '交易合约':
                    output_text = ""
                    for i in dict_args['strategy_id']:
                        output_text = output_text + i + ","
                    output_text = output_text[:-1]
                    item.setText(output_text)
                elif column_name == '交易模型':
                    item.setText(dict_args['trade_model'])
                elif column_name == '持仓盈亏':
                    # 如果策略有持仓则调用更新持仓盈亏的方法，如果策略没有持仓，填充0
                    # 收到持仓相关的tick更新，客户端自行计算持仓盈亏
                    if dict_args['position_a_buy'] == 0 and dict_args['position_a_sell'] == 0:
                        item.setText('0')
                elif column_name == '总持仓':
                    item.setText(dict_args['position_a_buy'] + dict_args['position_a_sell'])
                elif column_name == '买持仓':
                    item.setText(dict_args['position_a_buy'])
                elif column_name == '卖持仓':
                    item.setText(dict_args['position_a_sell'])
                elif column_name == '手续费':
                    # item.setText(dict_args['strategy_id'])
                    # 从数据库中的trade统计，有成交则刷新
                    # 填充代码
                    pass
                elif column_name == '成交量':
                    # item.setText(dict_args['strategy_id'])
                    # 从数据库中的trade统计，有成交则刷新
                    # 填充代码
                    pass
                elif column_name == '成交金额':
                    # item.setText(dict_args['strategy_id'])
                    # 从数据库中的trade统计，有成交则刷新
                    # 填充代码
                    pass
                elif column_name == '平均滑点':
                    # item.setText(dict_args['strategy_id'])
                    # 有成交刷新，作为strategy属性类维护，成交量加权平均滑点值
                    # 填充代码
                    pass

    # 更新界面：策略列表中的列“持仓盈亏”,此处为套利组合的持仓盈亏，另外还有具体合约持仓盈亏明细，在order框显示，由tick驱动更新
    def update_tableWidget_Trade_Args_chicangyinkui(self, dict_args):
        pass
    """

    def update_tableWidget_Trade_Args_init(self):
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():  # 遍历所有策略
            for i_row in range(self.tableWidget_Trade_Args.rowCount()):  # 遍历行
                # 策略与行对应
                print(">>> QAccountWidget.update_tableWidget_Trade_Args_init() self.tableWidget_Trade_Args.item(i_row, 2).text() == i_strategy.get_user_id()", self.tableWidget_Trade_Args.item(i_row, 2).text(), i_strategy.get_user_id(), type(self.tableWidget_Trade_Args.item(i_row, 2).text()), type(i_strategy.get_user_id()))
                if self.tableWidget_Trade_Args.item(i_row, 2).text() == i_strategy.get_user_id() and self.tableWidget_Trade_Args.item(i_row, 3).text() == i_strategy.get_strategy_id():
                    position = i_strategy.get_position()['position_a_buy'] + i_strategy.get_position()['position_a_sell']
                    self.tableWidget_Trade_Args.item(i_row, 7).setText(str(position))
                    print(">>> QAccountWidget.update_tableWidget_Trade_Args_init() position=", position)

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

    # 更新“策略参数”框价差，（仅更新鼠标所选中的单一策略）
    # def update_groupBox_spread(self, obj_strategy):
    def update_groupBox_spread(self, spread_long, spread_short):
        print(">>> QAccountWidget.update_groupBox_spread widget_name=", self.__widget_name)
        print(">>> QAccountWidget.update_groupBox_spread address memory =", self.update_groupBox_spread)
        print(">>> QAccountWidget.lineEdit_kongtoujiacha address memory =", self.lineEdit_kongtoujiacha)
        print(">>> QAccountWidget.lineEdit_duotoujiacha address memory =", self.lineEdit_duotoujiacha)
        # print(">>> QAccountWidget.obj_strategy address memory =", obj_strategy)
        # print(">>> QAccountWidget.update_groupBox_spread() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'], '(', str("%.2f" % float(obj_strategy.get_spread_short())), str("%.2f" % float(obj_strategy.get_spread_long())), ')')
        for i in range(3):
            self.lineEdit_kongtoujiacha.setText(str("%.2f" % float("0")))
            self.lineEdit_duotoujiacha.setText(str("%.2f" % float()))
        # self.lineEdit_kongtoujiacha.setText("short")
        # self.lineEdit_duotoujiacha.setText("long")


    # 更新界面：“策略参数”框，    groupBox_trade_args
    def update_groupBox_trade_args(self):
        print(">>> QAccountWidget.update_groupBox_trade_args() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
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

        # 设置固定参数：总手、每份、止损、超价触发、A等待、B等待、A限制、B限制、空头开、空头平、多头开、多头平、A总卖、A今卖、B总买、B今买、A总买、A总买、B总卖、B总卖
        # if self.is_single_user():  # 单账户页面
        # else:  # 总账户页面
        for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
            if self.__clicked_status['user_id'] == i_strategy.get_user_id() and self.__clicked_status['strategy_id'] == i_strategy.get_strategy_id():
                self.lineEdit_zongshou.setText(str(i_strategy.get_arguments()['lots']))  # 总手
                self.lineEdit_meifen.setText(str(i_strategy.get_arguments()['lots_batch']))  # 每份
                self.spinBox_zhisun.setValue(i_strategy.get_arguments()['stop_loss'])  # 止损
                self.spinBox_rangjia.setValue(i_strategy.get_arguments()['spread_shift'])  # 超价触发
                self.spinBox_Adengdai.setValue(i_strategy.get_arguments()['a_wait_price_tick'])  # A等待
                self.spinBox_Bdengdai.setValue(i_strategy.get_arguments()['b_wait_price_tick'])  # B等待
                self.lineEdit_Achedanxianzhi.setText(str(i_strategy.get_arguments()['a_order_action_limit']))  # A限制（撤单次数）
                self.lineEdit_Bchedanxianzhi.setText(str(i_strategy.get_arguments()['b_order_action_limit']))  # B限制（撤单次数）
                self.doubleSpinBox_kongtoukai.setValue(i_strategy.get_arguments()['sell_open'])  # 空头开（卖开价差）
                self.doubleSpinBox_kongtouping.setValue(i_strategy.get_arguments()['buy_close'])  # 空头平（买平价差）
                self.doubleSpinBox_duotoukai.setValue(i_strategy.get_arguments()['buy_open'])  # 多头开（买开价差）
                self.doubleSpinBox_duotouping.setValue(i_strategy.get_arguments()['sell_close'])  # 多头平（卖平价差）
                self.lineEdit_Azongsell.setText(str(i_strategy.get_position()['position_a_sell']))  # A总卖
                self.lineEdit_Ajinsell.setText(str(i_strategy.get_position()['position_a_sell_today']))  # A今卖
                self.lineEdit_Bzongbuy.setText(str(i_strategy.get_position()['position_b_buy']))  # B总买
                self.lineEdit_Bjinbuy.setText(str(i_strategy.get_position()['position_b_buy_today']))  # B今买
                self.lineEdit_Azongbuy.setText(str(i_strategy.get_position()['position_a_buy']))  # A总买
                self.lineEdit_Ajinbuy.setText(str(i_strategy.get_position()['position_a_buy_today']))  # A今买
                self.lineEdit_Bzongsell.setText(str(i_strategy.get_position()['position_b_sell']))  # B总卖
                self.lineEdit_Bjinsell.setText(str(i_strategy.get_position()['position_b_sell_today']))  # B今卖

    # 更新界面：“账户资金”框，panel_show_account
    def update_panel_show_account(self, dict_args):
        pass

    # 鼠标右击弹出菜单中的“添加策略”
    @pyqtSlot()
    def slot_action_add_strategy(self):
        print("slot_action_add_strategy was actived!")
        # todo...

    # 鼠标右击弹出菜单中的“删除策略”
    @pyqtSlot()
    def slot_action_del_strategy(self):
        print("slot_action_del_strategy was actived!")
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
        print("set strategy %s" % self.comboBox_qihuozhanghao.currentText())
    
    @pyqtSlot()
    def on_pushButton_query_strategy_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        # 获取界面参数框里显示的期货账号的策略编号
        self.__ClientMain.QryStrategyInfo(UserID=self.comboBox_qihuozhanghao.currentText(),
                                          StrategyID=self.comboBox_celuebianhao.currentText())
    
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
        in_dict = {'row': row, 'column': column, 'widget_name': self.__widget_name, 'user_id': self.tableWidget_Trade_Args.item(row, 2).text(), 'strategy_id': self.tableWidget_Trade_Args.item(row, 3).text()}
        self.set_clicked_status(in_dict)  # 保存鼠标点击状态到本类属性
        self.__ClientMain.set_clicked_status(in_dict)  # 保存鼠标点击状态到ClientMain的属性
        # 设置策略在总账户窗口中被鼠标选中的标志位
        if self.is_single_user():  # 单账户窗口
            for i_user in self.__ClientMain.get_CTPManager().get_list_user():
                # print(">>> QAccountWidget.on_tableWidget_Trade_Args_cellClicked() i_user.get_user_id()=", i_user.get_user_id())
                if i_user.get_user_id().decode() == in_dict['user_id']:
                    for i_strategy in i_user.get_list_strategy():
                        if i_strategy.get_strategy_id() == in_dict['strategy_id']:
                            i_strategy.set_clicked(True)  # 策略在单账户窗口中被鼠标选中
                        else:
                            i_strategy.set_clicked(False)  # 策略在单账户窗口中未被鼠标选中
        else:  # 总账户窗口
            for i_strategy in self.__ClientMain.get_CTPManager().get_list_strategy():
                if i_strategy.get_user_id() == in_dict['user_id'] and i_strategy.get_strategy_id() == in_dict['strategy_id']:
                    i_strategy.set_clicked_total(True)  # 策略在总账户窗口中被鼠标选中
                else:
                    i_strategy.set_clicked_total(False)  # 策略在总账户窗口中未被鼠标选中
        self.update_groupBox_trade_args()  # 更新策略参数框
        # self.update_groupBox_spread()  # 更新策略参数框中的价差值

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