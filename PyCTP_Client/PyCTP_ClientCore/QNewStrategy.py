# -*- coding: utf-8 -*-

"""
Module implementing NewStrategy.
"""

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget
import json

from Ui_QStrategySetting import Ui_NewStrategy


class QNewStrategy(QWidget, Ui_NewStrategy):
    """
    Class documentation goes here.
    """

    signal_send_msg = QtCore.pyqtSignal(dict)  # 定义信号：新建策略窗新建策略指令 -> SocketManager.slot_send_msg

    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QNewStrategy, self).__init__(parent)
        self.setupUi(self)

        reg_strategy_id = QtCore.QRegExp('[0-9][0-9]')
        validator_strategy_id = QtGui.QRegExpValidator(reg_strategy_id)
        self.lineEdit_strategy_id.setValidator(validator_strategy_id)

        reg_instrument_id = QtCore.QRegExp('([a-z]{1,2}|[A-Z]{1,2})[0-9]{3,4}')
        validator_instrument_id = QtGui.QRegExpValidator(reg_instrument_id)
        self.lineEdit_a_instrument.setValidator(validator_instrument_id)
        self.lineEdit_b_instrument.setValidator(validator_instrument_id)

    def set_QAccountWidget(self, obj):
        self.__QAccountWidget = obj

    def set_ClientMain(self, obj_ClientMain):
        self.__client_main = obj_ClientMain

    def get_ClientMain(self):
        return self.__client_main

    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager

    def get_CTPManager(self):
        return self.__ctp_manager

    def set_SocketManager(self, obj_SocketManager):
        self.__socket_manager = obj_SocketManager

    def get_SocketManager(self):
        return self.__socket_manager

    def set_trader_id(self, str_trader_id):
        self.__trader_id = str_trader_id

    def get_trader_id(self):
        return self.__trader_id

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
        list_instrument_id = self.__socket_manager.get_list_instrument_id()
        if self.lineEdit_a_instrument.text() not in list_instrument_id:
            str_output = "不存在合约代码:" + self.lineEdit_a_instrument.text()
            self.label_error_msg.setText(str_output)
            return
        if self.lineEdit_b_instrument.text() not in list_instrument_id:
            str_output = "不存在合约代码:" + self.lineEdit_b_instrument.text()
            self.label_error_msg.setText(str_output)
            return
        if self.lineEdit_a_instrument.text() == self.lineEdit_b_instrument.text():
            str_output = "合约代码重复，请重新输入"
            self.label_error_msg.setText(str_output)
            return

        user_id = self.comboBox_user_id.currentText()

        # 策略名为两位数字，如果填写了一位数字则自动补全为两位数字
        if len(self.lineEdit_strategy_id.text()) == 1:
            str_strategy_id = '0' + self.lineEdit_strategy_id.text()
            self.lineEdit_strategy_id.setText(str_strategy_id)
        elif len(self.lineEdit_strategy_id.text()) == 2:
            str_strategy_id = self.lineEdit_strategy_id.text()

        # 检查同一个期货账户内是否已经存在重复的策略ID
        list_update_table_view_data = self.__QAccountWidget.get_list_update_table_view_data()
        for i in list_update_table_view_data:
            # print(">>> QNewStrategy.on_pushButton_ok_clicked() user_id =", i[1], type(i[1]), "strategy_id =", i[2], type(i[2]))
            if i[1] == self.comboBox_user_id.currentText() and i[2] == str_strategy_id:
                str_output = "不能重复创建策略:" + str_strategy_id
                # print(">>> QNewStrategy.on_pushButton_ok_clicked() user_id =", i[1], type(i[1]), "strategy_id =", i[2], type(i[2]), "已经存在该策略:")
                self.label_error_msg.setText(str_output)
                return

        str_output = "正在创建策略：" + self.lineEdit_strategy_id.text()
        self.label_error_msg.setText(str_output)

        # 新建策略参数
        trader_id = self.__socket_manager.get_trader_id()
        dict_strategy_args = {
            'trader_id': trader_id,
            'user_id': user_id,
            'strategy_id': str_strategy_id,
            # 'trade_model': '',  # 交易模型
            # 'order_algorithm': self.__socket_manager.get_list_algorithm_info()[0]['name'],  # 下单算法
            'a_instrument_id': self.lineEdit_a_instrument.text(),
            'b_instrument_id': self.lineEdit_b_instrument.text()
        }
        # 拼接发送报文
        dict_create_strategy = {
            'MsgRef': self.__socket_manager.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 6,  # 新建策略
            'TraderID': trader_id,
            'UserID': dict_strategy_args['user_id'],
            'Info': [dict_strategy_args]
        }
        # json_create_strategy = json.dumps(dict_create_strategy)
        self.signal_send_msg.emit(dict_create_strategy)  # 发送新建策略信号 -> SocketManager.slot_send_msg

    # 判断显示窗口是否是"总账户"
    def is_all_account_widget(self):
        if self.__client_main.get_show_widget_name() == "总账户":
            return True
        else:
            return False

    # 初始化期货账号菜单，组件：comboBox_user_id
    def update_comboBox_user_id_menu(self):
        self.comboBox_user_id.clear()  # 清空菜单选项
        tab_name = self.__QAccountWidget.get_current_tab_name()
        if tab_name == '所有账户':  # 总账户页面
            # 插入所有user_id到item
            i_row = -1
            print(">>> QNewStrategy.update_comboBox_user_id_menu() self.__socket_manager.get_list_user_info() =", self.__socket_manager.get_list_user_info())
            for i in self.__socket_manager.get_list_user_info():
                # if self.comboBox_user_id.findText(i_user.get_user_id().decode(), QtCore.Qt.MatchExactly) == -1:
                i_row += 1
                self.comboBox_user_id.insertItem(i_row, i['userid'])
            # item中显示当前鼠标所选中的user_id
            # user_id = self.__client_main.get_clicked_strategy().get_user_id()
            i_row = self.comboBox_user_id.findText(self.__QAccountWidget.get_clicked_user_id(), QtCore.Qt.MatchExactly)
            if i_row > -1:
                self.comboBox_user_id.setCurrentIndex(i_row)
        else:  # 单账户窗口
            self.comboBox_user_id.insertItem(0, tab_name)

        # 清空lineEdit
        self.lineEdit_strategy_id.clear()
        self.lineEdit_a_instrument.clear()
        self.lineEdit_b_instrument.clear()
        self.label_error_msg.clear()

if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    Form = QNewStrategy()
    Form.show()

    sys.exit(app.exec_())
