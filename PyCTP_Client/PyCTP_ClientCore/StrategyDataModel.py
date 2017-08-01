''' pqt_tableview3.py
explore PyQT's QTableView Model
using QAbstractTableModel to present tabular data
allow table sorting by clicking on the header title

used the Anaconda package (comes with PyQt4) on OS X
(dns)
'''

# coding=utf-8

import operator  # used for sorting
import copy
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore
from time import time
import threading


class StrategyDataModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """

    def __init__(self, parent=None, data_list=[], header=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.__data_list = data_list
        header = ['开关', '期货账号', '策略编号', '交易合约', '总持仓', '买持仓', '卖持仓', '保证金', '持仓盈亏', '平仓盈亏', '手续费', '净盈亏', '成交量', '成交金额', 'A成交率', 'B成交率', '交易模型', '下单算法']
        self.__header = header
        self.__row = 0
        self.__column = 0
        # self.__is_set_data = False  # 是否给数据模型设置值，初始值为False
        self.__update_once = True  # 是否更新一遍全部数据，初始值为False
        self.__set_resizeColumnsToContents_flags = False  # 设置过列宽标志位为False
        # self.timer = QtCore.QTimer()
        # self.change_flag = True
        # self.timer.timeout.connect(self.updateModel)
        # self.timer.start(60000)
        # self.rowCheckStateMap = {}

    # 更新tableView
    def slot_set_data_list(self, data_list):
        # print(">>> StrategyDataModel.slot_set_data_list() called")

        self.__row = len(data_list)  # 最新数据的长度
        # if self.__row == 0:
            # print(">>> StrategyDataModel.slot_set_data_list() if self.__row == 0: return")
            # return

        if self.__row != len(self.__data_list):
            self.__update_once = True

        # 更新tableView整个区域：已经设置过数据、数据长度相同、未切换tab页
        if self.__update_once:  # and self.__row == len_data_list and self.__QAccountWidget.get_current_tab_name() == self.__last_tab_name:
            self.__data_list = data_list
            print(">>> StrategyDataModel.slot_set_data_list() 更新tableView整个区域, len(data_list) =", len(data_list))
            t1 = self.index(0, 1)  # 左上角
            t2 = self.index(self.rowCount(0), self.columnCount(0))  # 右下角

            if True:  # not self.__set_resizeColumnsToContents_flags:
                self.__QAccountWidget.tableView_Trade_Args.resizeColumnsToContents()  # tableView列宽自动适应
                self.__QAccountWidget.tableView_Trade_Args.resizeRowsToContents()  # tableView行高自动适应
                self.__set_resizeColumnsToContents_flags = True  # 设置过列宽标志位为True
                # print(">>> StrategyDataModel.slot_set_data_list() 只需要设置一次tableView列宽")
            # # 第一列更新为checkBox
            # for i in self.__data_list:
            #     checkbox = QtGui.QCheckBox()
            #     if i[0] == 1:
            #         checkbox.setText("开")
            #         checkbox.setCheckState(QtCore.Qt.Checked)
            #     else:
            #         checkbox.setText("关")
            #         checkbox.setCheckState(QtCore.Qt.Unchecked)
            #     i[0] = checkbox
            self.layoutAboutToBeChanged.emit()  # 布局准备信号
            self.layoutChanged.emit()  # 布局执行信号
            self.dataChanged.emit(t1, t2)
            self.__update_once = False  # 更新一次界面请求的值设置为False
        # 更新tableView部分区域：一般定时刷新任务时只刷新部分
        else:
            # print(">>> StrategyDataModel.slot_set_data_list() 更新tableView部分区域")
            # self.__data_list = data_list
            for i in range(self.__row):  # range(len(data_list)):
            # for i in range(len(self.__data_list)):
                self.__data_list[i][1:] = data_list[i][1:]
                # print(">>> StrategyDataModel.slot_set_data_list() len(self.__data_list) =", len(self.__data_list), "len(data_list) =", len(data_list))
            t1 = self.index(0, 4)  # 左上角
            t2 = self.index(self.rowCount(0), self.columnCount(0))  # 右下角

            # self.layoutAboutToBeChanged.emit()  # 布局准备信号
            # if self.__row != 0:
            #     self.__data_list = sorted(self.__data_list, key=operator.itemgetter(2))  # 排序
            # self.layoutChanged.emit()  # 布局执行信号
            self.dataChanged.emit(t1, t2)  # 更新指定区域
            # self.__update_once = False  # 更新一次界面请求的值设置为False
            # print(">>>slot_set_data_list() self.__update_once = False")

        self.__last_tab_name = self.__QAccountWidget.get_current_tab_name()  # 保存最后一次tabName

    # 刷新tableView全部元素
    def update_table_view_total(self, data_list):
        self.__data_list = data_list
        # print(">>> StrategyDataModel.slot_set_data_list() 更新tableView整个区域, len(data_list) =", len(data_list))
        t1 = self.index(0, 1)  # 左上角
        t2 = self.index(self.rowCount(0), self.columnCount(0))  # 右下角

        if True:  # not self.__set_resizeColumnsToContents_flags:
            self.__QAccountWidget.tableView_Trade_Args.resizeColumnsToContents()  # tableView列宽自动适应
            self.__QAccountWidget.tableView_Trade_Args.resizeRowsToContents()  # tableView行高自动适应
            self.__set_resizeColumnsToContents_flags = True  # 设置过列宽标志位为True
        # # 第一列更新为checkBox
        # for i in self.__data_list:
        #     checkbox = QtGui.QCheckBox()
        #     if i[0] == 1:
        #         checkbox.setText("开")
        #         checkbox.setCheckState(QtCore.Qt.Checked)
        #     else:
        #         checkbox.setText("关")
        #         checkbox.setCheckState(QtCore.Qt.Unchecked)
        #     i[0] = checkbox
        self.layoutAboutToBeChanged.emit()  # 布局准备信号
        self.layoutChanged.emit()  # 布局执行信号
        self.dataChanged.emit(t1, t2)
        self.__update_once = False  # 更新一次界面请求的值设置为False

    # 针对特定的单个strategy更新界面开关，socket_manager收到修改策略开关回报时调用
    def slot_update_strategy_on_off(self, dict_args):
        current_tab_name = self.__QAccountWidget.get_current_tab_name()
        user_id = dict_args['UserID']
        strategy_id = dict_args['StrategyID']
        on_off = dict_args['OnOff']
        if current_tab_name == '所有账户' or current_tab_name == user_id:
            for i in range(len(self.__data_list)):
                if self.__data_list[i][1] == user_id and self.__data_list[i][2] == strategy_id:
                    row = i
                    print(">>> StrategyDataModel.slot_update_strategy_on_off() user_id =", user_id, "strategy_id =", strategy_id, "针对特定的单个strategy更新界面开关")
                    if on_off == 1:
                        self.__data_list[row][0].setText('开')
                        self.__data_list[row][0].setCheckState(QtCore.Qt.Checked)
                    else:
                        self.__data_list[row][0].setText('关')
                        self.__data_list[row][0].setCheckState(QtCore.Qt.Unchecked)
                    index = self.index(row, 0)
                    self.dataChanged.emit(index, index)
                    break

    def set_update_once(self, bool_input):
        self.__update_once = bool_input

    def rowCount(self, parent):
        # print(">>> StrategyDataModel.rowCount() self.sender()= ", self.sender(), "len(self.__data_list) =", len(self.__data_list))
        return self.__row

    def columnCount(self, parent):
        # print(">>> StrategyDataModel.columnCount() self.sender()= ", self.sender(), "len(self.__data_list[0]) =", len(self.__data_list[0]))
        return 17  # len(self.__data_list[0])

    # 列标题
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.__header[col]
        return None

    # 排序
    def sort(self, col, order):
        """sort table by given column number col"""
        # print(">>> sort() col = ", col)
        if col != 0:
            # self.emit(SIGNAL("layoutAboutToBeChanged()"))
            self.layoutAboutToBeChanged.emit()
            self.__data_list = sorted(self.__data_list, key=operator.itemgetter(col))
            if order == Qt.DescendingOrder:
                self.__data_list.reverse()
            # self.emit(SIGNAL("layoutChanged()"))
            self.layoutChanged.emit()

    # checkBox勾选状态
    def flags(self, index):
        # print(">>> StrategyDataModel.flags() type(index) =", type(index))
        # if len(self.__QAccountWidget.get_list_update_table_view_data()) == 0:
        #     return
        if not index.isValid():
            return QAbstractTableModel.flags(self, index)
        # print(">>> flags() index.column() = ", index.column(), index.row())
        if index.column() == 0:
            # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
            # return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
            # print(">>> flags() column == 0")
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        else:
            # return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            # print(">>> flags() column != 0")
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def set_QAccountWidget(self, obj):
        self.__QAccountWidget = obj

    # view获取数据方法
    def data(self, index, role):
        if not index.isValid():
            return None
        column = index.column()
        row = index.row()
        # 获取当前index的值
        if column == 0:
            value = self.__data_list[row][column].text()
        else:
            value = self.__data_list[row][column]
        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            if column == 0:
                if value == "关":
                    value = '关'
                else:
                    value = '开'
            return value
        # # ForegroundRole字体颜色
        # elif role == QtCore.Qt.ForegroundRole and index.column() == 1:
        #     return QtGui.QColor(255, 0, 0)
        # elif role == QtCore.Qt.ForegroundRole and index.column() == 2:
        #     return QtGui.QColor(0, 255, 0)
        # # FontRole 字体样式，加粗、斜体、字体等等
        # elif role == QtCore.Qt.FontRole and index.column() == 1:
        #     font = QtGui.QFont()
        #     font.setBold(True)
        #     return font
        # elif role == QtCore.Qt.FontRole and index.column() == 2:
        #     font = QtGui.QFont()
        #     font.setBold(True)  # 加粗
        #     return font
        # TextAlignmentRole排列字体对其样式：居中、左对齐……
        elif role == QtCore.Qt.TextAlignmentRole and column == 0:
            return QtCore.Qt.AlignVCenter
        elif role == QtCore.Qt.TextAlignmentRole and column in [1, 2, 3, 16, 16]:
            return QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        elif role == QtCore.Qt.TextAlignmentRole and column in [4,5,6,7,8,9,10,11,12,13,14,15]:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter  #
        elif role == QtCore.Qt.BackgroundRole and column == 4:  # 撇退高亮背景提示
            # A总卖==B总买 and A总买==B总卖
            if int(self.__data_list[row][30]) / self.__data_list[row][47] != int(self.__data_list[row][6]) / self.__data_list[row][48] \
                    or int(self.__data_list[row][32]) / self.__data_list[row][47] != int(self.__data_list[row][5]) / self.__data_list[row][48]:
                return QtGui.QColor(243, 209, 110)
        elif role == QtCore.Qt.BackgroundRole and column == 5:
            return QtGui.QColor(255, 221, 221)
        elif role == QtCore.Qt.BackgroundRole and column == 6:
            return QtGui.QColor(221, 255, 221)
        elif role == QtCore.Qt.CheckStateRole:
            if column == 0:
                # if value == "关":
                #     return self.__data_list[row][column].checkState()
                #     # return QtCore.Qt.Unchecked
                # else:
                #     return self.__data_list[row][column].checkState()
                #     # return QtCore.Qt.Checked
                return self.__data_list[row][column].checkState()

    # 设置单个单元格数据
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.CheckStateRole and column == 0:
            print(">>>setData() value = ", value)
            print(">>>setData() QtCore.Qt.Checked = ", QtCore.Qt.Checked)
            if value == QtCore.Qt.Checked:
                self.__data_list[row][0].setCheckState(QtCore.Qt.Checked)
                on_off = 1
            elif value == QtCore.Qt.Unchecked:
                self.__data_list[row][0].setCheckState(QtCore.Qt.Unchecked)
                on_off = 0
            dict_args = {
                'user_id': self.__data_list[row][1],
                'strategy_id': self.__data_list[row][2],
                'on_off': on_off
            }
            self.__QAccountWidget.send_msg_revise_strategy_on_off(dict_args)
        elif role == QtCore.Qt.DisplayRole:
            self.__data_list[row][4] = value
        else:
            pass
        self.dataChanged.emit(index, index)
        return True


if __name__ == '__main__':
    app = QApplication([])
    # you could process a CSV file to create this data
    header = ['开关', '只平', '期货账号', '策略编号', '交易合约', '总持仓', '买持仓', '卖持仓', '持仓盈亏', '平仓盈亏', '手续费', '净盈亏', '成交量', '成交金额',
              'A成交率', 'B成交率', '交易模型', '下单算法']
    # a list of (fname, lname, age, weight) tuples
    checkbox1 = QtGui.QCheckBox("关");
    checkbox1.setChecked(True)
    dataList = [
        [checkbox1, 0, '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtGui.QCheckBox("关"), 0, '058176', '02', 'cu1705,cu1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtGui.QCheckBox("关"), 0, '058176', '03', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtGui.QCheckBox("关"), 0, '058176', '04', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtGui.QCheckBox("关"), 0, '058176', '01', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtGui.QCheckBox("关"), 0, '058176', '02', 'ru1705,ru1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtGui.QCheckBox("关"), 0, '058176', '02', 'ni1705,ni1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtGui.QCheckBox("关"), 0, '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    ]

    # win = MyWindow(dataList, header)
    # win.show()
    # win.table_model.setDataList(dataList)
    # timer = threading.Timer(10, timer_func, (win, dataList2))
    # timer.start()
