''' pqt_tableview3.py
explore PyQT's QTableView Model
using QAbstractTableModel to present tabular data
allow table sorting by clicking on the header title

used the Anaconda package (comes with PyQt4) on OS X
(dns)
'''

# coding=utf-8

import operator  # used for sorting
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
        # self.timer = QtCore.QTimer()
        # self.change_flag = True
        # self.timer.timeout.connect(self.updateModel)
        # self.timer.start(60000)
        # self.rowCheckStateMap = {}

    def setDataList(self, data_list):
        # print(">>> StrategyDataModel.setDataList() data_list =", data_list)
        # self.__data_list = data_list
        self.__data_list = [[0, '058176', '17', 'zn1705,zn1707', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 629080995, 67469229, 5.4e-323,
          2.7575735028013114e-289, 2.1219957915e-314, 0, 6.256259635004206e-309, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '07', 'cu1705,cu1707', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 1321149352, 67469252, 4e-323,
          2.7576188336738166e-289, 3e-323, 0, 3.2850879371313305e-299, 0, 0, 1321149364, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '14', 'zn1705,zn1704', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 1936028260, 574235251,
          3.453684153625054e+175, 1.7053696840786863e+256, 8.371700744886554e-144, 0, 4.263082912219336e-96, 0,
          942747439, 909192752, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '05', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 1321149239, 67469252, 3e-323,
          2.7576188336737624e-289, 3e-323, 0, 2.757618833673767e-289, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '09', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', -858856648, 67469113, 3.5e-323,
          2.7573477472540627e-289, 2e-323, 0, 2.757347747254068e-289, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '15', 'zn1705,zn1802', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 629080995, 67469229, 5.4e-323,
          2.7575735028013114e-289, 2.1219957915e-314, 0, 6.256259635004206e-309, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '04', 'ru1705,ru1704', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 1701995620, 975336307,
          2.872470422317026e+161, 4.5060609429814827e-144, 1.1607131484395217e-28, 0, 7.116394681647004e-144, 0,
          825175866, 825110584, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '06', 'rb1705,rb1712', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 1321149347, 67469252, 3e-323,
          2.75761883367376e-289, 2.1219957915e-314, 0, 6.25675067809271e-309, 0, 0, 1321149357, 0, 0, 0, 0, 0, 0, 0, 0,
          1], [0, '058176', '03', 'ru1705,ru1709', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 1701995620, 975336307,
               2.872470422317026e+161, 4.5060609429814827e-144, 1.1607131484395217e-28, 0, 7.116394681647004e-144, 0,
               825175866, 825110584, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '08', 'zn1705,zn1707', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', -858856537, 67469113, 3.5e-323,
          2.7573477472541165e-289, 1e-323, 0, 3.2850879371313305e-299, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '16', 'zn1705,zn1704', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 629080995, 67469229, 5.4e-323,
          2.7575735028013114e-289, 2.1219957915e-314, 0, 6.256259635004206e-309, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [0, '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 20, 1, 0.0, 0.0, 0.0, 0, 0.0, 0,
          400, 400, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, '058176', '02', 'rb1710,rb1705', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 80, 1, 0.0, 0.0, 0.0, 0, 0.0, 0,
          400, 400, 0, 0, 0, 0, 0, 0, 0, 0, 1]]
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
        return len(self.__data_list)

    def columnCount(self, parent):
        # print(">>> StrategyDataModel.columnCount() self.sender()= ", self.sender(), "len(self.__data_list[0]) =", len(self.__data_list[0]))
        return 17  # len(self.__data_list[0])

    # view获取数据方法
    def data(self, index, role):
        if not index.isValid():
            return None
        if (index.column() == 0):
            # value = self.__data_list[index.row()][index.column()].text()
            value = self.__data_list[index.row()][index.column()]
            # value = self.__data_list[index.row()][index.column()]
        else:
            value = self.__data_list[index.row()][index.column()]
        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            return value
        elif role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                # print(">>> data() row,col = %d, %d" % (index.row(), index.column()))
                # if self.__data_list[index.row()][index.column()].isChecked():
                #     return QtCore.Qt.Checked
                # else:
                #     return QtCore.Qt.Unchecked
                if self.__data_list[index.row()][index.column()] == 1:
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
    #     if not index.isValid():
    #         return None
        # print(">>> flags() index.column() = ", index.column())
        # if index.column() == 0:
        #     # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
        #     # return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        # else:
        #     return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    """
    # 设置单个单元格数据
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        # print(">>> setData() role = ", role)
        # print(">>> setData() index.column() = ", index.column())
        # print(">>> setData() value = ", value)
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            # print(">>> setData() role = ", role)
            # print(">>> setData() index.column() = ", index.column())
            if value == QtCore.Qt.Checked:
                self.__data_list[index.row()][index.column()].setChecked(True)
                self.__data_list[index.row()][index.column()].setText("开")
                # if studentInfos.size() > index.row():
                #     emit StudentInfoIsChecked(studentInfos[index.row()])
            else:
                self.__data_list[index.row()][index.column()].setChecked(False)
                self.__data_list[index.row()][index.column()].setText("关")
        else:
            pass
            # print(">>> setData() role = ", role)
            # print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        # print(">>> setData() index.row = ", index.row())
        # print(">>> setData() index.column = ", index.column())
        # self.dataChanged.emit(index, index)
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
