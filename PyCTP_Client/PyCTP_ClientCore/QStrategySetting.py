# -*- coding: utf-8 -*-

"""
Module implementing NewStrategy.
"""

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget

from Ui_QStrategySetting import Ui_NewStrategy


class NewStrategy(QWidget, Ui_NewStrategy):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(NewStrategy, self).__init__(parent)
        self.setupUi(self)

        reg_strategy_id = QtCore.QRegExp('[0-9][0-9]')
        validator_strategy_id = QtGui.QRegExpValidator(reg_strategy_id)
        self.lineEdit_strategy_id.setValidator(validator_strategy_id)

        reg_instrument_id = QtCore.QRegExp('([a-z]{1,2}|[A-Z]{1,2})[0-9]{3,4}')
        validator_instrument_id = QtGui.QRegExpValidator(reg_instrument_id)
        self.lineEdit_a_instrument.setValidator(validator_instrument_id)
        self.lineEdit_b_instrument.setValidator(validator_instrument_id)

    def set_ClientMain(self, obj_ClientMain):
        self.__ClientMain = obj_ClientMain
    
    @pyqtSlot()
    def on_pushButton_cancel_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        self.hide()
    
    @pyqtSlot()
    def on_pushButton_ok_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError


        # 检查合约代码
        if self.lineEdit_a_instrument.text() not in self.__ClientMain.get_CTPManager().get_list_instrument_id():
            str_output = "不存在合约代码:" + self.lineEdit_a_instrument.text()
            self.label_error_msg.setText(str_output)
            return
        if self.lineEdit_b_instrument.text() not in self.__ClientMain.get_CTPManager().get_list_instrument_id():
            str_output = "不存在合约代码:" + self.lineEdit_b_instrument.text()
            self.label_error_msg.setText(str_output)
            return
        if self.lineEdit_a_instrument.text() == self.lineEdit_b_instrument.text():
            str_output = "合约代码重复" + self.lineEdit_b_instrument.text()
            self.label_error_msg.setText(str_output)
            return

        # 输入验证通过，向服务端发送创建策略指令
        if len(self.lineEdit_strategy_id.text()) == 1:
            str_strategy_id = '0' + self.lineEdit_strategy_id.text()
            self.lineEdit_strategy_id.setText(str_strategy_id)
        elif len(self.lineEdit_strategy_id.text()) == 2:
            str_strategy_id = self.lineEdit_strategy_id.text()

        # strategy_id除重判断，针对当前user_id的已经存在的策略判断
        for i_user in self.__ClientMain.get_CTPManager().get_list_user():
            if i_user.get_user_id().decode() == self.comboBox_user_id.currentText():
                for i_strategy in i_user.get_list_strategy():
                    if i_strategy.get_strategy_id() == str_strategy_id:
                        str_output = "不能重复创建策略:" + str_strategy_id
                        self.label_error_msg.setText(str_output)
                        return
            break  # 找到对应的user对象，跳出循环

        str_output = "正在创建策略：" + self.lineEdit_strategy_id.text()
        self.label_error_msg.setText(str_output)
        dict_info = {
            'trader_id': self.__ClientMain.get_TraderID(),
            'user_id': self.comboBox_user_id.currentText(),
            'strategy_id': str_strategy_id,
            'list_instrument_id': [self.lineEdit_a_instrument.text(), self.lineEdit_b_instrument.text()],
            'trade_model': '',  # 交易模型
            'order_algorithm': self.__ClientMain.get_listAlgorithmInfo()[0]['name'],  # 下单算法
            'buy_open': 0.0,
            'sell_close': 0,
            'sell_open': 0,
            'buy_close': 0,
            'spread_shift': 0,
            'a_wait_price_tick': 0,
            'b_wait_price_tick': 0,
            'stop_loss': 0,
            'lots': 0,
            'lots_batch': 0,
            'a_order_action_limit': 400,
            'b_order_action_limit': 400,
            'StrategyOnoff': 0,
            'only_close': 0,

            "position_a_sell_today": 0,
            "position_b_sell": 0,
            "position_b_sell_today": 0,
            "position_b_buy_today": 0,
            "position_a_sell": 0,
            "position_b_buy_yesterday": 0,
            "is_active": 1,
            "position_b_sell_yesterday": 0,
            "position_b_buy": 0,
            "position_a_buy": 0,
            "hold_profit": 0,
            "close_profit": 0,
            "commission": 0,
            "position": 0,
            "position_buy": 0,
            "position_sell": 0,
            "trade_volume": 0,
            "amount": 0.0,
            "average_shift": 0.0,
            "position_a_buy_yesterday": 0,
            "position_a_buy_today": 0,
            "position_a_sell_yesterday": 0
        }
        self.__ClientMain.CreateStrategy(dict_info)

    # 判断显示窗口是否是"总账户"
    def is_all_account_widget(self):
        if self.__ClientMain.get_showQAccountWidget().get_widget_name() == "总账户":
            return True
        else:
            return False

    # 初始化期货账号菜单，组件：comboBox_user_id
    def update_comboBox_user_id_menu(self):
        # 设置期货账号选项
        if self.is_all_account_widget():  # 总账户页面
            # 插入所有user_id到item
            i_row = -1
            for i_user in self.__ClientMain.get_CTPManager().get_list_user():
                if self.comboBox_user_id.findText(i_user.get_user_id().decode(), QtCore.Qt.MatchExactly) == -1:
                    i_row += 1
                    self.comboBox_user_id.insertItem(i_row, i_user.get_user_id().decode())
            # item中显示当前鼠标所选中的user_id
            for i_row in range(self.comboBox_user_id.count()):
                if self.comboBox_user_id.itemText(i_row) == self.__ClientMain.get_showQAccountWidget().get_clicked_status()['user_id']:
                    self.comboBox_user_id.setCurrentIndex(i_row)
        else:  # 单账户窗口
            self.comboBox_user_id.clear()  # 清空菜单选项
            if self.comboBox_user_id.findText(self.__ClientMain.get_showQAccountWidget().get_widget_name(), QtCore.Qt.MatchExactly) == -1:
                self.comboBox_user_id.insertItem(0, self.__ClientMain.get_showQAccountWidget().get_widget_name())

        # 清空lineEdit
        self.lineEdit_strategy_id.clear()
        self.lineEdit_a_instrument.clear()
        self.lineEdit_b_instrument.clear()
        self.label_error_msg.clear()

if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    Form = NewStrategy()
    Form.show()

    sys.exit(app.exec_())
