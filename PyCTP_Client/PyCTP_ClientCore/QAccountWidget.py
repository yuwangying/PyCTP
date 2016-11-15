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
            # self.update_tableWidget_Trade_Args()
        if list_user is not None:
            self.__list_user = list_user
        self.__str_widget_name = str_widget_name

    # 自定义槽
    @pyqtSlot(str)
    def slot_SendMsg(self, msg):
        print("slot_SendMsg()", msg)
        # send json to server
        self.__sm.send_msg(msg)

    def set_user(self, obj_user):
        self.__user = obj_user

    def get_user(self):
        return self.__user

    def get_widget_name(self):
        return self.__str_widget_name

    # 设置窗口名称
    def set_widget_name(self, str_name):
        self.__widget_name = str_name

    # 传入形参：table对象和字符串，返回同名的表头所在的列标
    def getHeaderItemColumn(self, obj_tableWidget, str_column_name):
        for i in range(obj_tableWidget.rowCount()):
            if obj_tableWidget.horizontalHeaderItem(i).text() == str_column_name:
                return i
        return -1

    # 初始化策略参数表格
    def init_table_widget(self):
        if self.__widget_name == "总账户":
            pass
        else:
            i_col = 0  # table的行标
            for i in self.__user.get_list_strategy():
                i_col += 1  # table的行标
                item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
                if i.get_on_off() == 0:
                    item_strategy_on_off.setCheckState(False)
                    item_strategy_on_off.setText('关')
                elif i.get_on_off() == 1:
                    item_strategy_on_off.setCheckState(True)
                    item_strategy_on_off.setText('开')
                item_strategy_only_close = QtGui.QTableWidgetItem()  # 只平
                if i.get_on_off() == 0:
                    item_strategy_on_off.setCheckState(False)
                    item_strategy_on_off.setText('关')
                elif i.get_on_off() == 1:
                    item_strategy_on_off.setCheckState(True)
                    item_strategy_on_off.setText('开')
                item_user_id = QtGui.QTableWidgetItem(i.get_user_id())  # 期货账号
                item_strategy_id = QtGui.QTableWidgetItem(i.get_strategy_id())  # 策略编号
                str_tmp = ''
                for j in i.get_list_instrument_id():
                    str_tmp += j
                    if j != i.get_list_instrument_id()[-1]:
                        str_tmp += ','
                item_strument_id = QtGui.QTableWidgetItem(str_tmp)  # 交易合约
                item_trade_model = QtGui.QTableWidgetItem(i.get_arguments()['trade_model'])  # 交易模型
                item_order_algorithm = QtGui.QTableWidgetItem(i.get_arguments()['order_algorithm'])  # 下单算法
                item_hold_profit = QtGui.QTableWidgetItem(i.get_arguments()['hold_profit'])  # 持仓盈亏
                item_close_profit = QtGui.QTableWidgetItem(i.get_arguments()['close_profit'])  # 平仓盈亏
                item_commission = QtGui.QTableWidgetItem(i.get_arguments()['commission'])  # 手续费
                item_position = QtGui.QTableWidgetItem(i.get_arguments()['position'])  # 总持仓
                item_position_buy = QtGui.QTableWidgetItem(i.get_arguments()['position_buy'])  # 买持仓
                item_position_sell = QtGui.QTableWidgetItem(i.get_arguments()['position_sell'])  # 卖持仓
                item_trade_volume = QtGui.QTableWidgetItem(i.get_arguments()['trade_volume'])  # 成交量
                item_amount = QtGui.QTableWidgetItem(i.get_arguments()['amount'])  # 成交金额
                item_average_shift = QtGui.QTableWidgetItem(i.get_arguments()['average_shift'])  # 平均滑点
                self.tableWidget_Trade_Args.setItem(i_col, 0, item_strategy_on_off)  # 开关

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

    # 更新界面：“策略参数”框，    groupBox_trade_args
    def update_groupBox_trade_args(self, dict_args):
        pass

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
        print("on_tableWidget_Trade_Args_cellClicked() 鼠标点击位置：row %d, column %d" % (row, column))
        item = self.tableWidget_Trade_Args.item(row, column)
        print("on_tableWidget_Trade_Args_cellClicked() checkState=%d" % item.checkState())
        if item is not None:
            print("on_tableWidget_Trade_Args_cellClicked() 鼠标点击单元格值：%s" % (item.text()))

        # self.comboBox_qihuozhanghao.insertItem(0, "80000")  # 给界面空间设置值
        # print("on_tableWidget_Trade_Args_cellClicked", self.tableWidget_Trade_Args.findItems("你好", QtCore.Qt.MatchContains)[4].text())
        # print("header 0 name: ", self.tableWidget_Trade_Args.horizontalHeaderItem(0).text())
        # print("header 1 name: ", self.tableWidget_Trade_Args.horizontalHeaderItem(1).text())
        # print("列标 ", self.tableWidget_Trade_Args.column(self.tableWidget_Trade_Args.horizontalHeaderItem(1)))
        # print("表头“期货账号”所在列标：", self.getHeaderItemColumn(self.tableWidget_Trade_Args, "策略编号"))
        # self.tableWidget_Trade_Args.columnCount()

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