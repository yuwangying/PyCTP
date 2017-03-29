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
        header = ['开关', '期货账号', '策略编号', '交易合约', '总持仓', '买持仓', '卖持仓', '持仓盈亏', '平仓盈亏', '手续费', '净盈亏', '成交量', '成交金额', 'A成交率', 'B成交率', '交易模型', '下单算法']
        self.__header = header
        self.__row = 0
        self.__column = 0
        self.__is_set_data = False  # 是否给数据模型设置值，初始值为False
        self.__update_once = False  # 是否更新一遍全部数据，初始值为False
        # self.timer = QtCore.QTimer()
        # self.change_flag = True
        # self.timer.timeout.connect(self.updateModel)
        # self.timer.start(60000)
        # self.rowCheckStateMap = {}

    """
    # 更新tableView内全部元素
    def slot_set_data_list(self, data_list):
        # print(">>> StrategyDataModel.slot_set_data_list() data_list =", len(data_list), data_list)
        # print(">>> StrategyDataModel.slot_set_data_list() called")
        # self.__data_list = copy.deepcopy(data_list)
        self.__data_list = data_list
        self.__row = len(self.__data_list)
        # if self.__row != 0:
            # self.__data_list = sorted(self.__data_list, key=operator.itemgetter(2))
            # self.emit(SIGNAL("layoutAboutToBeChanged()"))
            # self.layoutAboutToBeChanged.emit()
            # if order == Qt.DescendingOrder:
            #     self.__data_list.reverse()
            # self.emit(SIGNAL("layoutChanged()"))
            # self.layoutChanged.emit()
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()
    """

    # 更新tableView
    def slot_set_data_list(self, data_list):
        # print(">>> StrategyDataModel.slot_set_data_list() called")
        len_data_list = len(data_list)  # 最新数据的长度
        # 已经设置过数据、数据长度相同、未切换tab页
        if not self.__update_once and self.__is_set_data and self.__row == len_data_list and self.__QAccountWidget.get_current_tab_name() == self.__last_tab_name:
            t1 = self.index(0, 1)  # 左上角
            t2 = self.index(self.rowCount(0), self.columnCount(0))  # 右下角
            self.dataChanged.emit(t1, t2)
        else:
            self.__data_list = data_list
            self.__row = len(self.__data_list)
            if self.__row != 0:
                self.__is_set_data = True
            self.layoutAboutToBeChanged.emit()
            if self.__row != 0:
                self.__data_list = sorted(self.__data_list, key=operator.itemgetter(2))
            self.layoutChanged.emit()
            self.__update_once = False  # 更新一次界面请求的值设置为False
            print(">>>slot_set_data_list() self.__update_once = False")

        self.__last_tab_name = self.__QAccountWidget.get_current_tab_name()  # 保存最后一次tabName

    def set_update_once(self, bool_input):
        self.__update_once = bool_input

    # def updateModel(self):
    #     dataList2 = []
    #     if self.change_flag is True:
    #         dataList2 = [
    #             [QtGui.QCheckBox("关"), 0, '063802', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '063802', '02', 'cu1705,cu1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '063802', '03', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '063802', '04', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '063802', '01', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '063802', '02', 'ru1705,ru1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '063802', '02', 'ni1705,ni1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '063802', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #         ]
    #         self.change_flag = False
    #     elif self.change_flag is False:
    #         dataList2 = [
    #             [QtGui.QCheckBox("关"), 0, '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '058176', '02', 'cu1705,cu1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #             [QtGui.QCheckBox("关"), 0, '058176', '03', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    #         ]
    #         self.change_flag = True
    #
    #     self.__data_list = dataList2
    #     self.layoutAboutToBeChanged.emit()
    #     # self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))  # 更新整个view
    #     self.dataChanged.emit(self.createIndex(2, 3),
    #                           self.createIndex(self.rowCount(0), self.columnCount(0)))  # 更新特定item
    #     self.layoutChanged.emit()

    def rowCount(self, parent):
        # print(">>> StrategyDataModel.rowCount() self.sender()= ", self.sender(), "len(self.__data_list) =", len(self.__data_list))
        return self.__row

    def columnCount(self, parent):
        # print(">>> StrategyDataModel.columnCount() self.sender()= ", self.sender(), "len(self.__data_list[0]) =", len(self.__data_list[0]))
        return 17  # len(self.__data_list[0])

    # view获取数据方法
    def data(self, index, role):
        if not index.isValid():
            return None
        column = index.column()
        row = index.row()

        value = self.__data_list[row][column]
        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            if column == 0:
                if value == 0:
                    value = '关'
                else:
                    value = '开'
            return value
        elif role == QtCore.Qt.CheckStateRole:
            if column == 0:
                if self.__data_list[row][column] == 1:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

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

    # 设置单个单元格数据
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.CheckStateRole and column == 0:
            if value == QtCore.Qt.Checked:
                self.__data_list[row][0] = 1
                on_off = 1
            elif value == QtCore.Qt.Unchecked:
                self.__data_list[row][0] = 0
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
