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
        # self.timer = QtCore.QTimer()
        # self.change_flag = True
        # self.timer.timeout.connect(self.updateModel)
        # self.timer.start(60000)
        # self.rowCheckStateMap = {}

    def slot_set_data_list(self, data_list):
        print(">>> StrategyDataModel.slot_set_data_list() data_list =", len(data_list), data_list)
        self.__data_list = copy.deepcopy(data_list)
        # print(">>> StrategyDataModel.slot_set_data_list() self.__data_list =", self.__data_list)
        self.__row = len(self.__data_list)
        # if len(data_list) > 0:
        #     print(">>> StrategyDataModel.slot_set_data_list() len(data_list) =", len(data_list), "type(data_list[0][0]) =", type(data_list[0][0]))


        if self.__row != 0:
            # self.emit(SIGNAL("layoutAboutToBeChanged()"))
            # self.layoutAboutToBeChanged.emit()
            self.__data_list = sorted(self.__data_list, key=operator.itemgetter(2))
            # if order == Qt.DescendingOrder:
            #     self.__data_list.reverse()
            # self.emit(SIGNAL("layoutChanged()"))
            # self.layoutChanged.emit()

        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

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
        if column == 0:
            # if self.__data_list[row][column].text() == '开':
            #     value = 1
            # else:
            #     value = 0
            # value = self.__data_list[row][column].text()
            value = self.__data_list[row][column]
            # value = self.__data_list[index.row()][index.column()]
        else:
            value = self.__data_list[row][column]
        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            return value
        elif role == QtCore.Qt.CheckStateRole:
            if column == 0:
                # print(">>> data() row,col = %d, %d" % (index.row(), index.column()))
                # if self.__data_list[row][column].isChecked():
                #     return QtCore.Qt.Checked
                # else:
                #     return QtCore.Qt.Unchecked
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
    # def flags(self, index):
    #     # print(">>> StrategyDataModel.flags() type(index) =", type(index))
    #     # if len(self.__q_account_widget.get_list_update_table_view_data()) == 0:
    #     #     return
    #     if not index.isValid():
    #         return None
    #     # print(">>> flags() index.column() = ", index.column(), index.row())
    #     if index.column() == 0:
    #         # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
    #         # return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
    #         # print(">>> flags() column == 0")
    #         return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
    #     else:
    #         # return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    #         # print(">>> flags() column != 0")
    #         return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def set_QAccountWidget(self, obj):
        self.__q_account_widget = obj

    """
    # 设置单个单元格数据
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        row = index.row()
        column = index.column()
        # print(">>> setData() role = ", role)
        # print(">>> setData() index.column() = ", index.column())
        # print(">>> setData() value = ", value)
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            # print(">>> setData() role = ", role)
            # print(">>> setData() index.column() = ", index.column())
            # print(">>> setData() index.value = ", value)
            # if value == QtCore.Qt.Checked:
            #     self.__data_list[row][column].setChecked(True)
            #     self.__data_list[row][column].setText("开")
            #     # if studentInfos.size() > index.row():
            #     #     emit StudentInfoIsChecked(studentInfos[index.row()])
            # else:
            #     self.__data_list[row][column].setChecked(False)
            #     self.__data_list[row][column].setText("关")
            if value == 1:
                # self.__data_list[row][column].setChecked(True)
                # self.__data_list[row][column].setText("开")
                # if studentInfos.size() > index.row():
                #     emit StudentInfoIsChecked(studentInfos[index.row()])
                return QtCore.Qt.Checked
            else:
                # self.__data_list[row][column].setChecked(False)
                # self.__data_list[row][column].setText("关")
                return QtCore.Qt.Unchecked
            pass
        else:
            pass
            # print(">>> setData() role = ", role)
            # print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        # print(">>> setData() index.row = ", index.row())
        # print(">>> setData() index.column = ", index.column())
        self.dataChanged.emit(index, index)
        return True
    """

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
