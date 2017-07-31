# -*- coding: utf-8 -*-

"""
Module implementing QAccountWidget.
"""
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import QPoint, QModelIndex
from PyQt4.QtGui import QTabBar
from Ui_QAccountWidget import Ui_Form
import json
import queue
from Strategy import Strategy
from MessageBox import MessageBox
from QNewStrategy import QNewStrategy
from PyQt4.QtGui import QApplication, QCompleter, QLineEdit, QStringListModel
from StrategyDataModel import StrategyDataModel
import threading
import time


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

"""
function structure
1. slot_update_strategy(obj_strategy)
    调用情景：发送参数（一个策略）、查询参数（所有策略）

2. update_statistics(obj_strategy)
    调用情景：成交回报（一个策略）、市场行情变化（一个策略）

3. update_spread()
    调用情景：市场行情变化（一个策略）

4. update_account_info()
    调用情景：查询账户、市场行情变化（定时任务0.5秒）
"""


class QAccountWidget(QWidget, Ui_Form):
    """
    Class documentation goes here.
    """
    Signal_SendMsg = QtCore.pyqtSignal(str)  # 自定义信号
    signal_update_groupBox_trade_args_for_query = QtCore.pyqtSignal(Strategy)  # 定义信号：更新界面参数框
    signal_send_msg = QtCore.pyqtSignal(dict)  # 窗口修改策略 -> SocketManager发送修改指令
    signal_show_QMessageBox = QtCore.pyqtSignal(list)  # 定义信号：弹窗 -> ClientMain(主线程)中槽函数调用弹窗
    signal_lineEdit_duotoujiacha_setText = QtCore.pyqtSignal(str)  # 定义信号：多头价差lineEdit更新
    signal_lineEdit_kongtoujiacha_setText = QtCore.pyqtSignal(str)  # 定义信号：self.lineEdit_kongtoujiacha.setText()
    signal_lineEdit_duotoujiacha_setStyleSheet = QtCore.pyqtSignal(str)  # 定义信号：lineEdit_duotoujiacha.setStyleSheet()
    signal_lineEdit_kongtoujiacha_setStyleSheet = QtCore.pyqtSignal(str)  # 定义信号：lineEdit_kongtoujiacha.setStyleSheet()
    signal_update_ui = QtCore.pyqtSignal()  # 定义信号：定时刷新UI
    signal_show_alert = QtCore.pyqtSignal(dict)  # 定义信号：显示弹窗

    # QAccountWidget(ClientMain=self.__client_main,
    #                CTPManager=self,
    #                SocketManager=self.__socket_manager,
    #                User=self)
    # def __init__(self, str_widget_name, obj_user=None, list_user=None, parent=None, ClientMain=None, SocketManager=None, CTPManager=None):
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QAccountWidget, self).__init__(parent)
        self.__total_process_finished = False  # 所有进程初始化完成标志位，初始值为False
        self.__init_finished = False  # QAccountWidget界面初始化完成标志位，初始值为False
        self.__set_socket_manager = False  # 设置了socket_manager为本类属性
        self.__allow_update_group_box_position = True  # 允许更新groupBox持仓变量标志位，初始值为true
        self.__len_list_update_table_view_data = 0  # tableView数据长度

        self.setupUi(self)  # 调用父类中配置界面的方法
        self.tableView_Trade_Args.setSortingEnabled(True)
        self.tableView_Trade_Args.horizontalHeader().setMovable(True)
        self.popMenu = QtGui.QMenu(self.tableView_Trade_Args)  # 创建鼠标右击菜单
        self.tableView_Trade_Args.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.tableView_Trade_Args.resizeColumnsToContents()  # tableView列宽自动适应
        # self.tableView_Trade_Args.resizeRowsToContents()  # tableView行高自动适应

        self.tabBar = QtGui.QTabBar(self.widget_tabbar)  # 创建QTabBar，选项卡
        self.tabBar.currentChanged.connect(self.slot_tab_changed)  # 信号槽连接：信号为自带的currentChanged，槽函数为slot_tab_changed，QTabBar切换tab时触发
        self.__dict_clicked_info = {'所有账户': {}}  # 记录鼠标点击策略，{tab_name: strategy_id,}
        self.__current_tab_name = ''
        self.__clicked_user_id = ''  # 初始化鼠标点击的策略的user_id
        self.__clicked_strategy_id = ''  # 初始化鼠标点击的策略的strategy_id
        self.__clicked_strategy_on_off = '关'  # 初始化鼠标点击策略的开关显示值
        self.__list_update_widget_data = list()  # 界面tableView正在显示和更新的数据，有SocketManager通过信号槽发送来
        self.slot_addTabBar("所有账户")

        self.__spread_long = 0  # 界面价差初始值
        self.__spread_long_last = 0
        self.__spread_short = 0
        self.__spread_short_last = 0

        self.__Queue_sub_instrument = queue.Queue(maxsize=100)  # 需要订阅行情的合约代码Queue

        # 设置tableWidget列的宽度
        # self.tableWidget_Trade_Args.setColumnWidth(0, 50)  # 开关
        # self.tableWidget_Trade_Args.setColumnWidth(1, 90)  # 期货账号
        # self.tableWidget_Trade_Args.setColumnWidth(2, 90)  # 策略编号
        # self.tableWidget_Trade_Args.setColumnWidth(3, 120)  # 交易合约
        # self.tableWidget_Trade_Args.setColumnWidth(4, 90)  # 总持仓
        # self.tableWidget_Trade_Args.setColumnWidth(5, 90)  # 买持仓
        # self.tableWidget_Trade_Args.setColumnWidth(6, 90)  # 卖持仓
        # self.tableWidget_Trade_Args.setColumnWidth(7, 90)  # 持仓盈亏
        # self.tableWidget_Trade_Args.setColumnWidth(8, 90)  # 平仓盈亏
        # self.tableWidget_Trade_Args.setColumnWidth(9, 90)  # 手续费
        # self.tableWidget_Trade_Args.setColumnWidth(10, 90)  # 净盈亏
        # self.tableWidget_Trade_Args.setColumnWidth(11, 90)  # 成交量
        # self.tableWidget_Trade_Args.setColumnWidth(12, 90)  # 成交额
        # self.tableWidget_Trade_Args.setColumnWidth(13, 90)  # A成交率
        # self.tableWidget_Trade_Args.setColumnWidth(14, 90)  # B成交率
        # self.tableWidget_Trade_Args.setColumnWidth(15, 90)  # 交易模型
        # self.tableWidget_Trade_Args.setColumnWidth(16, 90)  # 下单算法
        # 初始化comboBox_jiaoyimoxing
        # 客户端存储的交易模型可选项，服务端仅保留策略所设置交易模型，当前交易模型空白
        # 初始化comboBox_xiadansuanfa
        # index_item = -1
        # for i in self.__socket_manager.get_list_algorithm_info():
        #     index_item += 1
        #     self.comboBox_xiadansuanfa.insertItem(index_item, i['name'])

        # 添加策略菜单
        self.action_add = QtGui.QAction("添加策略", self)
        self.action_add.setIcon(QtGui.QIcon("image/add_strategy.ico"))
        self.action_add.triggered.connect(self.slot_action_add_strategy)
        self.popMenu.addAction(self.action_add)

        # 删除策略菜单
        self.action_del = QtGui.QAction("删除策略", self)
        self.action_del.setIcon(QtGui.QIcon("image/delete_strategy.ico"))
        self.action_del.triggered.connect(self.slot_action_del_strategy)
        self.popMenu.addAction(self.action_del)

        # 创建数据模型
        self.StrategyDataModel = StrategyDataModel(parent=self)
        self.StrategyDataModel.set_QAccountWidget(self)
        # 对tableView_Trade_Args设置数据模型对象
        self.tableView_Trade_Args.setModel(self.StrategyDataModel)

        # 定时刷新UI线程
        # self.__timer_thread = threading.Thread(target=self.thread_update_ui)
        # self.__timer_thread.daemon = True
        # self.__timer_thread.start()  # 待续，策略全部初始化完成之后再开始线程，2017年3月21日14:27:33
        self.__timer = QtCore.QTimer()  # 定时器
        self.__timer.setInterval(500)  # 时间间隔500ms
        self.__timer.setSingleShot(False)  # 非一次性定时器
        self.__timer.timeout.connect(self.slot_update_ui)  # 连接信号槽
        self.__timer.start()

        # self.__timer_thread = threading.Thread(target=self.thread_update_tableView)
        # self.__timer_thread.daemon = True
        # self.__timer_thread.start()

        self.__thread_market_manager = threading.Thread(target=self.subscription_market)
        self.__thread_market_manager.daemon = True
        self.__thread_market_manager.start()

    # 固定数据测试
    # def thread_update_tableView(self):
    #     self.StrategyDataModel.slot_set_data_list([])

    # 初始化创建tableWidget内的item，根据期货账户的策略数量总和来决定行数
    def slot_init_tableWidget(self, list_strategy_data):
        # print("QAccountWidget.slot_init_tableWidget() list_strategy_data =", list_strategy_data)
        for i in list_strategy_data:
            self.slot_insert_strategy(i)

    # 右击“添加删除策略”菜单消失时初始化鼠标点击信息
    def slot_init_right_click(self):
        self.__right_clicked_user_id = ''
        self.__right_clicked_strategy_id = ''

    # 初始化界面中groupBox的下单算法选项
    def slot_init_groupBox_order_algorithm(self, list_input):
        print(">>> init_groupBox_order_algorithm() 初始化下单算法", list_input)
        for i in range(len(list_input)):
            self.comboBox_xiadansuanfa.insertItem(i, list_input[i]['name'])

    # py自带thread实现定时器，定时刷新UI线程
    def thread_update_ui(self):
        while True:

            self.signal_update_ui.emit()  # 定时刷新UI信号
            time.sleep(1)

    # 订阅行情
    def subscription_market(self):
        while True:
            # print(">>> QAccountWidget.subscription_market() self.__Queue_sub_instrument.qsize() =", self.__Queue_sub_instrument.qsize())
            list_instrument_id = self.__Queue_sub_instrument.get()
            if list_instrument_id == self.__clicked_list_instrument_id:
                print("QAccountWidget.subscription_market() 订阅行情：", list_instrument_id)
                self.__socket_manager.get_market_manager().group_box_sub_market(list_instrument_id)
            else:
                print("QAccountWidget.subscription_market() 跳过订阅行情：", list_instrument_id)

    # Qt库函数定时器，定时刷新UI槽函数
    def slot_update_ui(self):
        # 更新界面tableView
        list_update_table_view_data = self.get_list_update_table_view_data()
        self.StrategyDataModel.slot_set_data_list(list_update_table_view_data)
        len_list_update_table_view_data = len(list_update_table_view_data)
        if self.__len_list_update_table_view_data != len_list_update_table_view_data:  # 数据长度有变化时界面刷新全部区域
            self.StrategyDataModel.set_update_once(True)  # 设置更新tableView全部区域的标志位True
            # self.StrategyDataModel.update_table_view_total(list_update_table_view_data)
            # print(">>> QAccountWidget.slot_update_ui()数据长度有变化时界面刷新全部区域,之前长度和之后长度", self.__len_list_update_table_view_data, len_list_update_table_view_data)
        self.__len_list_update_table_view_data = len_list_update_table_view_data
        # print(">>> QAccountWidget.slot_update_ui()", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "len(list_update_table_view_data) =", len_list_update_table_view_data)

        # 更新界面groupBox
        list_update_group_box_data = self.get_list_update_group_box_data()
        if len(list_update_group_box_data) > 0:
            self.slot_update_group_box_statistics()
        else:
            self.clear_group_box()

        # 更新界面panel_show_account
        list_update_panel_show_account = self.__socket_manager.get_list_panel_show_account()
        if len(list_update_panel_show_account) > 0:
            self.slot_update_panel_show_account(list_update_panel_show_account)

    def slot_addTabBar(self, user_id):
        self.__dict_clicked_info[user_id] = {}
        # self.tabBar.addTab(QtGui.QIcon("image/disactive.ico"), user_id)
        self.tabBar.addTab(user_id)
        print("QAccountWidget.slot_addTabBar() self.__dict_clicked_info =", self.__dict_clicked_info)

    # 设置tab样式： 0运行，1非运行
    def slot_setTabIcon(self, on_off):
        int_tab_index = self.tabBar.currentIndex()
        if on_off == 1:
            self.pushButton_start_strategy.setText('停止策略')
            self.tabBar.setTabIcon(int_tab_index, QtGui.QIcon("image/active.ico"))  # tab样式为开
        else:
            self.pushButton_start_strategy.setText('开始策略')
            self.tabBar.setTabIcon(int_tab_index, QtGui.QIcon("image/disactive.ico"))  # tab样式为关

    # 初始化所有tab的样式
    def slot_init_setTabIcon(self):
        print(">>> slot_init_setTabIcon()")
        for user_id in self.__socket_manager.get_dict_tab_index():
            tab_index = self.__socket_manager.get_dict_tab_index()[user_id]
            on_off = self.__socket_manager.get_dict_user_on_off()[user_id]
            if on_off == 1:
                self.tabBar.setTabIcon(tab_index, QtGui.QIcon("image/active.ico"))
            else:
                self.tabBar.setTabIcon(tab_index, QtGui.QIcon("image/disactive.ico"))

    def showEvent(self, QShowEvent):
        pass
        # print(">>> showEvent()", self.objectName(), "widget_name=", self.__widget_name)
        # self.__client_main.set_show_widget(self)  # 显示在最前端的窗口设置为ClientMain的属性，全局唯一
        # self.__client_main.set_show_widget_name(self.__widget_name)  # 显示在最前端的窗口名称设置为ClientMain的属性，全局唯一
        # 获取tab——name
        # print(">>> tabName")
        # self.__client_main.set_showEvent(True)  # 是否有任何窗口显示了

    def hideEvent(self, QHideEvent):
        pass
        # print(">>> hideEvent()", self.objectName(), "widget_name=", self.__widget_name)
        # self.__client_main.set_hideQAccountWidget(self)  # 将当前隐藏的窗口对象设置为ClienMain类的属性

    # 交易员登录成功，主界面“开始策略”关闭策略
    def slot_init_ui_on_off(self, int_input):
        if int_input == 1:
            self.pushButton_start_strategy.setText('停止策略')
        else:
            self.pushButton_start_strategy.setText('开始策略')

    # 槽函数，连接信号：QCTP.signal_on_tab_accounts_currentChanged，切换tab页的时候动态设置obj_user给QAccountWidget
    def slot_tab_changed(self, int_tab_index):
        self.__current_tab_index = int_tab_index  # 保存当前tab的index
        self.__current_tab_name = self.tabBar.tabText(int_tab_index)
        self.on_pushButton_set_position_active()  # 激活设置持仓按钮，设置持仓参数框设置只读
        # print(">>> QAccountWidget.slot_tab_changed() self.__current_tab_name =", self.__current_tab_name)
        if self.get_total_process_finished():  # 所有子进程初始化完成
            self.StrategyDataModel.set_update_once(True)  # 设置定时任务中刷新一次全部tableView
        # 更新期货账户开关或所有账户开关按钮
        # if self.__total_process_finished:  # 所有进程初始化完成标志位，初始值为False
        if self.__set_socket_manager:  # 所有进程初始化完成标志位，初始值为False
            on_off = self.__socket_manager.get_dict_user_on_off()[self.__current_tab_name]
            if on_off == 1:
                self.pushButton_start_strategy.setText('停止策略')
                self.tabBar.setTabIcon(int_tab_index, QtGui.QIcon("image/active.ico"))  # tab样式为开
            else:
                self.pushButton_start_strategy.setText('开始策略')
                self.tabBar.setTabIcon(int_tab_index, QtGui.QIcon("image/disactive.ico"))  # tab样式为关

        # if self.tableView_Trade_Args.StrategyDataModel is not None:
        # if self.tableView_Trade_Args.model() is not None:
        #     self.tableView_Trade_Args.StrategyDataModel.set_update_once(True)  # 更新一次tableView内全部index
        # print(">>> QAccountWidget.slot_tab_changed() self.__current_tab_name =", self.__current_tab_name, "int_tab_index =", int_tab_index)
        # print(">>> QAccountWidget.slot_tab_changed() self.__dict_clicked_info =", self.__dict_clicked_info)
        # print("QAccountWidget.slot_tab_changed() self.__current_tab_name =", self.__current_tab_name)
        dict_tab_clicked_info = self.__dict_clicked_info[self.__current_tab_name]
        # print(">>> QAccountWidget.slot_tab_changed() dict_tab_clicked_info =", len(dict_tab_clicked_info), dict_tab_clicked_info)
        # 主动触发鼠标单击事件
        if len(dict_tab_clicked_info) > 0:  # 该tab页中存在策略，且鼠标点击过
            # print("QAccountWidget.slot_tab_changed() if len(dict_tab_clicked_info) > 0:")
            row = dict_tab_clicked_info['row']
            column = dict_tab_clicked_info['column']
            self.__clicked_user_id = self.__dict_clicked_info[self.__current_tab_name]['user_id']
            self.__clicked_strategy_id = self.__dict_clicked_info[self.__current_tab_name]['strategy_id']

            list_update_table_view_data = self.get_list_update_table_view_data()
            # self.StrategyDataModel.set_update_once(True)
            self.StrategyDataModel.slot_set_data_list(list_update_table_view_data)  # 更新界面tableView

            list_update_group_box_data = self.get_list_update_group_box_data()
            if len(list_update_group_box_data) > 0:
                self.slot_update_group_box()  # 切换tab时更新groupBox中所有元素一次
                # print(">>> QAccountWidget.slot_tab_changed() 切换tab时更新groupBox中所有元素一次")
            else:
                self.clear_group_box()

            # selection_model = QtGui.QItemSelectionModel(self.tableView_Trade_Args.model())
            # self.tableView_Trade_Args.setSelectionModel(selection_model)
            # self.tableView_Trade_Args.selectionModel().select(index, QtGui.QItemSelectionModel.Select)
            # self.tableView_Trade_Args.setCurrentIndex(index)
            # self.tableView_Trade_Args.setFocus()
            # 主动触发鼠标单击事件，还原记忆中tab点击位置

        else:
            self.__clicked_user_id = ''
            self.__clicked_strategy_id = ''
        # self.slot_set_data_list([])  # 切换tab时清空tableView
        # if len(self.__dict_clicked_info[self.__current_tab_name]) > 0:
        #     row = self.__dict_clicked_info[self.__current_tab_name]['row']
            # self.tableWidget_Trade_Args.setCurrentCell(row, 0)
        # 待续，2017年3月26日23:20:18，切换tab的时候设置记忆中的行，可用方法setCurrentIndex
        # self.update_tableWidget_Trade_Args()
        # 初始化一遍tableWidget
        # self.slot_init_tableWidget(self.get_update_tableWidget_data())
        # self.update_groupBox()

    # 设置tableView更新所需数据
    # def slot_set_data_list(self, data_list):
        # print(">>> QAccountWidget.slot_set_data_list() data_list =", len(data_list), data_list)
        # self.__list_update_widget_data = data_list
        # self.StrategyDataModel.slot_set_data_list(data_list)

    # 更新界面行情：[多头价差, 空头价差]
    def slot_update_spread_ui(self, list_data):
        # print(">>> QAccountWidget.slot_update_spread_ui() list_data =", list_data)
        # self.__spread_long = list_data[0]
        # self.__spread_short = list_data[1]
        if len(self.__list_update_group_box_data) == 0:
            self.lineEdit_duotoujiacha.setText('')
            self.lineEdit_kongtoujiacha.setText('')
            return
        a_scale = self.__list_update_group_box_data[47]  # A合约乘数
        b_scale = self.__list_update_group_box_data[48]  # B合约乘数
        self.__spread_long = round(list_data[0] * a_scale - list_data[3] * b_scale, 2)
        self.__spread_short = round(list_data[1] * a_scale - list_data[2] * b_scale, 2)
        # print(">>> QAccountWidget.slot_update_spread_ui() self.__spread_long =", self.__spread_long, "self.__spread_short =", self.__spread_short)
        if self.__spread_long != self.__spread_long_last:
            # print(">>> QAccountWidget.slot_update_spread_ui() 更新多头价差", self.__spread_long)
            self.lineEdit_duotoujiacha.setText(str(self.__spread_long))
            pass
        if self.__spread_short != self.__spread_short_last:
            # print(">>> QAccountWidget.slot_update_spread_ui() 更新空头价差", self.__spread_short)
            self.lineEdit_kongtoujiacha.setText(str(self.__spread_short))
            pass
        self.__spread_long_last = self.__spread_long
        self.__spread_short_last = self.__spread_short

    def set_ClientMain(self, obj_ClientMain):
        self.__client_main = obj_ClientMain

    def get_ClientMain(self):
        return self.__client_main

    def set_SocketManager(self, obj_SocketManager):
        self.__set_socket_manager = True
        self.__socket_manager = obj_SocketManager

    def get_SocketManager(self):
        return self.__socket_manager

    def set_QLogin(self, obj_QLogin):
        self.__q_login = obj_QLogin

    def get_QLogin(self):
        return self.__q_login

    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager

    def get_CTPManager(self):
        return self.__ctp_manager

    # 形参为user对象或ctpmanager对象，ctpmanager代表所有期货账户对象的总和
    def set_user(self, obj_user):
        self.__user = obj_user

    def set_allow_update_group_box_position(self, bool_input):
        self.__allow_update_group_box_position = bool_input

    def get_allow_update_group_box_position(self):
        return self.__allow_update_group_box_position

    def get_user(self):
        return self.__user

    def get_current_tab_name(self):
        return self.__current_tab_name

    def get_widget_name(self):
        # print(">>> QAccountWidget.get_widget_name() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        return self.__widget_name

    def get_clicked_user_id(self):
        return self.__clicked_user_id

    def get_clicked_strategy_id(self):
        return self.__clicked_strategy_id

    def set_clicked_strategy_on_off(self, bool_input):
        self.__clicked_strategy_on_off = bool_input

    def get_clicked_strategy_on_off(self):
        return self.__clicked_strategy_on_off

    def get_group_box_price_tick(self):
        return self.__group_box_price_tick

    def set_total_process_finished(self, bool_input):
        self.__total_process_finished = bool_input

    def get_total_process_finished(self):
        return self.__total_process_finished

    # 设置窗口名称
    def set_widget_name(self, str_name):
        # print(">>> QAccountWidget.set_widget_name() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        self.__widget_name = str_name

    # 设置鼠标点击状态，信息包含:item所在行、item所在列、widget_name、user_id、strategy_id
    def set_clicked_status(self, dict_input):
        self.__clicked_status = dict_input
        self.__client_main.set_clicked_status(dict_input)  # 保存鼠标点击状态到ClientMain的属性，保存全局唯一一个鼠标最后点击位置
        item = self.tableWidget_Trade_Args.item(dict_input['row'], dict_input['column'])
        self.__client_main.set_clicked_item(item)  # 鼠标点击的item设置为ClientMain的属性，全局唯一
        print(">>> QAccountWidget.set_clicked_status() widget_name=", self.__widget_name, 'user_id=', self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])

    # return dict()
    def get_clicked_status(self):
        print(">>> QAccountWidget.get_clicked_status() self.sender()=", self.sender(), " widget_name=", self.__widget_name, 'user_id=',
              self.__clicked_status['user_id'], 'strategy_id=', self.__clicked_status['strategy_id'])
        return self.__clicked_status

    def set_list_strategy(self, list_strategy):
        self.__list_strategy = list_strategy

    def get_list_strategy(self):
        return self.__list_strategy

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

    # 获取更新talbeView的数据
    def get_list_update_table_view_data(self):
        # 组织刷新tableView的数据
        self.__list_update_table_view_data = list()
        if self.__current_tab_name == '所有账户':
            dict_table_view_data = self.__socket_manager.get_dict_table_view_data()
            for i in dict_table_view_data:
                self.__list_update_table_view_data.extend(dict_table_view_data[i])
        else:
            self.__list_update_table_view_data = self.__socket_manager.get_dict_table_view_data()[self.__current_tab_name]
        return self.__list_update_table_view_data

    # 获取更新groupBox的数据
    def get_list_update_group_box_data(self):
        self.__list_update_group_box_data = list()
        # 组织刷新groupBox数据，当期货账户不存在策略时，list长度为0
        if len(self.__list_update_table_view_data) > 0:  # 当存在需要更新tableView的策略信息
            for i in self.__list_update_table_view_data:
                if i[1] == self.__clicked_user_id and i[2] == self.__clicked_strategy_id:
                    self.__list_update_group_box_data = i
                    break
        return self.__list_update_group_box_data

    # 判断当前窗口是否单账户
    def is_single_user_widget(self):
        if self.__widget_name == "总账户":
            return False
        else:
            return True

    # 创建“新建策略窗口”
    def create_QNewStrategy(self):
        # print(">>> QAccountWidget.create_QNewStrategy()")
        self.__q_new_strategy = QNewStrategy()

        # 设置图标
        self.__q_new_strategy.setWindowIcon(QtGui.QIcon(':/image/bee.ico'))
        completer = QCompleter()
        model = QStringListModel()
        list_instrument_id = self.__socket_manager.get_list_instrument_id()
        model.setStringList(list_instrument_id)
        completer.setModel(model)
        self.__q_new_strategy.lineEdit_a_instrument.setCompleter(completer)
        self.__q_new_strategy.lineEdit_b_instrument.setCompleter(completer)
        self.__q_new_strategy.set_QAccountWidget(self)
        self.__q_new_strategy.set_SocketManager(self.__socket_manager)
        self.__socket_manager.set_QNewStrategy(self.__q_new_strategy)
        # self.__q_new_strategy.set_CTPManager(self)  # CTPManager设置为新建策略窗口属性
        # self.__q_new_strategy.set_SocketManager(self.__socket_manager)  # SocketManager设置为新建策略窗口属性
        # self.__q_new_strategy.set_trader_id(self.__trader_id)  # 设置trade_id属性
        # self.__client_main.set_QNewStrategy(self.__q_new_strategy)  # 新建策略窗口设置为ClientMain属性
        # self.signal_hide_QNewStrategy.connect(self.get_QNewStrategy().hide)  # 绑定信号槽，新创建策略成功后隐藏“新建策略弹窗”

        # 绑定信号槽：新建策略窗新建策略指令 -> SocketManager.slot_send_msg
        self.__q_new_strategy.signal_send_msg.connect(self.__socket_manager.slot_send_msg)
        # 绑定信号槽：SocketManager收到新建策略回报 -> QNewStrategy隐藏“新建策略窗口”
        self.__socket_manager.signal_QNewStrategy_hide.connect(self.__q_new_strategy.hide)

    """
    # 向界面插入策略，形参是任何策略对象，该方法自动判断策略是否属于本窗口
    @QtCore.pyqtSlot(object)
    def slot_insert_strategy(self, obj_strategy):
        # 总账户窗口或策略所属的单账户窗口
        if self.is_single_user_widget() is False or obj_strategy.get_user_id() == self.__widget_name:
            i_row = self.tableWidget_Trade_Args.rowCount()  # 将要出入到的行标
            self.tableWidget_Trade_Args.insertRow(i_row)
            print(">>> QAccountWidget.slot_insert_strategy() 添加策略，widget_name=", self.__widget_name, "i_row=", i_row, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id(), "self.sender=", self.sender())
            dict_strategy_args = obj_strategy.get_arguments()  # 获取策略参数
            dict_position = obj_strategy.get_position()  # 获取策略持仓
            item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
            if dict_strategy_args['strategy_on_off'] == 0:
                item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
                item_strategy_on_off.setText('关')
            elif dict_strategy_args['strategy_on_off'] == 1:
                item_strategy_on_off.setCheckState(QtCore.Qt.Checked)
                item_strategy_on_off.setText('开')
            # item_strategy_only_close = QtGui.QTableWidgetItem()  # 只平
            # if dict_strategy_args['only_close'] == 0:
            #     item_strategy_only_close.setCheckState(QtCore.Qt.Unchecked)
            #     item_strategy_only_close.setText('关')
            # elif dict_strategy_args['only_close'] == 1:
            #     item_strategy_only_close.setCheckState(QtCore.Qt.Checked)
            #     item_strategy_only_close.setText('开')
            item_user_id = QtGui.QTableWidgetItem(obj_strategy.get_user_id())  # 期货账号
            item_strategy_id = QtGui.QTableWidgetItem(obj_strategy.get_strategy_id())  # 策略编号
            # str_tmp = ''
            # for j in obj_strategy.get_list_instrument_id():
            #     str_tmp += j
            #     if j != obj_strategy.get_list_instrument_id()[-1]:
            #         str_tmp += ','
            str_tmp = obj_strategy.get_a_instrument_id() + obj_strategy.get_b_instrument_id()
            item_instrument_id = QtGui.QTableWidgetItem(str_tmp)  # 交易合约
            item_position = QtGui.QTableWidgetItem(str(dict_position['position_a_buy'] + dict_position['position_a_sell']))  # 总持仓
            item_position_buy = QtGui.QTableWidgetItem(str(dict_position['position_a_buy']))  # 买持仓
            item_position_sell = QtGui.QTableWidgetItem(str(dict_position['position_a_sell']))  # 卖持仓
            item_position_profit = QtGui.QTableWidgetItem('-')  # 持仓盈亏
            item_close_profit = QtGui.QTableWidgetItem('-')  # 平仓盈亏
            item_commission = QtGui.QTableWidgetItem('-')  # 手续费
            item_profit = QtGui.QTableWidgetItem('-')  # 净盈亏
            item_trade_count = QtGui.QTableWidgetItem('-')  # 成交量
            item_amount = QtGui.QTableWidgetItem('-')  # 成交金额
            item_a_trade_rate = QtGui.QTableWidgetItem('-')  # A成交率
            item_b_trade_rate = QtGui.QTableWidgetItem('-')  # B成交率
            item_trade_model = QtGui.QTableWidgetItem(dict_strategy_args['trade_model'])  # 交易模型
            item_order_algorithm = QtGui.QTableWidgetItem(dict_strategy_args['order_algorithm'])  # 下单算法
            self.tableWidget_Trade_Args.setItem(i_row, 0, item_strategy_on_off)  # 开关
            # self.tableWidget_Trade_Args.setItem(i_row, 1, item_strategy_only_close)  # 只平
            self.tableWidget_Trade_Args.setItem(i_row, 1, item_user_id)  # 期货账号
            self.tableWidget_Trade_Args.setItem(i_row, 2, item_strategy_id)  # 策略编号
            self.tableWidget_Trade_Args.setItem(i_row, 3, item_instrument_id)  # 交易合约
            self.tableWidget_Trade_Args.setItem(i_row, 4, item_position)  # 总持仓
            self.tableWidget_Trade_Args.setItem(i_row, 5, item_position_buy)  # 买持仓
            self.tableWidget_Trade_Args.setItem(i_row, 6, item_position_sell)  # 卖持仓
            self.tableWidget_Trade_Args.setItem(i_row, 7, item_position_profit)  # 持仓盈亏
            self.tableWidget_Trade_Args.setItem(i_row, 8, item_close_profit)  # 平仓盈亏
            self.tableWidget_Trade_Args.setItem(i_row, 9, item_commission)  # 手续费
            self.tableWidget_Trade_Args.setItem(i_row, 10, item_profit)  # 净盈亏
            self.tableWidget_Trade_Args.setItem(i_row, 11, item_trade_count)  # 成交量
            self.tableWidget_Trade_Args.setItem(i_row, 12, item_amount)  # 成交金额
            self.tableWidget_Trade_Args.setItem(i_row, 13, item_a_trade_rate)  # A成交率
            self.tableWidget_Trade_Args.setItem(i_row, 14, item_b_trade_rate)  # B成交率
            self.tableWidget_Trade_Args.setItem(i_row, 15, item_trade_model)  # 交易模型
            self.tableWidget_Trade_Args.setItem(i_row, 16, item_order_algorithm)  # 下单算法
            self.tableWidget_Trade_Args.setCurrentCell(i_row, 0)  # 设置当前行为“当前行”

            self.set_on_tableWidget_Trade_Args_cellClicked(i_row, 0)  # 触发鼠标左击单击该策略行

            # 绑定信号槽：向界面插入策略的时候，绑定策略对象与窗口对象之间的信号槽关系
            # 信号槽连接：策略对象修改策略 -> 窗口对象更新策略显示（Strategy.signal_update_strategy -> QAccountWidget.slot_update_strategy()）
            if self.is_single_user_widget():
                if self.__widget_name == obj_strategy.get_user_id():
                    # print(">>> QAccountWidget.slot_insert_strategy() 向界面插入策略时绑定信号槽，widget_id=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id())
                    # 信号槽连接：策略对象的信号signal_update_spread_signal -> 所属的单账户窗口对象的槽函数slot_update_spread
                    obj_strategy.signal_update_spread_signal.connect(self.slot_update_spread)
                    # 信号槽连接：策略对象修改策略 -> 窗口对象更新策略显示（Strategy.signal_update_strategy -> QAccountWidget.slot_update_strategy()）
                    obj_strategy.signal_update_strategy.connect(self.slot_update_strategy)
                    # 信号槽连接：策略对象持仓发生变化 -> 界面刷新持仓显示（Strategy.signal_update_strategy_position -> QAccountWidget.slot_update_strategy_position）
                    obj_strategy.signal_update_strategy_position.connect(self.slot_update_strategy_position)
                    # 信号槽连接：策略对象修改持仓方法被调用 -> 窗口对象修改设置持仓按钮状态
                    obj_strategy.signal_pushButton_set_position_setEnabled.connect(self.slot_pushButton_set_position_setEnabled)
            # 策略与总账户窗口信号slot_update_spread连接
            else:
                # print(">>> QAccountWidget.slot_insert_strategy() 向界面插入策略时绑定信号槽，widget_id=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id())
                # 信号槽连接：策略对象的信号signal_update_spread_total -> 总账户窗口对象的槽函数slot_update_spread
                obj_strategy.signal_update_spread_total.connect(self.slot_update_spread)
                # 信号槽连接：策略对象修改策略 -> 窗口对象更新策略显示（Strategy.signal_update_strategy -> QAccountWidget.slot_update_strategy()）
                obj_strategy.signal_update_strategy.connect(self.slot_update_strategy)
                # 信号槽连接：策略对象持仓发生变化 -> 界面刷新持仓显示（Strategy.signal_update_strategy_position -> QAccountWidget.slot_update_strategy_position）
                obj_strategy.signal_update_strategy_position.connect(self.slot_update_strategy_position)
                # 信号槽连接：策略对象修改持仓方法被调用 -> 窗口对象修改设置持仓按钮状态
                obj_strategy.signal_pushButton_set_position_setEnabled.connect(self.slot_pushButton_set_position_setEnabled)
                # 界面初始化完成状态、即程序运行中添加策略成功，弹窗提醒
                if self.__ctp_manager.get_init_UI_finished():
                    QMessageBox().showMessage("通知", "新建策略成功，期货账号" + obj_strategy.get_user_id() + "策略编号" + obj_strategy.get_strategy_id())
    """

    # 向界面插入策略，形参是任何策略对象，所有策略数量有增加时调用该方法
    def slot_insert_strategy(self, dict_strategy_arguments):
        # 总账户窗口或策略所属的单账户窗口
        i_row = self.tableWidget_Trade_Args.rowCount()  # 将要出入到的行标
        self.tableWidget_Trade_Args.insertRow(i_row)  # 在tableWidget中插入行
        print(">>> QAccountWidget.slot_insert_strategy() user_id =", dict_strategy_arguments['user_id'], "strategy_id =", dict_strategy_arguments['strategy_id'], "i_row =", i_row, " dict_strategy_arguments =", dict_strategy_arguments)
        item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
        item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
        item_strategy_on_off.setText('关')
        item_user_id = QtGui.QTableWidgetItem(dict_strategy_arguments['user_id'])  # 期货账号
        item_strategy_id = QtGui.QTableWidgetItem(dict_strategy_arguments['strategy_id'])  # 策略编号
        a_instrument_id = dict_strategy_arguments['list_instrument_id'][0]
        b_instrument_id = dict_strategy_arguments['list_instrument_id'][1]
        str_instruments = ','.join([a_instrument_id, b_instrument_id])
        item_instrument_id = QtGui.QTableWidgetItem(str_instruments)  # 交易合约
        # item_position = QtGui.QTableWidgetItem(
        #     str(dict_strategy_position['position_a_buy'] + dict_strategy_position['position_a_sell']))  # 总持仓
        # item_position_buy = QtGui.QTableWidgetItem(str(dict_strategy_position['position_a_buy']))  # 买持仓
        # item_position_sell = QtGui.QTableWidgetItem(str(dict_strategy_position['position_a_sell']))  # 卖持仓
        # item_position_profit = QtGui.QTableWidgetItem(str(dict_strategy_statistics['position_profit']))  # 持仓盈亏
        # item_close_profit = QtGui.QTableWidgetItem(str(dict_strategy_statistics['close_profit']))  # 平仓盈亏
        # item_commission = QtGui.QTableWidgetItem(str(dict_strategy_statistics['commission']))  # 手续费
        # item_profit = QtGui.QTableWidgetItem(str(dict_strategy_statistics['profit']))  # 净盈亏
        # traded_count = str(dict_strategy_statistics['a_traded_count'] + dict_strategy_statistics['b_traded_count'])
        # item_trade_count = QtGui.QTableWidgetItem(traded_count)  # 成交量
        # traded_amount = str(dict_strategy_statistics['a_traded_mount'] + dict_strategy_statistics['b_traded_mount'])
        # item_amount = QtGui.QTableWidgetItem(traded_amount)  # 成交金额
        # item_a_trade_rate = QtGui.QTableWidgetItem(str(dict_strategy_statistics['a_trade_rate']))  # A成交率
        # item_b_trade_rate = QtGui.QTableWidgetItem(str(dict_strategy_statistics['b_trade_rate']))  # B成交率
        # item_trade_model = QtGui.QTableWidgetItem(dict_strategy_arguments['trade_model'])  # 交易模型
        # item_order_algorithm = QtGui.QTableWidgetItem(dict_strategy_arguments['order_algorithm'])  # 下单算法
        item_position = QtGui.QTableWidgetItem('0')  # 总持仓
        item_position_buy = QtGui.QTableWidgetItem('0')  # 买持仓
        item_position_sell = QtGui.QTableWidgetItem('0')  # 卖持仓
        item_position_profit = QtGui.QTableWidgetItem('0')  # 持仓盈亏
        item_close_profit = QtGui.QTableWidgetItem('0')  # 平仓盈亏
        item_commission = QtGui.QTableWidgetItem('0')  # 手续费
        item_profit = QtGui.QTableWidgetItem('0')  # 净盈亏
        item_trade_count = QtGui.QTableWidgetItem('0')  # 成交量
        item_amount = QtGui.QTableWidgetItem('0')  # 成交金额
        item_a_trade_rate = QtGui.QTableWidgetItem('0.0')  # A成交率
        item_b_trade_rate = QtGui.QTableWidgetItem('0.0')  # B成交率
        item_trade_model = QtGui.QTableWidgetItem('')  # 交易模型
        item_order_algorithm = QtGui.QTableWidgetItem('')  # 下单算法
        self.tableWidget_Trade_Args.setItem(i_row, 0, item_strategy_on_off)  # 开关
        self.tableWidget_Trade_Args.setItem(i_row, 1, item_user_id)  # 期货账号
        self.tableWidget_Trade_Args.setItem(i_row, 2, item_strategy_id)  # 策略编号
        self.tableWidget_Trade_Args.setItem(i_row, 3, item_instrument_id)  # 交易合约
        self.tableWidget_Trade_Args.setItem(i_row, 4, item_position)  # 总持仓
        self.tableWidget_Trade_Args.setItem(i_row, 5, item_position_buy)  # 买持仓
        self.tableWidget_Trade_Args.setItem(i_row, 6, item_position_sell)  # 卖持仓
        self.tableWidget_Trade_Args.setItem(i_row, 7, item_position_profit)  # 持仓盈亏
        self.tableWidget_Trade_Args.setItem(i_row, 8, item_close_profit)  # 平仓盈亏
        self.tableWidget_Trade_Args.setItem(i_row, 9, item_commission)  # 手续费
        self.tableWidget_Trade_Args.setItem(i_row, 10, item_profit)  # 净盈亏
        self.tableWidget_Trade_Args.setItem(i_row, 11, item_trade_count)  # 成交量
        self.tableWidget_Trade_Args.setItem(i_row, 12, item_amount)  # 成交金额
        self.tableWidget_Trade_Args.setItem(i_row, 13, item_a_trade_rate)  # A成交率
        self.tableWidget_Trade_Args.setItem(i_row, 14, item_b_trade_rate)  # B成交率
        self.tableWidget_Trade_Args.setItem(i_row, 15, item_trade_model)  # 交易模型
        self.tableWidget_Trade_Args.setItem(i_row, 16, item_order_algorithm)  # 下单算法

        # self.tableWidget_Trade_Args.setCurrentCell(i_row, 0)  # 设置当前行为“当前行”
        # self.set_on_tableWidget_Trade_Args_cellClicked(i_row, 0)  # 触发鼠标左击单击该策略行

    """
    # 从界面删除策略
    @QtCore.pyqtSlot(object)
    def slot_remove_strategy(self, obj_strategy):
        # 总账户窗口或策略所属的单账户窗口
        if self.is_single_user_widget() is False or obj_strategy.get_user_id() == self.__widget_name:
            for i_row in range(self.tableWidget_Trade_Args.rowCount()):
                # 在table中找到对应的策略行，更新界面显示，跳出for
                if self.tableWidget_Trade_Args.item(i_row, 2).text() == obj_strategy.get_user_id() and self.tableWidget_Trade_Args.item(i_row, 3).text() == obj_strategy.get_strategy_id():
                    # print(">>> QAccountWidget.remove_strategy() 删除策略，widget_name=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id())
                    self.tableWidget_Trade_Args.removeRow(i_row)
                    if self.is_single_user_widget():
                        QMessageBox().showMessage("通知", "删除策略成功，期货账号"+obj_strategy.get_user_id()+"策略编号"+obj_strategy.get_strategy_id())
                    break
            # 如果tableWidget_Trade_Args中不存在策略，将groupBox中内容清空
            if self.tableWidget_Trade_Args.rowCount() == 0:
                # print(">>> QAccountWidget.slot_remove_strategy() widget_name=", self.__widget_name, "窗口中没有策略，清空groupBox")
                # 期货账号
                self.lineEdit_qihuozhanghao.setText('')
                # 策略编号
                self.lineEdit_celuebianhao.setText('')
                # 交易模型
                index_comboBox = self.comboBox_jiaoyimoxing.findText('')
                if index_comboBox != -1:
                    self.comboBox_jiaoyimoxing.setCurrentIndex(index_comboBox)
                # 下单算法
                index_comboBox = self.comboBox_xiadansuanfa.findText('')
                if index_comboBox != -1:
                    self.comboBox_xiadansuanfa.setCurrentIndex(index_comboBox)
                # 总手
                self.lineEdit_zongshou.setText('')
                # 每份
                self.lineEdit_meifen.setText('')
                # 止损
                self.spinBox_zhisun.setValue(0)
                # 超价触发
                self.spinBox_rangjia.setValue(0)
                # A等待
                self.spinBox_Adengdai.setValue(0)
                # B等待
                self.spinBox_Bdengdai.setValue(0)
                # 市场空头价差
                self.lineEdit_kongtoujiacha.setText('')
                # 持仓多头价差
                self.lineEdit_duotoujiacha.setText('')
                # A限制
                self.lineEdit_Achedanxianzhi.setText('')
                # B限制
                self.lineEdit_Bchedanxianzhi.setText('')
                # A撤单
                self.lineEdit_Achedan.setText('')
                # B撤单
                self.lineEdit_Bchedan.setText('')
                # 空头开
                self.doubleSpinBox_kongtoukai.setValue(0)
                self.doubleSpinBox_kongtoukai.setSingleStep(0)
                # 空头平
                self.doubleSpinBox_kongtouping.setValue(0)
                self.doubleSpinBox_kongtouping.setSingleStep(1)
                # 多头开
                self.doubleSpinBox_duotoukai.setValue(0)
                self.doubleSpinBox_duotoukai.setSingleStep(1)
                # 多头平
                self.doubleSpinBox_duotouping.setValue(0)
                self.doubleSpinBox_duotouping.setSingleStep(1)
                # 空头开-开关
                self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
                # 空头平-开关
                self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
                # 多头开-开关
                self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
                # 多头平-开关
                self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
                # A总卖
                self.lineEdit_Azongsell.setText('')
                # A昨卖
                self.lineEdit_Azuosell.setText('')
                # B总买
                self.lineEdit_Bzongbuy.setText('')
                # B昨买
                self.lineEdit_Bzuobuy.setText('')
                # A总买
                self.lineEdit_Azongbuy.setText('')
                # A昨买
                self.lineEdit_Azuobuy.setText('')
                # B总卖
                self.lineEdit_Bzongsell.setText('')
                # B昨卖
                self.lineEdit_Bzuosell.setText('')
                # 禁用groupBox中的按钮
                self.pushButton_set_strategy.setEnabled(False)
                self.pushButton_query_strategy.setEnabled(False)
                self.pushButton_set_position.setEnabled(False)
            # 如果tableWidget_Trade_Args中还存在策略，将主动触发clicked_table_widget事件，以更新groupBox显示
            elif self.tableWidget_Trade_Args.rowCount() > 0:
                self.set_on_tableWidget_Trade_Args_cellClicked(0, 0)
    """

    # 从界面删除策略
    @QtCore.pyqtSlot(object)
    def slot_remove_strategy(self, obj_strategy):
        # 总账户窗口或策略所属的单账户窗口
        if self.is_single_user_widget() is False or obj_strategy.get_user_id() == self.__widget_name:
            for i_row in range(self.tableWidget_Trade_Args.rowCount()):
                # 在table中找到对应的策略行，更新界面显示，跳出for
                if self.tableWidget_Trade_Args.item(i_row,
                                                    2).text() == obj_strategy.get_user_id() and self.tableWidget_Trade_Args.item(
                        i_row, 3).text() == obj_strategy.get_strategy_id():
                    # print(">>> QAccountWidget.remove_strategy() 删除策略，widget_name=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id())
                    self.tableWidget_Trade_Args.removeRow(i_row)
                    if self.is_single_user_widget():
                        # MessageBox().showMessage("通知", "删除策略成功，期货账号" + obj_strategy.get_user_id() + "策略编号" + obj_strategy.get_strategy_id())
                        str_main = "删除策略成功，期货账号" + obj_strategy.get_user_id() + "策略编号" + obj_strategy.get_strategy_id()
                        dict_args = {"title": "消息", "main": str_main}
                        self.signal_show_alert.emit(dict_args)

                    break
            # 如果tableWidget_Trade_Args中不存在策略，将groupBox中内容清空
            if self.tableWidget_Trade_Args.rowCount() == 0:
                # print(">>> QAccountWidget.slot_remove_strategy() widget_name=", self.__widget_name, "窗口中没有策略，清空groupBox")
                # 期货账号
                self.lineEdit_qihuozhanghao.setText('')
                # 策略编号
                self.lineEdit_celuebianhao.setText('')
                # 交易模型
                index_comboBox = self.comboBox_jiaoyimoxing.findText('')
                if index_comboBox != -1:
                    self.comboBox_jiaoyimoxing.setCurrentIndex(index_comboBox)
                # 下单算法
                index_comboBox = self.comboBox_xiadansuanfa.findText('')
                if index_comboBox != -1:
                    self.comboBox_xiadansuanfa.setCurrentIndex(index_comboBox)
                # A合约
                self.lineEdit_Aheyue.setText('')
                # B合约
                self.lineEdit_Bheyue.setText('')
                # A合约乘数
                self.lineEdit_Achengshu.setText('')
                # B合约乘数
                self.lineEdit_Bchengshu.setText('')
                # 总手
                self.lineEdit_zongshou.setText('')
                # 每份
                self.lineEdit_meifen.setText('')
                # 止损
                self.spinBox_zhisun.setValue(0)
                # 超价触发
                self.spinBox_rangjia.setValue(0)
                # A等待
                self.spinBox_Adengdai.setValue(0)
                # B等待
                self.spinBox_Bdengdai.setValue(0)
                # 市场空头价差
                self.lineEdit_kongtoujiacha.setText('')
                # 持仓多头价差
                self.lineEdit_duotoujiacha.setText('')
                # A限制
                self.lineEdit_Achedanxianzhi.setText('')
                # B限制
                self.lineEdit_Bchedanxianzhi.setText('')
                # A撤单
                self.lineEdit_Achedan.setText('')
                # B撤单
                self.lineEdit_Bchedan.setText('')
                # 空头开
                self.doubleSpinBox_kongtoukai.setValue(0)
                self.doubleSpinBox_kongtoukai.setSingleStep(0)
                # 空头平
                self.doubleSpinBox_kongtouping.setValue(0)
                self.doubleSpinBox_kongtouping.setSingleStep(1)
                # 多头开
                self.doubleSpinBox_duotoukai.setValue(0)
                self.doubleSpinBox_duotoukai.setSingleStep(1)
                # 多头平
                self.doubleSpinBox_duotouping.setValue(0)
                self.doubleSpinBox_duotouping.setSingleStep(1)
                # 空头开-开关
                self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
                # 空头平-开关
                self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
                # 多头开-开关
                self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
                # 多头平-开关
                self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
                # A总卖
                self.lineEdit_Azongsell.setText('')
                # A昨卖
                self.lineEdit_Azuosell.setText('')
                # B总买
                self.lineEdit_Bzongbuy.setText('')
                # B昨买
                self.lineEdit_Bzuobuy.setText('')
                # A总买
                self.lineEdit_Azongbuy.setText('')
                # A昨买
                self.lineEdit_Azuobuy.setText('')
                # B总卖
                self.lineEdit_Bzongsell.setText('')
                # B昨卖
                self.lineEdit_Bzuosell.setText('')
                # 禁用groupBox中的按钮
                self.pushButton_set_strategy.setEnabled(False)
                self.pushButton_query_strategy.setEnabled(False)
                self.pushButton_set_position.setEnabled(False)
            # 如果tableWidget_Trade_Args中还存在策略，将主动触发clicked_table_widget事件，以更新groupBox显示
            elif self.tableWidget_Trade_Args.rowCount() > 0:
                self.set_on_tableWidget_Trade_Args_cellClicked(0, 0)

    # 界面增加一行，内容空白
    def slot_insert_row(self):
        i_row = self.tableWidget_Trade_Args.rowCount()
        self.tableWidget_Trade_Args.insertRow(i_row)
        item_strategy_on_off = QtGui.QTableWidgetItem()  # 开关
        item_strategy_on_off.setCheckState(QtCore.Qt.Unchecked)
        item_strategy_on_off.setText('关')
        item_user_id = QtGui.QTableWidgetItem('')  # 期货账号
        item_strategy_id = QtGui.QTableWidgetItem('')  # 策略编号
        item_instrument_id = QtGui.QTableWidgetItem('')  # 交易合约
        item_position = QtGui.QTableWidgetItem('0')  # 总持仓
        item_position_buy = QtGui.QTableWidgetItem('0')  # 买持仓
        item_position_sell = QtGui.QTableWidgetItem('0')  # 卖持仓
        item_position_profit = QtGui.QTableWidgetItem('0')  # 持仓盈亏
        item_close_profit = QtGui.QTableWidgetItem('0')  # 平仓盈亏
        item_commission = QtGui.QTableWidgetItem('0')  # 手续费
        item_profit = QtGui.QTableWidgetItem('0')  # 净盈亏
        item_trade_count = QtGui.QTableWidgetItem('0')  # 成交量
        item_amount = QtGui.QTableWidgetItem('0')  # 成交金额
        item_a_trade_rate = QtGui.QTableWidgetItem('0.0')  # A成交率
        item_b_trade_rate = QtGui.QTableWidgetItem('0.0')  # B成交率
        item_trade_model = QtGui.QTableWidgetItem('')  # 交易模型
        item_order_algorithm = QtGui.QTableWidgetItem('')  # 下单算法
        self.tableWidget_Trade_Args.setItem(i_row, 0, item_strategy_on_off)  # 开关
        self.tableWidget_Trade_Args.setItem(i_row, 1, item_user_id)  # 期货账号
        self.tableWidget_Trade_Args.setItem(i_row, 2, item_strategy_id)  # 策略编号
        self.tableWidget_Trade_Args.setItem(i_row, 3, item_instrument_id)  # 交易合约
        self.tableWidget_Trade_Args.setItem(i_row, 4, item_position)  # 总持仓
        self.tableWidget_Trade_Args.setItem(i_row, 5, item_position_buy)  # 买持仓
        self.tableWidget_Trade_Args.setItem(i_row, 6, item_position_sell)  # 卖持仓
        self.tableWidget_Trade_Args.setItem(i_row, 7, item_position_profit)  # 持仓盈亏
        self.tableWidget_Trade_Args.setItem(i_row, 8, item_close_profit)  # 平仓盈亏
        self.tableWidget_Trade_Args.setItem(i_row, 9, item_commission)  # 手续费
        self.tableWidget_Trade_Args.setItem(i_row, 10, item_profit)  # 净盈亏
        self.tableWidget_Trade_Args.setItem(i_row, 11, item_trade_count)  # 成交量
        self.tableWidget_Trade_Args.setItem(i_row, 12, item_amount)  # 成交金额
        self.tableWidget_Trade_Args.setItem(i_row, 13, item_a_trade_rate)  # A成交率
        self.tableWidget_Trade_Args.setItem(i_row, 14, item_b_trade_rate)  # B成交率
        self.tableWidget_Trade_Args.setItem(i_row, 15, item_trade_model)  # 交易模型
        self.tableWidget_Trade_Args.setItem(i_row, 16, item_order_algorithm)  # 下单算法

    # 界面删除一行
    def slot_delete_row(self, row=-1):
        # 传入形参则删除指定行
        if row > -1:
            self.tableWidget_Trade_Args.removeRow(row)
        # 未传入形参则删除最后一行
        else:
            row_count = self.tableWidget_Trade_Args.rowCount()
            self.tableWidget_Trade_Args.removeRow(row_count)

    # 获取要更新tableWidget的数据
    def get_update_tableWidget_data(self):
        # 获取要更新的数据
        dict_user_process_data = self.__socket_manager.get_dict_user_process_data()
        list_update_data = list()  # list_update_data是要更新到界面的数据
        for user_id in dict_user_process_data:
            if self.__current_tab_name == "所有账户" or self.__current_tab_name == user_id:
                dict_strategy_arguments = dict_user_process_data[user_id]['running']['strategy_arguments']
                dict_strategy_position = dict_user_process_data[user_id]['running']['strategy_position']
                dict_strategy_statistics = dict_user_process_data[user_id]['running']['strategy_statistics']

                for strategy_id in dict_strategy_arguments:
                    dict_update_data_one_strategy = dict()
                    dict_update_data_one_strategy['strategy_on_off'] = dict_strategy_arguments[strategy_id]['on_off']
                    dict_update_data_one_strategy['user_id'] = dict_strategy_arguments[strategy_id]['user_id']
                    dict_update_data_one_strategy['strategy_id'] = dict_strategy_arguments[strategy_id]['strategy_id']
                    dict_update_data_one_strategy['trade_instrument'] = ','.join(
                        [dict_strategy_arguments[strategy_id]['a_instrument_id'],
                         dict_strategy_arguments[strategy_id]['b_instrument_id']])
                    dict_update_data_one_strategy['trade_model'] = dict_strategy_arguments[strategy_id]['trade_model']
                    dict_update_data_one_strategy['order_algorithm'] = dict_strategy_arguments[strategy_id][
                        'order_algorithm']
                    for i_strategy_id in dict_strategy_position:
                        if strategy_id == i_strategy_id:
                            dict_update_data_one_strategy['position'] = dict_strategy_position[strategy_id][
                                                                            'position_a_buy'] + \
                                                                        dict_strategy_position[strategy_id][
                                                                            'position_a_sell']
                            dict_update_data_one_strategy['position_buy'] = dict_strategy_position[strategy_id][
                                'position_a_buy']
                            dict_update_data_one_strategy['position_sell'] = dict_strategy_position[strategy_id][
                                'position_a_sell']
                            break
                    for i_strategy_id in dict_strategy_statistics:
                        if strategy_id == i_strategy_id:
                            dict_update_data_one_strategy[
                                'profit_position'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['profit_position']
                            dict_update_data_one_strategy[
                                'profit_close'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['profit_close']
                            dict_update_data_one_strategy[
                                'profit'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['profit_close']
                            dict_update_data_one_strategy[
                                'commission'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['commission']
                            dict_update_data_one_strategy[
                                'total_traded_count'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['total_traded_count']
                            dict_update_data_one_strategy[
                                'total_traded_amount'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['total_traded_amount']
                            dict_update_data_one_strategy['a_trade_rate'] = dict_strategy_statistics[strategy_id][
                                'a_trade_rate']
                            dict_update_data_one_strategy['b_trade_rate'] = dict_strategy_statistics[strategy_id][
                                'b_trade_rate']
                            break
                    list_update_data.append(dict_update_data_one_strategy)
        return list_update_data

    # 更新tableWidget_Trade_Args
    def update_tableWidget_Trade_Args(self):
        row_count = self.tableWidget_Trade_Args.rowCount()  # 将要出入到的行标
        if row_count == 0:
            return
        # 获取要更新的数据
        dict_user_process_data = self.__socket_manager.get_dict_user_process_data()
        # list_update_data = list()  # list_update_data是要更新到界面的数据
        # for user_id in dict_user_process_data:
        #     if self.__current_tab_name == "所有账户" or self.__current_tab_name == user_id:
        #         dict_strategy_arguments = dict_user_process_data[user_id]['running']['strategy_arguments']
        #         dict_strategy_position = dict_user_process_data[user_id]['running']['strategy_position']
        #         dict_strategy_statistics = dict_user_process_data[user_id]['running']['strategy_statistics']
        #         # print(">>> ::QAccountWidget.update_tableWidget_Trade_Args() dict_strategy_arguments =", dict_strategy_arguments)
        #         for strategy_id in dict_strategy_arguments:
        #             dict_update_data_one_strategy = dict()
        #             # try:
        #             #     print(">>> QAccountWidget.update_tableWidget_Trade_Args() dict_strategy_arguments[strategy_id] =", dict_strategy_arguments[strategy_id])
        #             # except:
        #             #     print(">>> except:QAccountWidget.update_tableWidget_Trade_Args() dict_strategy_arguments =", dict_strategy_arguments)
        #             #     print(">>> except:QAccountWidget.update_tableWidget_Trade_Args() strategy_id =", strategy_id)
        #             dict_update_data_one_strategy['strategy_on_off'] = dict_strategy_arguments[strategy_id]['on_off']
        #             dict_update_data_one_strategy['user_id'] = dict_strategy_arguments[strategy_id]['user_id']
        #             dict_update_data_one_strategy['strategy_id'] = dict_strategy_arguments[strategy_id]['strategy_id']
        #             dict_update_data_one_strategy['trade_instrument'] = ','.join([dict_strategy_arguments[strategy_id]['a_instrument_id'],dict_strategy_arguments[strategy_id]['b_instrument_id']])
        #             dict_update_data_one_strategy['trade_model'] = dict_strategy_arguments[strategy_id]['trade_model']
        #             dict_update_data_one_strategy['order_algorithm'] = dict_strategy_arguments[strategy_id]['order_algorithm']
        #             for i_strategy_id in dict_strategy_position:
        #                 if strategy_id == i_strategy_id:
        #                     dict_update_data_one_strategy['position'] = dict_strategy_position[strategy_id]['position_a_buy'] + dict_strategy_position[strategy_id]['position_a_sell']
        #                     dict_update_data_one_strategy['position_buy'] = dict_strategy_position[strategy_id]['position_a_buy']
        #                     dict_update_data_one_strategy['position_sell'] = dict_strategy_position[strategy_id]['position_a_sell']
        #                     break
        #             for i_strategy_id in dict_strategy_statistics:
        #                 if strategy_id == i_strategy_id:
        #                     dict_update_data_one_strategy['profit_position'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['profit_position']
        #                     dict_update_data_one_strategy['profit_close'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['profit_close']
        #                     dict_update_data_one_strategy['profit'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['profit_close']
        #                     dict_update_data_one_strategy['commission'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['commission']
        #                     dict_update_data_one_strategy['total_traded_count'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['total_traded_count']
        #                     dict_update_data_one_strategy['total_traded_amount'] = '待'  # 待续，需改为dict_strategy_statistics[strategy_id]['total_traded_amount']
        #                     dict_update_data_one_strategy['a_trade_rate'] = dict_strategy_statistics[strategy_id]['a_trade_rate']
        #                     dict_update_data_one_strategy['b_trade_rate'] = dict_strategy_statistics[strategy_id]['b_trade_rate']
        #                     break
        #             list_update_data.append(dict_update_data_one_strategy)
        # # 将list_update_data更新到界面，数据样本如下：
        # # 遍历需要更新到界面的数据
        # # print(">>> QAccountWidget.update_tableWidget_Trade_Args() 界面更新数据list_update_data =", list_update_data)
        # print(">>> QAccountWidget.slot_remove_strategy() list_update_data =", list_update_data)
        list_update_data = [{'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'ru1705,ru1709', 'strategy_id': '03', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'cu1705,cu1707', 'strategy_id': '07', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'rb1705,rb1710', 'strategy_id': '01', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'zn1705,zn1710', 'strategy_id': '09', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'rb1705,rb1710', 'strategy_id': '05', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'rb1705,rb1712', 'strategy_id': '06', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'zn1705,zn1707', 'strategy_id': '08', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'ru1705,ru1704', 'strategy_id': '04', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'rb1710,rb1705', 'strategy_id': '02', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 1, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '058176', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'rb1705,rb1706', 'strategy_id': '03', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '063802', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'zn1705,zn1707', 'strategy_id': '01', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '063802', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'rb1705,rb1707', 'strategy_id': '04', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '063802', 'position_sell': 0},
         {'total_traded_amount': '待', 'profit_close': '待', 'commission': '待', 'profit': '待',
          'trade_instrument': 'cu1705,cu1706', 'strategy_id': '02', 'order_algorithm': '', 'profit_position': '待',
          'strategy_on_off': 0, 'trade_model': '', 'a_trade_rate': 0, 'total_traded_count': '待', 'b_trade_rate': 0,
          'position_buy': 0, 'position': 0, 'user_id': '063802', 'position_sell': 0}]

        for i in range(len(list_update_data)):
            dict_strategy_data = list_update_data[i]
            self.update_tableWidget_Trade_Args_one_part(i, dict_strategy_data)  # 更新策略列表中的单行，形参：行标、数据

        # 清空多余的行
        if row_count > len(list_update_data):
            for i in range(len(list_update_data), row_count, 1):
                self.clean_tableWidget_Trade_Args_one(i)

    # 更新策略列表中的单行，形参：行标、数据
    def update_tableWidget_Trade_Args_one_part(self, row, data):
        # 开关
        # print(">>> QAccountWidget.update_tableWidget_Trade_Args_one_part() user_id=", data['user_id'], "strategy_id=", data['strategy_id'], "data =", data)
        # item_on_off = self.tableWidget_Trade_Args.item(row, 0)
        # if data['strategy_on_off'] == 0:
        #     item_on_off.setText("关")
        #     item_on_off.setCheckState(QtCore.Qt.Unchecked)
        # elif data['strategy_on_off'] == 1:
        #     item_on_off.setText("开")
        #     item_on_off.setCheckState(QtCore.Qt.Checked)
        # else:
        #     print(">>> QAccountWidget.update_tableWidget_Trade_Args_one_part() user_id=", data['user_id'], "strategy_id=",
        #           data['strategy_id'], "策略参数strategy_on_off值异常", data['strategy_on_off'])
        # if self.__item_on_off_status is not None:
        #     if self.__item_on_off_status['enable'] == 0:
        #         item_on_off.setFlags(item_on_off.flags() ^ (QtCore.Qt.ItemIsEnabled))  # 激活item
        #         self.__item_on_off_status['enable'] = 1  # 0禁用、1激活
        # 期货账号
        self.tableWidget_Trade_Args.item(row, 1).setText(data['user_id'])
        # 策略编号
        self.tableWidget_Trade_Args.item(row, 2).setText(data['strategy_id'])
        # 交易合约
        # trade_instrument = ','.join([data['a_instrument_id'], data['a_instrument_id']])
        self.tableWidget_Trade_Args.item(row, 3).setText(data['trade_instrument'])
        # 总持仓
        self.tableWidget_Trade_Args.item(row, 4).setText(str(data['position']))
        # 买持仓
        self.tableWidget_Trade_Args.item(row, 5).setText(str(data['position_buy']))
        # 卖持仓
        self.tableWidget_Trade_Args.item(row, 6).setText(str(data['position_sell']))
        # 持仓盈亏
        self.tableWidget_Trade_Args.item(row, 7).setText(str(data['profit_position']))
        # 平仓盈亏
        self.tableWidget_Trade_Args.item(row, 8).setText(str(data['profit_close']))
        # 手续费
        self.tableWidget_Trade_Args.item(row, 9).setText(str(data['commission']))
        # 净盈亏
        self.tableWidget_Trade_Args.item(row, 10).setText(str(data['profit']))
        # 成交量
        self.tableWidget_Trade_Args.item(row, 11).setText(str(data['total_traded_count']))
        # 成交金额
        self.tableWidget_Trade_Args.item(row, 12).setText(str(data['total_traded_amount']))
        # A成交率
        self.tableWidget_Trade_Args.item(row, 13).setText(str(data['a_trade_rate']))
        # B成交率
        self.tableWidget_Trade_Args.item(row, 14).setText(str(data['b_trade_rate']))
        # 交易模型
        self.tableWidget_Trade_Args.item(row, 15).setText(str(data['trade_model']))
        # 下单算法
        self.tableWidget_Trade_Args.item(row, 16).setText(str(data['order_algorithm']))

    # 清空策略列表中的单行数据
    def clean_tableWidget_Trade_Args_one(self, row):
        # 开关
        self.tableWidget_Trade_Args.setItem(row, 0, QtGui.QTableWidgetItem())  # 开关
        # 期货账号
        self.tableWidget_Trade_Args.item(row, 1).setText('')
        # 策略编号
        self.tableWidget_Trade_Args.item(row, 2).setText('')
        # 交易合约
        self.tableWidget_Trade_Args.item(row, 3).setText('')
        # 总持仓
        self.tableWidget_Trade_Args.item(row, 4).setText('')
        # 买持仓
        self.tableWidget_Trade_Args.item(row, 5).setText('')
        # 卖持仓
        self.tableWidget_Trade_Args.item(row, 6).setText('')
        # 持仓盈亏
        self.tableWidget_Trade_Args.item(row, 7).setText('')
        # 平仓盈亏
        self.tableWidget_Trade_Args.item(row, 8).setText('')
        # 手续费
        self.tableWidget_Trade_Args.item(row, 9).setText('')
        # 净盈亏
        self.tableWidget_Trade_Args.item(row, 10).setText('')
        # 成交量
        self.tableWidget_Trade_Args.item(row, 11).setText('')
        # 成交金额
        self.tableWidget_Trade_Args.item(row, 12).setText('')
        # A成交率
        self.tableWidget_Trade_Args.item(row, 13).setText('')
        # B成交率
        self.tableWidget_Trade_Args.item(row, 14).setText('')
        # 交易模型
        self.tableWidget_Trade_Args.item(row, 15).setText('')
        # 下单算法
        self.tableWidget_Trade_Args.item(row, 16).setText('')

    # 清空groupBox
    def clean_groupBox(self):
        print(">>> QAccountWidget.clean_groupBox() called")
        self.lineEdit_qihuozhanghao.setText('')  # 期货账号
        self.lineEdit_celuebianhao.setText('')  # 策略编号
        self.comboBox_jiaoyimoxing.setCurrentIndex(-1)
        self.comboBox_xiadansuanfa.setCurrentIndex(-1)
        self.lineEdit_Aheyue.setText('')  # A合约
        self.lineEdit_Bheyue.setText('')  # B合约
        self.lineEdit_Achengshu.setText('')  # A合约乘数
        self.lineEdit_Bchengshu.setText('')  # B合约乘数
        self.lineEdit_duotoujiacha.setText('')  # 多头价差
        self.lineEdit_kongtoujiacha.setText('')  # 空头价差
        self.lineEdit_zongshou.setText('')  # 总手
        self.lineEdit_meifen.setText('')  # 每份
        self.spinBox_zhisun.setValue(0)  # 止损
        self.spinBox_rangjia.setValue(0)  # 超价触发
        self.spinBox_Abaodanpianyi.setValue(0)  # A报价偏移
        self.spinBox_Bbaodanpianyi.setValue(0)  # B报价偏移
        self.spinBox_Adengdai.setValue(0)  # A撤单等待
        self.spinBox_Bdengdai.setValue(0)  # B撤单等待
        self.lineEdit_Achedanxianzhi.setText('')  # A撤单限制
        self.lineEdit_Bchedanxianzhi.setText('')  # B撤单限制
        self.lineEdit_Achedan.setText('')  # A撤单
        self.lineEdit_Bchedan.setText('')  # B撤单
        self.doubleSpinBox_kongtoukai.setValue(0)  # 空头开
        # self.doubleSpinBox_kongtoukai.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        self.doubleSpinBox_kongtouping.setValue(0)  # 空头平
        # self.doubleSpinBox_kongtouping.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        self.doubleSpinBox_duotoukai.setValue(0)  # 多头开
        # self.doubleSpinBox_duotoukai.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        self.doubleSpinBox_duotouping.setValue(0)  # 多头平
        # self.doubleSpinBox_duotouping.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        # 空头开-开关
        self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
        # 空头平-开关
        self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
        # 多头开-开关
        self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
        # 多头平-开关
        self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
        self.lineEdit_Azongsell.setText('')  # A总卖
        self.lineEdit_Azuosell.setText('')  # A昨卖
        self.lineEdit_Bzongbuy.setText('')  # B总买
        self.lineEdit_Bzuobuy.setText('')  # B昨买
        self.lineEdit_Azongbuy.setText('')  # A总买
        self.lineEdit_Azuobuy.setText('')  # A昨买
        self.lineEdit_Bzongsell.setText('')  # B总卖
        self.lineEdit_Bzuosell.setText('')  # B昨卖

    """
    # 更新单个策略的界面显示，调用情景：鼠标点击tableWidget、发送参数、发送持仓、查询、插入策略
    @QtCore.pyqtSlot(object)
    def slot_update_strategy(self, obj_strategy):
        if self.tableWidget_Trade_Args.rowCount() == 0:
            return
        dict_strategy_args = obj_strategy.get_arguments()  # 策略参数
        dict_strategy_position = obj_strategy.get_position()  # 策略持仓
        dict_strategy_statistics = obj_strategy.get_dict_statistics()  # 交易统计数据
        print(">>> QAccountWidget.slot_update_strategy() "
              "widget_name=", self.__widget_name,
              "user_id=", obj_strategy.get_user_id(),
              "strategy_id=", obj_strategy.get_strategy_id(),
              "self.sender()=", self.sender(),
              "dict_strategy_args=", dict_strategy_args)
        # 更新tableWidget
        for i_row in range(self.tableWidget_Trade_Args.rowCount()):
            # 在table中找到对应的策略行，更新界面显示，跳出for
            if self.tableWidget_Trade_Args.item(i_row, 2).text() == obj_strategy.get_user_id() and self.tableWidget_Trade_Args.item(i_row, 3).text() == obj_strategy.get_strategy_id():
                # print(">>> QAccountWidget.slot_update_strategy() 更新tableWidget，widget_name=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id())
                # 开关
                item_on_off = self.tableWidget_Trade_Args.item(i_row, 0)
                if dict_strategy_args['strategy_on_off'] == 0:
                    # print(">>> QAccountWidget.slot_update_strategy() 更新tableWidget，widget_name=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id(), "策略开关设置：关")
                    item_on_off.setText("关")
                    item_on_off.setCheckState(QtCore.Qt.Unchecked)
                elif dict_strategy_args['strategy_on_off'] == 1:
                    # print(">>> QAccountWidget.slot_update_strategy() 更新tableWidget，widget_name=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id(), "策略开关设置：开")
                    item_on_off.setText("开")
                    item_on_off.setCheckState(QtCore.Qt.Checked)
                else:
                    print("QAccountWidget.slot_update_strategy() user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id(), "策略参数strategy_on_off值异常", dict_strategy_args['strategy_on_off'])
                if self.__item_on_off_status is not None:
                    if self.__item_on_off_status['enable'] == 0:
                        item_on_off.setFlags(item_on_off.flags() ^ (QtCore.Qt.ItemIsEnabled))  # 激活item
                        self.__item_on_off_status['enable'] = 1  # 0禁用、1激活
                # 只平
                # item_only_close = self.tableWidget_Trade_Args.item(i_row, 1)
                # if dict_strategy_args['only_close'] == 0:
                #     item_only_close.setText("关")
                #     item_only_close.setCheckState(QtCore.Qt.Unchecked)
                # elif dict_strategy_args['only_close'] == 1:
                #     item_only_close.setText("开")
                #     item_only_close.setCheckState(QtCore.Qt.Checked)
                # else:
                #     print("QAccountWidget.slot_update_strategy() user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id(), "策略参数only_close值异常", dict_strategy_args['only_close'])
                # if self.__item_only_close_status is not None:
                #     if self.__item_only_close_status['enable'] == 0:
                #         item_only_close.setFlags(item_only_close.flags() ^ (QtCore.Qt.ItemIsEnabled))  # 激活item
                #         self.__item_only_close_status['enable'] = 1  # 0禁用、1激活
                # 总持仓
                item_position = self.tableWidget_Trade_Args.item(i_row, 5)
                item_position.setText(
                    str(dict_strategy_position['position_a_buy'] + dict_strategy_position['position_a_sell']))
                # 买持仓
                item_position_buy = self.tableWidget_Trade_Args.item(i_row, 6)
                item_position_buy.setText(
                    str(dict_strategy_position['position_a_buy']))
                # 卖持仓
                item_position_sell = self.tableWidget_Trade_Args.item(i_row, 7)
                item_position_sell.setText(
                    str(dict_strategy_position['position_a_sell']))
                # 持仓盈亏，策略有持仓的时候由行情驱动更新，可以设计为定时任务，待续，2017年2月17日15:29:48
                item_profit_position = self.tableWidget_Trade_Args.item(i_row, 8)
                item_profit_position.setText('-')
                # 平仓盈亏
                item_profit_close = self.tableWidget_Trade_Args.item(i_row, 9)
                item_profit_close.setText(
                    str(int(dict_strategy_statistics['profit_close'])))
                # 手续费
                item_commission = self.tableWidget_Trade_Args.item(i_row, 10)
                item_commission.setText(
                    str(int(dict_strategy_statistics['commission'])))
                # 净盈亏
                item_profit = self.tableWidget_Trade_Args.item(i_row, 11)
                item_profit.setText(
                    str(int(dict_strategy_statistics['profit'])))
                # 成交量
                item_volume = self.tableWidget_Trade_Args.item(i_row, 12)
                item_volume.setText(
                    str(dict_strategy_statistics['volume']))
                # 成交金额
                item_amount = self.tableWidget_Trade_Args.item(i_row, 13)
                item_amount.setText(
                    str(int(dict_strategy_statistics['amount'])))
                # A成交率
                item_A_traded_rate = self.tableWidget_Trade_Args.item(i_row, 14)
                item_A_traded_rate.setText(
                    str(dict_strategy_statistics['A_traded_rate']))
                # B成交率
                item_B_traded_rate = self.tableWidget_Trade_Args.item(i_row, 15)
                item_B_traded_rate.setText(
                    str(dict_strategy_statistics['B_traded_rate']))
                # 交易模型
                item_trade_model = self.tableWidget_Trade_Args.item(i_row, 16)
                item_trade_model.setText(dict_strategy_args['trade_model'])
                # 下单算法
                item_order_algorithm = self.tableWidget_Trade_Args.item(i_row, 17)
                item_order_algorithm.setText(dict_strategy_args['order_algorithm'])

                break  # 在tableWidget中找到对应的策略行，结束for循环
        # 更新groupBox
        if self.__clicked_strategy == obj_strategy:  # 只更新在当前窗口中被鼠标选中的策略
            # print(">>> QAccountWidget.slot_update_strategy() 更新groupBox，widget_name=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id())
            # 期货账号
            self.lineEdit_qihuozhanghao.setText(dict_strategy_args['user_id'])
            # 策略编号
            self.lineEdit_celuebianhao.setText(dict_strategy_args['strategy_id'])
            # 交易模型
            index_comboBox = self.comboBox_jiaoyimoxing.findText(dict_strategy_args['trade_model'])
            if index_comboBox != -1:
                self.comboBox_jiaoyimoxing.setCurrentIndex(index_comboBox)
            # 下单算法
            index_comboBox = self.comboBox_xiadansuanfa.findText(dict_strategy_args['order_algorithm'])
            if index_comboBox != -1:
                self.comboBox_xiadansuanfa.setCurrentIndex(index_comboBox)
            # 总手
            self.lineEdit_zongshou.setText(str(dict_strategy_args['lots']))
            # 每份
            self.lineEdit_meifen.setText(str(dict_strategy_args['lots_batch']))
            # 止损
            self.spinBox_zhisun.setValue(dict_strategy_args['stop_loss'])
            # 超价触发
            self.spinBox_rangjia.setValue(dict_strategy_args['spread_shift'])
            # A报价偏移
            self.spinBox_Abaodanpianyi.setValue(dict_strategy_args['a_limit_price_shift'])
            # B报价偏移
            self.spinBox_Bbaodanpianyi.setValue(dict_strategy_args['b_limit_price_shift'])
            # A撤单等待
            self.spinBox_Adengdai.setValue(dict_strategy_args['a_wait_price_tick'])
            # B撤单等待
            self.spinBox_Bdengdai.setValue(dict_strategy_args['b_wait_price_tick'])
            # A限制
            self.lineEdit_Achedanxianzhi.setText(str(dict_strategy_args['a_order_action_limit']))
            # B限制
            self.lineEdit_Bchedanxianzhi.setText(str(dict_strategy_args['b_order_action_limit']))
            # A撤单
            self.lineEdit_Achedan.setText(str(obj_strategy.get_a_action_count()))
            # B撤单
            self.lineEdit_Bchedan.setText(str(obj_strategy.get_b_action_count()))
            # 空头开
            self.doubleSpinBox_kongtoukai.setValue(dict_strategy_args['sell_open'])
            self.doubleSpinBox_kongtoukai.setSingleStep(obj_strategy.get_a_price_tick())
            # 空头平
            self.doubleSpinBox_kongtouping.setValue(dict_strategy_args['buy_close'])
            self.doubleSpinBox_kongtouping.setSingleStep(obj_strategy.get_a_price_tick())
            # 多头开
            self.doubleSpinBox_duotoukai.setValue(dict_strategy_args['buy_open'])
            self.doubleSpinBox_duotoukai.setSingleStep(obj_strategy.get_a_price_tick())
            # 多头平
            self.doubleSpinBox_duotouping.setValue(dict_strategy_args['sell_close'])
            self.doubleSpinBox_duotouping.setSingleStep(obj_strategy.get_a_price_tick())
            # 空头开-开关
            if dict_strategy_args['sell_open_on_off'] == 0:
                self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
            elif dict_strategy_args['sell_open_on_off'] == 1:
                self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)
            # 空头平-开关
            if dict_strategy_args['buy_close_on_off'] == 0:
                self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
            elif dict_strategy_args['buy_close_on_off'] == 1:
                self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)
            # 多头开-开关
            if dict_strategy_args['buy_open_on_off'] == 0:
                self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
            elif dict_strategy_args['buy_open_on_off'] == 1:
                self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)
            # 多头平-开关
            if dict_strategy_args['sell_close_on_off'] == 0:
                self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
            elif dict_strategy_args['sell_close_on_off'] == 1:
                self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)
            # A总卖
            self.lineEdit_Azongsell.setText(str(dict_strategy_position['position_a_sell']))
            # A昨卖
            self.lineEdit_Azuosell.setText(str(dict_strategy_position['position_a_sell_yesterday']))
            # B总买
            self.lineEdit_Bzongbuy.setText(str(dict_strategy_position['position_b_buy']))
            # B昨买
            self.lineEdit_Bzuobuy.setText(str(dict_strategy_position['position_b_buy_yesterday']))
            # A总买
            self.lineEdit_Azongbuy.setText(str(dict_strategy_position['position_a_buy']))
            # A昨买
            self.lineEdit_Azuobuy.setText(str(dict_strategy_position['position_a_buy_yesterday']))
            # B总卖
            self.lineEdit_Bzongsell.setText(str(dict_strategy_position['position_b_sell']))
            # B昨卖
            self.lineEdit_Bzuosell.setText(str(dict_strategy_position['position_b_sell_yesterday']))
            # A撤单
            self.lineEdit_Achedan.setText(str(obj_strategy.get_a_action_count()))
            # B撤单
            self.lineEdit_Bchedan.setText(str(obj_strategy.get_b_action_count()))

            # 恢复发送和设置持仓按钮状态
            self.slot_restore_groupBox_pushButton()

        # self.slot_update_strategy_position(obj_strategy)  # 调用slot_update_strategy是连带调用slot_update_strategy_position

    """

    # 更新groupBox：更新全部item
    def update_groupBox(self):
        print(">>> QAccountWidget.update_groupBox() ")
        # 鼠标未点击任何策略之前，不更新groupBox
        if len(self.__dict_clicked_info[self.__current_tab_name]) == 0:
            return
        clicked_user_id = self.__dict_clicked_info[self.__current_tab_name]['user_id']
        clicked_strategy_id = self.__dict_clicked_info[self.__current_tab_name]['strategy_id']
        if clicked_user_id == '' or clicked_strategy_id == '':
            self.clean_groupBox()  # 清空groupBox
            return
        dict_user_data = self.__socket_manager.get_dict_user_process_data()[clicked_user_id][
            'running']  # 获取被选中的期货账户的所有数据
        # print(">>> QAccountWidget.update_groupBox() clicked_user_id =", clicked_user_id, "clicked_strategy_id", clicked_strategy_id, "dict_user_data =", dict_user_data)
        dict_strategy_arguments = dict_user_data['strategy_arguments'][clicked_strategy_id]
        dict_strategy_statistics = dict_user_data['strategy_statistics'][clicked_strategy_id]
        dict_strategy_position = dict_user_data['strategy_position'][clicked_strategy_id]
        dict_instrument_statistics = dict_user_data['instrument_statistics']
        # dict_trading_account = dict_user_data['trading_account']  # 期货账户资金情况
        a_instrument_id = dict_strategy_arguments['a_instrument_id']
        b_instrument_id = dict_strategy_arguments['b_instrument_id']
        # a_price_tick = dict_strategy_arguments['a_price_tick']
        # b_price_tick = dict_strategy_arguments['b_price_tick']
        # a_action_count = dict_instrument_statistics[a_instrument_id]['action_count']  # A合约撤单次数
        # b_action_count = dict_instrument_statistics[b_instrument_id]['action_count']  # B合约撤单次数
        if a_instrument_id in dict_instrument_statistics:
            a_action_count = dict_instrument_statistics[a_instrument_id]['action_count']  # A合约撤单次数
        else:
            a_action_count = 0
        if b_instrument_id in dict_instrument_statistics:
            b_action_count = dict_instrument_statistics[b_instrument_id]['action_count']  # B合约撤单次数
        else:
            b_action_count = 0

        self.lineEdit_qihuozhanghao.setText(clicked_user_id)  # 期货账号
        self.lineEdit_celuebianhao.setText(clicked_strategy_id)  # 策略编号
        index_comboBox = self.comboBox_jiaoyimoxing.findText(dict_strategy_arguments['trade_model'])  # 交易模型
        if index_comboBox != -1:
            self.comboBox_jiaoyimoxing.setCurrentIndex(index_comboBox)
        index_comboBox = self.comboBox_xiadansuanfa.findText(dict_strategy_arguments['order_algorithm'])  # 下单算法
        if index_comboBox != -1:
            self.comboBox_xiadansuanfa.setCurrentIndex(index_comboBox)
        self.lineEdit_Aheyue.setText(dict_strategy_arguments['a_instrument_id'])  # A合约
        self.lineEdit_Bheyue.setText(dict_strategy_arguments['b_instrument_id'])  # B合约
        self.lineEdit_Achengshu.setText(str(dict_strategy_arguments['instrument_a_scale']))  # A合约乘数
        self.lineEdit_Bchengshu.setText(str(dict_strategy_arguments['instrument_b_scale']))  # B合约乘数
        self.lineEdit_zongshou.setText(str(dict_strategy_arguments['lots']))  # 总手
        self.lineEdit_meifen.setText(str(dict_strategy_arguments['lots_batch']))  # 每份
        self.spinBox_zhisun.setValue(dict_strategy_arguments['stop_loss'])  # 止损
        self.spinBox_rangjia.setValue(dict_strategy_arguments['spread_shift'])  # 超价触发
        self.spinBox_Abaodanpianyi.setValue(dict_strategy_arguments['a_limit_price_shift'])  # A报价偏移
        self.spinBox_Bbaodanpianyi.setValue(dict_strategy_arguments['b_limit_price_shift'])  # B报价偏移
        self.spinBox_Adengdai.setValue(dict_strategy_arguments['a_wait_price_tick'])  # A撤单等待
        self.spinBox_Bdengdai.setValue(dict_strategy_arguments['b_wait_price_tick'])  # B撤单等待
        self.lineEdit_Achedanxianzhi.setText(str(dict_strategy_arguments['a_order_action_limit']))  # A撤单限制
        self.lineEdit_Bchedanxianzhi.setText(str(dict_strategy_arguments['b_order_action_limit']))  # B撤单限制
        self.lineEdit_Achedan.setText(str(a_action_count))  # A撤单
        self.lineEdit_Bchedan.setText(str(b_action_count))  # B撤单
        self.doubleSpinBox_kongtoukai.setValue(dict_strategy_arguments['sell_open'])  # 空头开
        # self.doubleSpinBox_kongtoukai.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        self.doubleSpinBox_kongtouping.setValue(dict_strategy_arguments['buy_close'])  # 空头平
        # self.doubleSpinBox_kongtouping.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        self.doubleSpinBox_duotoukai.setValue(dict_strategy_arguments['buy_open'])  # 多头开
        # self.doubleSpinBox_duotoukai.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        self.doubleSpinBox_duotouping.setValue(dict_strategy_arguments['sell_close'])  # 多头平
        # self.doubleSpinBox_duotouping.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        # 空头开-开关
        if dict_strategy_arguments['sell_open_on_off'] == 0:
            self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
        elif dict_strategy_arguments['sell_open_on_off'] == 1:
            self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)
        # 空头平-开关
        if dict_strategy_arguments['buy_close_on_off'] == 0:
            self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
        elif dict_strategy_arguments['buy_close_on_off'] == 1:
            self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)
        # 多头开-开关
        if dict_strategy_arguments['buy_open_on_off'] == 0:
            self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
        elif dict_strategy_arguments['buy_open_on_off'] == 1:
            self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)
        # 多头平-开关
        if dict_strategy_arguments['sell_close_on_off'] == 0:
            self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
        elif dict_strategy_arguments['sell_close_on_off'] == 1:
            self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)
        self.lineEdit_Azongsell.setText(str(dict_strategy_position['position_a_sell']))  # A总卖
        self.lineEdit_Azuosell.setText(str(dict_strategy_position['position_a_sell_yesterday']))  # A昨卖
        self.lineEdit_Bzongbuy.setText(str(dict_strategy_position['position_b_buy']))  # B总买
        self.lineEdit_Bzuobuy.setText(str(dict_strategy_position['position_b_buy_yesterday']))  # B昨买
        self.lineEdit_Azongbuy.setText(str(dict_strategy_position['position_a_buy']))  # A总买
        self.lineEdit_Azuobuy.setText(str(dict_strategy_position['position_a_buy_yesterday']))  # A昨买
        self.lineEdit_Bzongsell.setText(str(dict_strategy_position['position_b_sell']))  # B总卖
        self.lineEdit_Bzuosell.setText(str(dict_strategy_position['position_b_sell_yesterday']))  # B昨卖

    # 更新groupBox：全部元素
    def slot_update_group_box(self):
        # print(">>> QAccountWidget.slot_update_group_box() ", "self.__list_update_group_box_data =", self.__list_update_group_box_data)
        self.__group_box_price_tick = self.__list_update_group_box_data[36]  # groupBox中的最小跳
        self.lineEdit_qihuozhanghao.setText(self.__list_update_group_box_data[1])  # 期货账号
        self.lineEdit_celuebianhao.setText(self.__list_update_group_box_data[2])  # 策略编号
        index_comboBox = self.comboBox_jiaoyimoxing.findText(self.__list_update_group_box_data[16])  # 交易模型
        if index_comboBox != -1:
            self.comboBox_jiaoyimoxing.setCurrentIndex(index_comboBox)
        index_comboBox = self.comboBox_xiadansuanfa.findText(self.__list_update_group_box_data[17])  # 下单算法
        # print(">>> QAccountWidget.slot_update_group_box() index_comboBox =", index_comboBox)
        if index_comboBox != -1:
            self.comboBox_xiadansuanfa.setCurrentIndex(index_comboBox)
        self.lineEdit_Aheyue.setText(self.__list_update_group_box_data[45])  # A合约
        self.lineEdit_Bheyue.setText(self.__list_update_group_box_data[46])  # B合约
        self.lineEdit_Achengshu.setText(str(self.__list_update_group_box_data[47]))  # A合约乘数
        self.lineEdit_Bchengshu.setText(str(self.__list_update_group_box_data[48]))  # B合约乘数
        self.lineEdit_zongshou.setText(self.__list_update_group_box_data[18])  # 总手
        self.lineEdit_meifen.setText(self.__list_update_group_box_data[19])  # 每份
        self.spinBox_zhisun.setValue(self.__list_update_group_box_data[20])  # 止损
        self.spinBox_rangjia.setValue(self.__list_update_group_box_data[21])  # 超价触发
        self.spinBox_Abaodanpianyi.setValue(self.__list_update_group_box_data[23])  # A报价偏移
        self.spinBox_Bbaodanpianyi.setValue(self.__list_update_group_box_data[25])  # B报价偏移
        self.spinBox_Adengdai.setValue(self.__list_update_group_box_data[22])  # A撤单等待
        self.spinBox_Bdengdai.setValue(self.__list_update_group_box_data[24])  # B撤单等待
        self.lineEdit_Achedanxianzhi.setText(self.__list_update_group_box_data[26])  # A撤单限制
        self.lineEdit_Bchedanxianzhi.setText(self.__list_update_group_box_data[27])  # B撤单限制
        self.lineEdit_Achedan.setText(self.__list_update_group_box_data[28])  # A撤单
        self.lineEdit_Bchedan.setText(self.__list_update_group_box_data[29])  # B撤单
        self.doubleSpinBox_kongtoukai.setValue(self.__list_update_group_box_data[37])  # 空头开
        self.doubleSpinBox_kongtoukai.setSingleStep(self.__list_update_group_box_data[36])  # 设置step
        self.doubleSpinBox_kongtouping.setValue(self.__list_update_group_box_data[38])  # 空头平
        self.doubleSpinBox_kongtouping.setSingleStep(self.__list_update_group_box_data[36])  # 设置step
        self.doubleSpinBox_duotoukai.setValue(self.__list_update_group_box_data[40])  # 多头开
        self.doubleSpinBox_duotoukai.setSingleStep(self.__list_update_group_box_data[36])  # 设置step
        self.doubleSpinBox_duotouping.setValue(self.__list_update_group_box_data[39])  # 多头平
        self.doubleSpinBox_duotouping.setSingleStep(self.__list_update_group_box_data[36])  # 设置step
        # 空头开-开关
        if self.__list_update_group_box_data[41] == 0:
            self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
        elif self.__list_update_group_box_data[41] == 1:
            self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)
        # 空头平-开关
        if self.__list_update_group_box_data[42] == 0:
            self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
        elif self.__list_update_group_box_data[42] == 1:
            self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)
        # 多头开-开关
        if self.__list_update_group_box_data[44] == 0:
            self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
        elif self.__list_update_group_box_data[44] == 1:
            self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)
        # 多头平-开关
        if self.__list_update_group_box_data[43] == 0:
            self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
        elif self.__list_update_group_box_data[43] == 1:
            self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)
        self.lineEdit_Azongsell.setText(self.__list_update_group_box_data[30])  # A总卖
        self.lineEdit_Azuosell.setText(self.__list_update_group_box_data[31])  # A昨卖
        self.lineEdit_Bzongbuy.setText(self.__list_update_group_box_data[6])  # B总买
        self.lineEdit_Bzuobuy.setText(self.__list_update_group_box_data[35])  # B昨买
        self.lineEdit_Azongbuy.setText(self.__list_update_group_box_data[32])  # A总买
        self.lineEdit_Azuobuy.setText(self.__list_update_group_box_data[33])  # A昨买
        self.lineEdit_Bzongsell.setText(self.__list_update_group_box_data[5])  # B总卖
        self.lineEdit_Bzuosell.setText(self.__list_update_group_box_data[34])  # B昨卖
        self.lineEdit_Azongsell.setReadOnly(True)  # 文本框只读
        self.lineEdit_Azongsell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Azuosell.setReadOnly(True)
        self.lineEdit_Azuosell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzongbuy.setReadOnly(True)
        self.lineEdit_Bzongbuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzuobuy.setReadOnly(True)
        self.lineEdit_Bzuobuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Azongbuy.setReadOnly(True)
        self.lineEdit_Azongbuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Azuobuy.setReadOnly(True)
        self.lineEdit_Azuobuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzongsell.setReadOnly(True)
        self.lineEdit_Bzongsell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzuosell.setReadOnly(True)
        self.lineEdit_Bzuosell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.pushButton_set_position.setText("设置持仓")

    # 更新groupBox：仅更新统计类指标，不更新用户输入参数
    def slot_update_group_box_statistics(self):
        # self.lineEdit_qihuozhanghao.setText(self.__list_update_group_box_data[1])  # 期货账号
        # self.lineEdit_celuebianhao.setText(self.__list_update_group_box_data[2])  # 策略编号
        # index_comboBox = self.comboBox_jiaoyimoxing.findText(self.__list_update_group_box_data[15])  # 交易模型
        # if index_comboBox != -1:
        #     self.comboBox_jiaoyimoxing.setCurrentIndex(index_comboBox)
        # index_comboBox = self.comboBox_xiadansuanfa.findText(self.__list_update_group_box_data[16])  # 下单算法
        # if index_comboBox != -1:
        #     self.comboBox_xiadansuanfa.setCurrentIndex(index_comboBox)
        # self.lineEdit_zongshou.setText(self.__list_update_group_box_data[17])  # 总手
        # self.lineEdit_meifen.setText(self.__list_update_group_box_data[18])  # 每份
        # self.spinBox_zhisun.setValue(self.__list_update_group_box_data[19])  # 止损
        # self.spinBox_rangjia.setValue(self.__list_update_group_box_data[20])  # 超价触发
        # self.spinBox_Abaodanpianyi.setValue(self.__list_update_group_box_data[22])  # A报价偏移
        # self.spinBox_Bbaodanpianyi.setValue(self.__list_update_group_box_data[24])  # B报价偏移
        # self.spinBox_Adengdai.setValue(self.__list_update_group_box_data[21])  # A撤单等待
        # self.spinBox_Bdengdai.setValue(self.__list_update_group_box_data[23])  # B撤单等待
        # self.lineEdit_Achedanxianzhi.setText(self.__list_update_group_box_data[25])  # A撤单限制
        # self.lineEdit_Bchedanxianzhi.setText(self.__list_update_group_box_data[26])  # B撤单限制
        self.lineEdit_Achedan.setText(self.__list_update_group_box_data[28])  # A撤单
        self.lineEdit_Bchedan.setText(self.__list_update_group_box_data[29])  # B撤单
        # self.doubleSpinBox_kongtoukai.setValue(self.__list_update_group_box_data[36])  # 空头开
        # self.doubleSpinBox_kongtoukai.setSingleStep(1)  # 设置step
        # self.doubleSpinBox_kongtouping.setValue(self.__list_update_group_box_data[37])  # 空头平
        # self.doubleSpinBox_kongtouping.setSingleStep(1)  # 设置step
        # self.doubleSpinBox_duotoukai.setValue(self.__list_update_group_box_data[38])  # 多头开
        # self.doubleSpinBox_duotoukai.setSingleStep(1)  # 设置step
        # self.doubleSpinBox_duotouping.setValue(self.__list_update_group_box_data[39])  # 多头平
        # self.doubleSpinBox_duotouping.setSingleStep(1)  # 设置step
        # # 空头开-开关
        # if self.__list_update_group_box_data[40] == 0:
        #     self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
        # elif self.__list_update_group_box_data[40] == 1:
        #     self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)
        # # 空头平-开关
        # if self.__list_update_group_box_data[41] == 0:
        #     self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
        # elif self.__list_update_group_box_data[41] == 1:
        #     self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)
        # # 多头开-开关
        # if self.__list_update_group_box_data[43] == 0:
        #     self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
        # elif self.__list_update_group_box_data[43] == 1:
        #     self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)
        # # 多头平-开关
        # if self.__list_update_group_box_data[42] == 0:
        #     self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
        # elif self.__list_update_group_box_data[42] == 1:
        #     self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)
        # 当仓位输入框被激活为可编辑状态时，不更新持仓的item
        # if self.lineEdit_Azongsell.isEnabled() is False:
        if self.lineEdit_Azongsell.isReadOnly():  # 策略持仓的lineEdit为只读模式时更新策略持仓变量
            self.lineEdit_Azongsell.setText(self.__list_update_group_box_data[30])  # A总卖
            self.lineEdit_Azuosell.setText(self.__list_update_group_box_data[31])  # A昨卖
            self.lineEdit_Bzongbuy.setText(self.__list_update_group_box_data[6])  # B总买
            self.lineEdit_Bzuobuy.setText(self.__list_update_group_box_data[35])  # B昨买
            self.lineEdit_Azongbuy.setText(self.__list_update_group_box_data[32])  # A总买
            self.lineEdit_Azuobuy.setText(self.__list_update_group_box_data[33])  # A昨买
            self.lineEdit_Bzongsell.setText(self.__list_update_group_box_data[5])  # B总卖
            self.lineEdit_Bzuosell.setText(self.__list_update_group_box_data[34])  # B昨卖

    # 清空groupBox界面
    def clear_group_box(self):
        str_none = ''
        int_none = 0
        self.lineEdit_qihuozhanghao.setText(str_none)  # 期货账号
        self.lineEdit_celuebianhao.setText(str_none)  # 策略编号
        self.comboBox_jiaoyimoxing.setCurrentIndex(-1)
        self.comboBox_xiadansuanfa.setCurrentIndex(-1)
        self.lineEdit_Aheyue.setText(str_none)  # A合约
        self.lineEdit_Bheyue.setText(str_none)  # B合约
        self.lineEdit_Achengshu.setText(str_none)  # A合约乘数
        self.lineEdit_Bchengshu.setText(str_none)  # B合约乘数
        self.lineEdit_zongshou.setText(str_none)  # 总手
        self.lineEdit_meifen.setText(str_none)  # 每份
        self.spinBox_zhisun.setValue(int_none)  # 止损
        self.spinBox_rangjia.setValue(int_none)  # 超价触发
        self.spinBox_Abaodanpianyi.setValue(int_none)  # A报价偏移
        self.spinBox_Bbaodanpianyi.setValue(int_none)  # B报价偏移
        self.spinBox_Adengdai.setValue(int_none)  # A撤单等待
        self.spinBox_Bdengdai.setValue(int_none)  # B撤单等待
        self.lineEdit_Achedanxianzhi.setText(str_none)  # A撤单限制
        self.lineEdit_Bchedanxianzhi.setText(str_none)  # B撤单限制
        self.lineEdit_Achedan.setText(str_none)  # A撤单
        self.lineEdit_Bchedan.setText(str_none)  # B撤单
        self.doubleSpinBox_kongtoukai.setValue(int_none)  # 空头开
        self.doubleSpinBox_kongtoukai.setSingleStep(1)  # 设置step
        self.doubleSpinBox_kongtouping.setValue(int_none)  # 空头平
        self.doubleSpinBox_kongtouping.setSingleStep(1)  # 设置step
        self.doubleSpinBox_duotoukai.setValue(int_none)  # 多头开
        self.doubleSpinBox_duotoukai.setSingleStep(1)  # 设置step
        self.doubleSpinBox_duotouping.setValue(int_none)  # 多头平
        self.doubleSpinBox_duotouping.setSingleStep(1)  # 设置step
        # 空头开-开关
        self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
        # 空头平-开关
        self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
        # 多头开-开关
        self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
        # 多头平-开关
        self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
        self.lineEdit_Azongsell.setText(str_none)  # A总卖
        self.lineEdit_Azuosell.setText(str_none)  # A昨卖
        self.lineEdit_Bzongbuy.setText(str_none)  # B总买
        self.lineEdit_Bzuobuy.setText(str_none)  # B昨买
        self.lineEdit_Azongbuy.setText(str_none)  # A总买
        self.lineEdit_Azuobuy.setText(str_none)  # A昨买
        self.lineEdit_Bzongsell.setText(str_none)  # B总卖
        self.lineEdit_Bzuosell.setText(str_none)  # B昨卖

    # 更新groupBox：更新除用户输入部分的item
    def update_groupBox_part(self):
        # 鼠标未点击任何策略之前，不更新groupBox
        if len(self.__dict_clicked_info[self.__current_tab_name]) == 0:
            return
        clicked_user_id = self.__dict_clicked_info[self.__current_tab_name]['user_id']
        clicked_strategy_id = self.__dict_clicked_info[self.__current_tab_name]['strategy_id']
        if clicked_strategy_id == '' or clicked_user_id == '':
            return
        dict_user_data = self.__socket_manager.get_dict_user_process_data()[clicked_user_id]['running']  # 获取被选中的期货账户的所有数据
        # print(">>> QAccountWidget.update_groupBox_part() clicked_user_id =", clicked_user_id, "clicked_strategy_id", clicked_strategy_id, "dict_user_data =", dict_user_data)
        dict_strategy_arguments = dict_user_data['strategy_arguments'][clicked_strategy_id]
        dict_strategy_statistics = dict_user_data['strategy_statistics'][clicked_strategy_id]
        dict_strategy_position = dict_user_data['strategy_position'][clicked_strategy_id]
        dict_instrument_statistics = dict_user_data['instrument_statistics']
        # print(">>> QAccountWidget.update_groupBox_part() dict_instrument_statistics =", dict_instrument_statistics)
        # dict_trading_account = dict_user_data['trading_account']  # 期货账户资金情况
        a_instrument_id = dict_strategy_arguments['a_instrument_id']
        b_instrument_id = dict_strategy_arguments['b_instrument_id']
        # a_price_tick = dict_strategy_arguments['a_price_tick']
        # b_price_tick = dict_strategy_arguments['b_price_tick']
        if a_instrument_id in dict_instrument_statistics:
            a_action_count = dict_instrument_statistics[a_instrument_id]['action_count']  # A合约撤单次数
        else:
            a_action_count = 0
        if b_instrument_id in dict_instrument_statistics:
            b_action_count = dict_instrument_statistics[b_instrument_id]['action_count']  # B合约撤单次数
        else:
            b_action_count = 0
        self.lineEdit_qihuozhanghao.setText(clicked_user_id)  # 期货账号
        self.lineEdit_celuebianhao.setText(clicked_strategy_id)  # 策略编号
        # index_comboBox = self.comboBox_jiaoyimoxing.findText(dict_strategy_arguments['trade_model'])  # 交易模型
        # if index_comboBox != -1:
        #     self.comboBox_jiaoyimoxing.setCurrentIndex(index_comboBox)
        # index_comboBox = self.comboBox_xiadansuanfa.findText(dict_strategy_arguments['order_algorithm'])  # 下单算法
        # if index_comboBox != -1:
        #     self.comboBox_xiadansuanfa.setCurrentIndex(index_comboBox)
        # self.lineEdit_zongshou.setText(str(dict_strategy_arguments['lots']))  # 总手
        # self.lineEdit_meifen.setText(str(dict_strategy_arguments['lots_batch']))  # 每份
        # self.spinBox_zhisun.setValue(dict_strategy_arguments['stop_loss'])  # 止损
        # self.spinBox_rangjia.setValue(dict_strategy_arguments['spread_shift'])  # 超价触发
        # self.spinBox_Abaodanpianyi.setValue(dict_strategy_arguments['a_limit_price_shift'])  # A报价偏移
        # self.spinBox_Bbaodanpianyi.setValue(dict_strategy_arguments['b_limit_price_shift'])  # B报价偏移
        # self.spinBox_Adengdai.setValue(dict_strategy_arguments['a_wait_price_tick'])  # A撤单等待
        # self.spinBox_Bdengdai.setValue(dict_strategy_arguments['b_wait_price_tick'])  # B撤单等待
        # self.lineEdit_Achedanxianzhi.setText(str(dict_strategy_arguments['a_order_action_limit']))  # A撤单限制
        # self.lineEdit_Bchedanxianzhi.setText(str(dict_strategy_arguments['b_order_action_limit']))  # B撤单限制
        self.lineEdit_Achedan.setText(str(a_action_count))  # A撤单
        self.lineEdit_Bchedan.setText(str(b_action_count))  # B撤单
        # self.doubleSpinBox_kongtoukai.setValue(dict_strategy_arguments['sell_open'])  # 空头开
        # self.doubleSpinBox_kongtoukai.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        # self.doubleSpinBox_kongtouping.setValue(dict_strategy_arguments['buy_close'])  # 空头平
        # self.doubleSpinBox_kongtouping.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        # self.doubleSpinBox_duotoukai.setValue(dict_strategy_arguments['buy_open'])  # 多头开
        # self.doubleSpinBox_duotoukai.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        # self.doubleSpinBox_duotouping.setValue(dict_strategy_arguments['sell_close'])  # 多头平
        # self.doubleSpinBox_duotouping.setSingleStep(obj_strategy.get_a_price_tick())  # 设置step
        # # 空头开-开关
        # if dict_strategy_arguments['sell_open_on_off'] == 0:
        #     self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Unchecked)
        # elif dict_strategy_arguments['sell_open_on_off'] == 1:
        #     self.checkBox_kongtoukai.setCheckState(QtCore.Qt.Checked)
        # # 空头平-开关
        # if dict_strategy_arguments['buy_close_on_off'] == 0:
        #     self.checkBox_kongtouping.setCheckState(QtCore.Qt.Unchecked)
        # elif dict_strategy_arguments['buy_close_on_off'] == 1:
        #     self.checkBox_kongtouping.setCheckState(QtCore.Qt.Checked)
        # # 多头开-开关
        # if dict_strategy_arguments['buy_open_on_off'] == 0:
        #     self.checkBox_duotoukai.setCheckState(QtCore.Qt.Unchecked)
        # elif dict_strategy_arguments['buy_open_on_off'] == 1:
        #     self.checkBox_duotoukai.setCheckState(QtCore.Qt.Checked)
        # # 多头平-开关
        # if dict_strategy_arguments['sell_close_on_off'] == 0:
        #     self.checkBox_duotouping.setCheckState(QtCore.Qt.Unchecked)
        # elif dict_strategy_arguments['sell_close_on_off'] == 1:
        #     self.checkBox_duotouping.setCheckState(QtCore.Qt.Checked)
        self.lineEdit_Azongsell.setText(str(dict_strategy_position['position_a_sell']))  # A总卖
        self.lineEdit_Azuosell.setText(str(dict_strategy_position['position_a_sell_yesterday']))  # A昨卖
        self.lineEdit_Bzongbuy.setText(str(dict_strategy_position['position_b_buy']))  # B总买
        self.lineEdit_Bzuobuy.setText(str(dict_strategy_position['position_b_buy_yesterday']))  # B昨买
        self.lineEdit_Azongbuy.setText(str(dict_strategy_position['position_a_buy']))  # A总买
        self.lineEdit_Azuobuy.setText(str(dict_strategy_position['position_a_buy_yesterday']))  # A昨买
        self.lineEdit_Bzongsell.setText(str(dict_strategy_position['position_b_sell']))  # B总卖
        self.lineEdit_Bzuosell.setText(str(dict_strategy_position['position_b_sell_yesterday']))  # B昨卖

    # 更新单个策略的界面显示，调用情景：所有调用self.slot_update_strategy()的时候、order回调、trade回调、撤单
    @QtCore.pyqtSlot(object)
    def slot_update_strategy_position(self, obj_strategy):
        dict_strategy_args = obj_strategy.get_arguments()  # 策略参数
        dict_strategy_position = obj_strategy.get_position()  # 策略持仓
        dict_strategy_statistics = obj_strategy.get_dict_statistics()  # 交易统计数据
        print(">>> QAccountWidget.slot_update_strategy_position() "
              "widget_name=", self.__widget_name,
              "user_id=", dict_strategy_args['user_id'],
              "strategy_id=", dict_strategy_args['strategy_id'],
              "self.sender()=", self.sender(),
              "dict_strategy_position=", dict_strategy_position)
        """更新tableWidget"""
        for i_row in range(self.tableWidget_Trade_Args.rowCount()):
            # 在table中找到对应的策略行，更新界面显示，跳出for
            if self.tableWidget_Trade_Args.item(i_row, 2).text() == obj_strategy.get_user_id() and self.tableWidget_Trade_Args.item(i_row, 3).text() == obj_strategy.get_strategy_id():
                # 总持仓
                item_position = self.tableWidget_Trade_Args.item(i_row, 5)
                item_position.setText(
                    str(dict_strategy_position['position_a_buy'] + dict_strategy_position['position_a_sell']))
                # 买持仓
                item_position_buy = self.tableWidget_Trade_Args.item(i_row, 6)
                item_position_buy.setText(
                    str(dict_strategy_position['position_a_buy'] + dict_strategy_position['position_a_buy']))
                # 卖持仓
                item_position_sell = self.tableWidget_Trade_Args.item(i_row, 7)
                item_position_sell.setText(
                    str(dict_strategy_position['position_a_buy'] + dict_strategy_position['position_a_sell']))
                # 持仓盈亏，策略有持仓的时候由行情驱动更新，可以设计为定时任务
                # 平仓盈亏
                item_profit_close = self.tableWidget_Trade_Args.item(i_row, 9)
                item_profit_close.setText(
                    str(dict_strategy_statistics['profit_close']))
                # 手续费
                item_commission = self.tableWidget_Trade_Args.item(i_row, 10)
                item_commission.setText(
                    str(dict_strategy_statistics['commission']))
                # 净盈亏
                item_profit = self.tableWidget_Trade_Args.item(i_row, 11)
                item_profit.setText(
                    str(dict_strategy_statistics['profit']))
                # 成交量
                item_volume = self.tableWidget_Trade_Args.item(i_row, 12)
                item_volume.setText(
                    str(dict_strategy_statistics['volume']))
                # 成交金额
                item_amount = self.tableWidget_Trade_Args.item(i_row, 13)
                item_amount.setText(
                    str(dict_strategy_statistics['amount']))
                # A成交率
                item_A_traded_rate = self.tableWidget_Trade_Args.item(i_row, 14)
                item_A_traded_rate.setText(
                    str(dict_strategy_statistics['A_traded_rate']))
                # B成交率
                item_B_traded_rate = self.tableWidget_Trade_Args.item(i_row, 15)
                item_B_traded_rate.setText(
                    str(dict_strategy_statistics['B_traded_rate']))

            break  # 在tableWidget中找到对应的策略行，结束for循环
        """更新groupBox"""
        if self.__clicked_strategy == obj_strategy:  # 只更新在当前窗口中被鼠标选中的策略
            # print(">>> QAccountWidget.slot_update_strategy() 更新groupBox，widget_name=", self.__widget_name, "user_id=", obj_strategy.get_user_id(), "strategy_id=", obj_strategy.get_strategy_id())
            # A总卖
            self.lineEdit_Azongsell.setText(str(dict_strategy_position['position_a_sell']))
            # A昨卖
            self.lineEdit_Azuosell.setText(str(dict_strategy_position['position_a_sell_yesterday']))
            # B总买
            self.lineEdit_Bzongbuy.setText(str(dict_strategy_position['position_b_buy']))
            # B昨买
            self.lineEdit_Bzuobuy.setText(str(dict_strategy_position['position_b_buy_yesterday']))
            # A总买
            self.lineEdit_Azongbuy.setText(str(dict_strategy_position['position_a_buy']))
            # A昨买
            self.lineEdit_Azuobuy.setText(str(dict_strategy_position['position_a_buy_yesterday']))
            # B总卖
            self.lineEdit_Bzongsell.setText(str(dict_strategy_position['position_b_sell']))
            # B昨卖
            self.lineEdit_Bzuosell.setText(str(dict_strategy_position['position_b_sell_yesterday']))
            # A撤单
            self.lineEdit_Achedan.setText(str(obj_strategy.get_a_action_count()))
            # B撤单
            self.lineEdit_Bchedan.setText(str(obj_strategy.get_b_action_count()))

    # 绑定信号槽：收到服务端的查询策略信息 -> groupBox界面状态还原（激活查询按钮、恢复“设置持仓”按钮）
    @QtCore.pyqtSlot()
    def slot_restore_groupBox_pushButton(self):
        self.pushButton_set_strategy.setEnabled(True)  # 激活按钮
        self.pushButton_query_strategy.setEnabled(True)
        self.pushButton_set_position.setEnabled(True)
        self.lineEdit_Azongsell.setEnabled(False)  # 禁用编辑框
        self.lineEdit_Azuosell.setEnabled(False)
        self.lineEdit_Bzongbuy.setEnabled(False)
        self.lineEdit_Bzuobuy.setEnabled(False)
        self.lineEdit_Azongbuy.setEnabled(False)
        self.lineEdit_Azuobuy.setEnabled(False)
        self.lineEdit_Bzongsell.setEnabled(False)
        self.lineEdit_Bzuosell.setEnabled(False)
        self.pushButton_set_position.setText("设置持仓")

    # 槽函数：维护“开始策略”按钮的状态，分别被一个总账户窗口信号和多个单期货账户窗口信号绑定
    @QtCore.pyqtSlot()
    def slot_update_pushButton_start_strategy(self):
        self.pushButton_start_strategy.setEnabled(True)  # 激活按钮
        # if self.is_single_user_widget():
        #     on_off = self.__user.get_on_off()  # 窗口对应的期货账户的交易开关
        #     if on_off == 1:
        #         self.pushButton_start_strategy.setText("关闭策略")
        #     elif on_off == 0:
        #         self.pushButton_start_strategy.setText("开始策略")
        # else:
        # on_off = self.__ctp_manager.get_on_off()  # 总账户窗口对应的交易员开关
        if self.is_single_user_widget():
            on_off = self.__user.get_on_off()
        else:
            on_off = self.__ctp_manager.get_on_off()
        if on_off == 1:
            self.pushButton_start_strategy.setText("关闭策略")
        elif on_off == 0:
            self.pushButton_start_strategy.setText("开始策略")


    @QtCore.pyqtSlot()
    def slot_pushButton_set_position_setEnabled(self):
        self.pushButton_set_position.setText("设置持仓")
        self.pushButton_set_position.setEnabled(True)  # 设置为可用

    # 初始化界面：策略统计类指标（统计代码在Strategy类中实现，界面层的类仅负责显示）
    def init_table_widget_statistics(self):
        for i_strategy in self.__client_main.get_CTPManager().get_list_strategy():  # 遍历所有策略
            for i_row in range(self.tableWidget_Trade_Args.rowCount()):  # 遍历行
                # 策略与行对应
                if self.tableWidget_Trade_Args.item(i_row, 2).text() == i_strategy.get_user_id() and self.tableWidget_Trade_Args.item(i_row, 3).text() == i_strategy.get_strategy_id():
                    position = i_strategy.get_position()['position_a_buy'] + i_strategy.get_position()['position_a_sell']
                    self.tableWidget_Trade_Args.item(i_row, 7).setText(str(position))

    # 更新界面：价差行情
    @QtCore.pyqtSlot(dict)
    def slot_update_spread(self, dict_input):
        # print(">>> QAccountWidget.slot_update_spread() 更新界面价差行情，widget_name=", self.__widget_name)
        # dict_input = {'spread_long': int, 'spread_short': int}
        # 更新多头价差显示
        if self.__spread_long is None:  # 初始值
            # self.lineEdit_duotoujiacha.setText(("%.2f" % dict_input['spread_long']))
            # self.lineEdit_duotoujiacha.setStyleSheet("color: rgb(0, 0, 0);")
            self.signal_lineEdit_duotoujiacha_setText.emit(("%.2f" % dict_input['spread_long']))
            self.signal_lineEdit_duotoujiacha_setStyleSheet.emit("color: rgb(0, 0, 0);")
        elif dict_input['spread_long'] > self.__spread_long:  # 最新值大于前值
            # self.lineEdit_duotoujiacha.setText(("%.2f" % dict_input['spread_long']))
            # self.lineEdit_duotoujiacha.setStyleSheet("color: rgb(255, 0, 0);font-weight:bold;")
            self.signal_lineEdit_duotoujiacha_setText.emit(("%.2f" % dict_input['spread_long']))
            self.signal_lineEdit_duotoujiacha_setStyleSheet.emit("color: rgb(255, 0, 0);font-weight:bold;")
        elif dict_input['spread_long'] < self.__spread_long:  # 最新值小于前值
            # self.lineEdit_duotoujiacha.setText(("%.2f" % dict_input['spread_long']))
            # self.lineEdit_duotoujiacha.setStyleSheet("color: rgb(0, 170, 0);font-weight:bold;")
            self.signal_lineEdit_duotoujiacha_setText.emit(("%.2f" % dict_input['spread_long']))
            self.signal_lineEdit_duotoujiacha_setStyleSheet.emit("color: rgb(0, 170, 0);font-weight:bold;")
        # 更新空头价差显示
        if self.__spread_short is None:  # 初始值
            # self.lineEdit_kongtoujiacha.setText(("%.2f" % dict_input['spread_short']))
            # self.lineEdit_kongtoujiacha.setStyleSheet("color: rgb(0, 0, 0);")
            self.signal_lineEdit_kongtoujiacha_setText.emit(("%.2f" % dict_input['spread_short']))
            self.signal_lineEdit_kongtoujiacha_setStyleSheet.emit("color: rgb(0, 0, 0);")
        elif dict_input['spread_short'] > self.__spread_short:  # 最新值大于前值
            # self.lineEdit_kongtoujiacha.setText(("%.2f" % dict_input['spread_short']))
            # self.lineEdit_kongtoujiacha.setStyleSheet("color: rgb(255, 0, 0);font-weight:bold;")
            self.signal_lineEdit_kongtoujiacha_setText.emit(("%.2f" % dict_input['spread_short']))
            self.signal_lineEdit_kongtoujiacha_setStyleSheet.emit("color: rgb(255, 0, 0);font-weight:bold;")
        elif dict_input['spread_short'] < self.__spread_short:  # 最新值小于前值
            # self.lineEdit_kongtoujiacha.setText(("%.2f" % dict_input['spread_short']))
            # self.lineEdit_kongtoujiacha.setStyleSheet("color: rgb(0, 170, 0);font-weight:bold;")
            self.signal_lineEdit_kongtoujiacha_setText.emit(("%.2f" % dict_input['spread_short']))
            self.signal_lineEdit_kongtoujiacha_setStyleSheet.emit("color: rgb(0, 170, 0);font-weight:bold;")
        self.__spread_long = dict_input['spread_long']  # 储存最后值，与后来的值比较，如果之变化就刷新界面
        self.__spread_short = dict_input['spread_short']

    # 间接槽函数，目的槽函数在StrategyDataModel.slot_update_strategy_on_off()
    def slot_update_strategy_on_off(self, dict_args):
        # self.StrategyDataModel.slot_update_strategy_on_off(dict_args)
        pass

    # 点击“发送”按钮后的参数更新，要更新的策略为goupBox中显示的user_id、strategy_id对应的
    def update_groupBox_trade_args_for_set(self):
        # 遍历策略列表，找到与界面显示相同的策略对象实例
        for i_strategy in self.__client_main.get_CTPManager().get_list_strategy():
            if i_strategy.get_user_id() == self.comboBox_qihuozhanghao.currentText() and i_strategy.get_strategy_id() == self.comboBox_celuebianhao.currentText():
                dict_args = i_strategy.get_arguments()
                self.lineEdit_Aheyue.setText(dict_args['Aheyue'])  # A合约
                self.lineEdit_Bheyue.setText(dict_args['Bheyue'])
                self.lineEdit_Achengshu.setText(str(dict_args['Achengshu']))  # A合约乘数
                self.lineEdit_Bchengshu.setText(str(dict_args['Bchengshu']))
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
                break

    # 更新界面：“账户资金”框，panel_show_account
    """
    @QtCore.pyqtSlot(dict)
    def slot_update_panel_show_account(self, dict_args):
        print(">>> QAccountWidget.slot_update_panel_show_account() dict_args=", dict_args)

        # 参数实例
        # {
        # 'Capital': 1760786.59375,
        # 'PreBalance': 1760668.7,
        # 'PositionProfit': 200.0,
        # 'CloseProfit': 0.0,
        # 'Commission': 82.10625,
        # 'Available': 1629190.59375,
        # 'CurrMargin': 131396.0,
        # 'FrozenMargin': 0.0,
        # 'Risk': 0.07462346684510018
        # 'Deposit': 0.0,
        # 'Withdraw': 0.0,
        # }

        self.label_value_dongtaiquanyi.setText(str(int(dict_args['Capital'])))  # 动态权益
        self.label_value_jingtaiquanyi.setText(str(int(dict_args['PreBalance'])))  # 静态权益
        self.label_value_chicangyingkui.setText(str(int(dict_args['PositionProfit'])))  # 持仓盈亏
        self.label_value_pingcangyingkui.setText(str(int(dict_args['CloseProfit'])))  # 平仓盈亏
        self.label_value_shouxufei.setText(str(int(dict_args['Commission'])))  # 手续费
        self.label_value_keyongzijin.setText(str(int(dict_args['Available'])))  # 可用资金
        self.label_value_zhanyongbaozhengjin.setText(str(int(dict_args['CurrMargin'])))  # 占用保证金
        # self.label_value_xiadandongjie.setText(str(int(dict_args['FrozenMargin'])))  # 下单冻结
        self.label_value_fengxiandu.setText(str(int(dict_args['Risk']*100))+'%')  # 风险度
        self.label_value_jinrirujin.setText(str(int(dict_args['Deposit'])))  # 今日入金
        self.label_value_jinrichujin.setText(str(int(dict_args['Withdraw'])))  # 今日出金
    """

    # 更新界面：“账户资金”框，panel_show_account
    def slot_update_panel_show_account(self, list_data):
        # print(">>> QAccountWidget.slot_update_panel_show_account() self.__current_tab_name =", self.__current_tab_name, "list_data =", list_data)
        self.label_value_dongtaiquanyi.setText(str(list_data[0]))  # 动态权益
        self.label_value_jingtaiquanyi.setText(str(list_data[1]))  # 静态权益
        self.label_value_chicangyingkui.setText(str(list_data[2]))  # 持仓盈亏
        self.label_value_pingcangyingkui.setText(str(list_data[3]))  # 平仓盈亏
        self.label_value_shouxufei.setText(str(list_data[4]))  # 手续费
        self.label_value_keyongzijin.setText(str(list_data[5]))  # 可用资金
        self.label_value_zhanyongbaozhengjin.setText(str(list_data[6]))  # 占用保证金
        self.label_value_fengxiandu.setText(list_data[7])  # 风险度
        self.label_value_jinrirujin.setText(str(list_data[8]))  # 今日入金
        self.label_value_jinrichujin.setText(str(list_data[9]))  # 今日出金

    # 鼠标右击弹出菜单中的“添加策略”
    @pyqtSlot()
    def slot_action_add_strategy(self):
        print(">>> QAccountWidget.slot_action_add_strategy() called")
        # self.__client_main.get_QNewStrategy().update_comboBox_user_id_menu()  # 更新新建策略框中的期货账号可选项菜单
        # self.__q_new_strategy
        # 设置期货账号可选项
        self.__q_new_strategy.update_comboBox_user_id_menu()
        self.__q_new_strategy.show()
        # todo...

    """
    # 鼠标右击弹出菜单中的“删除策略”
    @pyqtSlot()
    def slot_action_del_strategy(self):
        print(">>> QAccountWidget.slot_action_del_strategy() widget_name=", self.__widget_name)
        # 没有任何策略的窗口点击“删除策略”，无任何响应
        if self.tableWidget_Trade_Args.rowCount() == 0:
            return
        # 鼠标点击信息为空，跳过
        if self.__clicked_item is None or self.__clicked_status is None:
            return
        # 找到将要删除的策略对象
        for i_strategy in self.__ctp_manager.get_list_strategy():
            print(">>> QAccountWidget.slot_action_del_strategy() i_strategy.get_user_id()=", i_strategy.get_user_id(), "i_strategy.get_strategy_id()=", i_strategy.get_strategy_id(), "self.__clicked_status['user_id']=", self.__clicked_status['user_id'], "self.__clicked_status['strategy_id']=", self.__clicked_status['strategy_id'])
            if i_strategy.get_user_id() == self.__clicked_status['user_id'] and i_strategy.get_strategy_id() == self.__clicked_status['strategy_id']:
                print(">>> QAccountWidget.slot_action_del_strategy() 找到将要删除的策略，user_id=", i_strategy.get_user_id(), "strategy_id=", i_strategy.get_strategy_id())
                # 判断持仓：有持仓，跳出
                dict_position = i_strategy.get_position()
                for i in dict_position:
                    if dict_position[i] != 0:
                        print("QAccountWidgetslot_action_del_strategy() 不能删除有持仓的策略，user_id=", i_strategy.get_user_id(), "strategy_id=", i_strategy.get_strategy_id())
                        QMessageBox().showMessage("错误", "不能删除有持仓的策略")
                        return
                # 策略开关的状态为开，跳过
                if i_strategy.get_on_off() == 1:
                    print("QAccountWidgetslot_action_del_strategy() 不能删除交易开关为开的策略，user_id=", i_strategy.get_user_id(), "strategy_id=", i_strategy.get_strategy_id())
                    QMessageBox().showMessage("错误", "不能删除交易开关为开的策略")
                    return

                # 向服务端发送删除策略指令
                dict_delete_strategy = {'MsgRef': self.__client_main.get_SocketManager().msg_ref_add(),
                                        'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                        'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                        'MsgType': 7,  # 删除策略
                                        'TraderID': i_strategy.get_trader_id(),
                                        'UserID': i_strategy.get_user_id(),
                                        'StrategyID': i_strategy.get_strategy_id()
                                        }
                json_delete_strategy = json.dumps(dict_delete_strategy)
                self.signal_send_msg.emit(json_delete_strategy)
                break  # 找到对应的策略对象，跳出for循环
    """

    # 鼠标右击弹出菜单中的“删除策略”
    @pyqtSlot()
    def slot_action_del_strategy(self):
        list_update_group_box_data = self.get_list_update_group_box_data()
        strategy_on_off = list_update_group_box_data[0].checkState()
        # print(">>> QAccountWidget.slot_action_del_strategy() 删除策略，user_id =", self.__clicked_user_id, "strategy_id =", self.__clicked_strategy_id, "策略开关 =", strategy_on_off, type(strategy_on_off))
        # 判断策略是否可以安全删除：策略无持仓，开关为关闭
        if strategy_on_off == 2:
            print(">>> QAccountWidget.slot_action_del_strategy() 不允许删除策略开关为开的策略")
            # MessageBox().showMessage("错误", "不允许删除策略开关为开的策略！")
            dict_args = {"title": "消息", "main": "不允许删除策略开关为开的策略"}
            self.signal_show_alert.emit(dict_args)
            return
        # B总卖、B总买、A总卖、A总买
        if list_update_group_box_data[5] != '0' \
                or list_update_group_box_data[6] != '0' \
                or list_update_group_box_data[30] != '0' \
                or list_update_group_box_data[32] != '0':
            print(">>> QAccountWidget.slot_action_del_strategy() 不允许删除有持仓的策略", list_update_group_box_data[5], list_update_group_box_data[6], list_update_group_box_data[30], list_update_group_box_data[32], list_update_group_box_data)
            # MessageBox().showMessage("错误", "不允许删除有持仓的策略！")
            dict_args = {"title": "消息", "main": "不允许删除有持仓的策略"}
            self.signal_show_alert.emit(dict_args)
            return

        print(">>> QAccountWidget.slot_action_del_strategy() self.get_list_update_group_box_data() =", self.get_list_update_group_box_data())
        dict_msg = {
            'MsgRef': self.__socket_manager.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 7,  # 删除策略
            'TraderID': self.__socket_manager.get_trader_id(),
            'UserID': self.__clicked_user_id,
            'StrategyID':self.__clicked_strategy_id
            }
        # json_msg = json.dumps(dict_msg)
        self.signal_send_msg.emit(dict_msg)

    def send_msg_revise_strategy_on_off(self, dict_args):
        dict_msg = {
            'MsgRef': self.__socket_manager.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 13,  # 修改策略开关
            'TraderID': self.__socket_manager.get_trader_id(),
            'UserID': dict_args['user_id'],
            'StrategyID': dict_args['strategy_id'],
            'OnOff': dict_args['on_off']
        }
        # json_msg = json.dumps(dict_msg)
        self.signal_send_msg.emit(dict_msg)

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

    """
    @pyqtSlot()
    def on_pushButton_start_strategy_clicked(self):
        # Slot documentation goes here.
        # TODO: not implemented yet
        # raise NotImplementedError
        if self.is_single_user_widget():
            on_off = self.__user.get_on_off()
        else:
            on_off = self.__ctp_manager.get_on_off()
        print(">>> QAccountWidget.on_pushButton_start_strategy_clicked() 按钮状态：", self.pushButton_start_strategy.text(), on_off)
        if self.pushButton_start_strategy.text() == '开始策略' and on_off == 0:
            self.pushButton_start_strategy.setEnabled(False)  # 将按钮禁用
            # 发送开始策略命令：将期货账户开关修改为开，值为1
            if self.is_single_user_widget():
                dict_trade_onoff = {
                    'MsgRef': self.__socket_manager.msg_ref_add(),
                    'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                    'MsgSrc': 0,  # 消息源，客户端0，服务端1
                    'MsgType': 9,  # 单个期货账户交易开关
                    'TraderID': self.__ctp_manager.get_trader_id(),
                    'UserID': self.__widget_name,
                    'OnOff': 1}
            else:
                dict_trade_onoff = {
                    'MsgRef': self.__socket_manager.msg_ref_add(),
                    'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                    'MsgSrc': 0,  # 消息源，客户端0，服务端1
                    'MsgType': 8,  # 交易员交易开关
                    'TraderID': self.__ctp_manager.get_trader_id(),
                    'OnOff': 1}
            json_trade_onoff = json.dumps(dict_trade_onoff)
            self.signal_send_msg.emit(json_trade_onoff)
        elif self.pushButton_start_strategy.text() == '关闭策略' and on_off == 1:
            self.pushButton_start_strategy.setEnabled(False)  # 将按钮禁用
            # 发送关闭策略命令：将期货账户开关修改为关，值为0
            if self.is_single_user_widget():
                dict_trade_onoff = {
                    'MsgRef': self.__socket_manager.msg_ref_add(),
                    'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                    'MsgSrc': 0,  # 消息源，客户端0，服务端1
                    'MsgType': 9,  # 单个期货账户交易开关
                    'TraderID': self.__ctp_manager.get_trader_id(),
                    'UserID': self.__widget_name,
                    'OnOff': 0}
            else:
                dict_trade_onoff = {
                    'MsgRef': self.__socket_manager.msg_ref_add(),
                    'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                    'MsgSrc': 0,  # 消息源，客户端0，服务端1
                    'MsgType': 8,  # 交易员交易开关
                    'TraderID': self.__ctp_manager.get_trader_id(),
                    'OnOff': 0}
            json_trade_onoff = json.dumps(dict_trade_onoff)
            self.signal_send_msg.emit(json_trade_onoff)
        else:
            print("QAccountWidget.on_pushButton_start_strategy_clicked() 按钮显示状态与内核值不一致，不发送指令交易开关指令，widget_name=", self.__widget_name, "按钮显示：", self.pushButton_start_strategy.text(), "内核开关值：", on_off)
    """

    @pyqtSlot()
    def on_pushButton_start_strategy_clicked(self):
        if self.pushButton_start_strategy.text() == '开始策略':
            # self.pushButton_start_strategy.setEnabled(False)  # 将按钮禁用
            self.pushButton_start_strategy.setText('停止策略')
            on_off = 1
        elif self.pushButton_start_strategy.text() == '停止策略':
            self.pushButton_start_strategy.setText('开始策略')
            on_off = 0

        if self.__current_tab_name == '所有账户':
            dict_trade_onoff = {
                'MsgRef': self.__socket_manager.msg_ref_add(),
                'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                'MsgSrc': 0,  # 消息源，客户端0，服务端1
                'MsgType': 8,  # 交易员交易开关
                'TraderID': self.__socket_manager.get_trader_id(),
                'OnOff': on_off}
        else:
            dict_trade_onoff = {
                'MsgRef': self.__socket_manager.msg_ref_add(),
                'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                'MsgSrc': 0,  # 消息源，客户端0，服务端1
                'MsgType': 9,  # 期货账户开关
                'TraderID': self.__socket_manager.get_trader_id(),
                'UserID': self.__current_tab_name,
                'OnOff': on_off}
        # json_trade_onoff = json.dumps(dict_trade_onoff)
        self.signal_send_msg.emit(dict_trade_onoff)

    # 联动加
    @pyqtSlot()
    def on_pushButton_liandongjia_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        # price_tick = self.__client_main.get_clicked_strategy().get_a_price_tick()  # 最小跳
        # print(">>> on_pushButton_liandongjia_clicked() self.lineEdit_qihuozhanghao.text() =", self.lineEdit_qihuozhanghao.text())
        if self.lineEdit_qihuozhanghao.text() == '':
            print(">>> on_pushButton_liandongjia_clicked() if self.lineEdit_qihuozhanghao.text() == ''")
            return
        value = self.doubleSpinBox_duotoukai.value() + self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_duotoukai.setValue(value)
        value = self.doubleSpinBox_duotouping.value() + self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_duotouping.setValue(value)
        value = self.doubleSpinBox_kongtoukai.value() + self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_kongtoukai.setValue(value)
        value = self.doubleSpinBox_kongtouping.value() + self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_kongtouping.setValue(value)

    # 联动减
    @pyqtSlot()
    def on_pushButton_liandongjian_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        # price_tick = self.__client_main.get_clicked_strategy().get_a_price_tick()  # 最小跳
        if self.lineEdit_qihuozhanghao.text() == '':
            print(">>> on_pushButton_liandongjia_clicked() if self.lineEdit_qihuozhanghao.text() == ''")
            return
        value = self.doubleSpinBox_duotoukai.value() - self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_duotoukai.setValue(value)
        value = self.doubleSpinBox_duotouping.value() - self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_duotouping.setValue(value)
        value = self.doubleSpinBox_kongtoukai.value() - self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_kongtoukai.setValue(value)
        value = self.doubleSpinBox_kongtouping.value() - self.__group_box_price_tick  # 计算更新值
        self.doubleSpinBox_kongtouping.setValue(value)

    # 修改策略参数，参数排错
    def arguments_examine(self):
        # QMessageBox().showMessage("错误", "总手、每份参数错误！")
        if len(self.lineEdit_qihuozhanghao.text()) <= 0 or len(self.lineEdit_celuebianhao.text()) <= 0:
            # self.signal_show_QMessageBox.emit(["错误", "参数错误"])
            # MessageBox().showMessage("错误", "请选择策略！")
            dict_args = {"title": "消息", "main": "请选择策略！"}
            self.signal_show_alert.emit(dict_args)
            return
        if len(self.lineEdit_zongshou.text()) == 0 or len(self.lineEdit_meifen.text()) == 0:
            # self.signal_show_QMessageBox.emit(["错误", "参数错误"])
            # MessageBox().showMessage("错误", "总手、每份参数错误！")
            dict_args = {"title": "消息", "main": "总手、每份参数错误！"}
            self.signal_show_alert.emit(dict_args)
            return
        if int(self.lineEdit_zongshou.text()) <= 0:  # 正确值：总手大于零的整数
            # self.signal_show_QMessageBox.emit(["错误", "‘总手’必须为大于零的整数"])
            dict_args = {"title": "消息", "main": "‘总手’必须为大于零的整数！"}
            self.signal_show_alert.emit(dict_args)
            return
        elif int(self.lineEdit_meifen.text()) <= 0:  # 正确值：每份大于零的整数
            # self.signal_show_QMessageBox.emit(["错误", "‘每份’必须为大于零的整数"])
            dict_args = {"title": "消息", "main": "‘每份’必须为大于零的整数"}
            self.signal_show_alert.emit(dict_args)
            return
        elif int(self.lineEdit_zongshou.text()) < int(self.lineEdit_meifen.text()):  # 正确值：每份小于总手
            # self.signal_show_QMessageBox.emit(["错误", "‘总手’必须大于‘每份’"])
            dict_args = {"title": "消息", "main": "‘总手’必须大于‘每份’"}
            self.signal_show_alert.emit(dict_args)
            return
        elif int(self.lineEdit_Achedanxianzhi.text()) <= 0:  # 正确值：A撤单次数限制必须大于0
            dict_args = {"title": "消息", "main": "‘A限制’必须大于0"}
            self.signal_show_alert.emit(dict_args)
            return
        elif int(self.lineEdit_Bchedanxianzhi.text()) <= 0:  # 正确值：B撤单次数限制必须大于0
            dict_args = {"title": "消息", "main": "‘B限制’必须大于0"}
            self.signal_show_alert.emit(dict_args)
            return
        elif self.doubleSpinBox_kongtoukai.value() <= self.doubleSpinBox_kongtouping.value():  # 正确值：空头开 > 空头平
            # self.signal_show_QMessageBox.emit(["错误", "‘空头开’必须大于‘空头平’"])
            dict_args = {"title": "消息", "main": "‘空头开’必须大于‘空头平’"}
            self.signal_show_alert.emit(dict_args)
            return
        elif self.doubleSpinBox_duotoukai.value() >= self.doubleSpinBox_duotouping.value():  # 正确值：多头开 < 多头平
            # self.signal_show_QMessageBox.emit(["警告", "‘多头开’必须小于‘多头平’"])
            dict_args = {"title": "消息", "main": "‘多头开’必须小于‘多头平’"}
            self.signal_show_alert.emit(dict_args)
            return

    @pyqtSlot()
    def on_pushButton_set_strategy_clicked(self):
        # print(">>> QAccountWidget.on_pushButton_set_strategy_clicked() called")
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        self.arguments_examine()  # 参数排错

        # "sell_open": self.doubleSpinBox_kongtoukai.value(),  # 价差卖开触发参数
        # "buy_close": self.doubleSpinBox_kongtouping.value(),  # 价差买平触发参数
        # "sell_close": self.doubleSpinBox_duotouping.value(),  # 价差卖平触发参数
        # "buy_open": self.doubleSpinBox_duotoukai.value(),  # 价差买开触发参数
        if len(self.lineEdit_celuebianhao.text()) == 0:
            dict_args = {"title": "消息", "main": "请先选择策略！"}
            self.signal_show_alert.emit(dict_args)
            return
        if self.doubleSpinBox_kongtoukai.value() <= self.doubleSpinBox_kongtouping.value():
            # MessageBox().showMessage("错误", "卖开触发参数必须大于买平触发参数！")
            dict_args = {"title": "消息", "main": "卖开触发参数必须大于买平触发参数！"}
            self.signal_show_alert.emit(dict_args)
            return
        if self.doubleSpinBox_duotouping.value() <= self.doubleSpinBox_duotoukai.value():
            # MessageBox().showMessage("错误", "买开触发参数必须小于卖平触发参数！")
            dict_args = {"title": "消息", "main": "买开触发参数必须小于卖平触发参数！"}
            self.signal_show_alert.emit(dict_args)
            return

        dict_args = {
            "MsgRef": self.__socket_manager.msg_ref_add(),
            "MsgSendFlag": 0,  # 发送标志，客户端发出0，服务端发出1
            "MsgType": 5,  # 修改单条策略持仓
            "TraderID": self.__socket_manager.get_trader_id(),  # trader_id
            "UserID": self.lineEdit_qihuozhanghao.text(),  # user_id
            "StrategyID": self.lineEdit_celuebianhao.text(),  # strategy_id
            "MsgSrc": 0,
            "Info": [{
                "trader_id": self.__socket_manager.get_trader_id(),  # trader_id
                "user_id": self.lineEdit_qihuozhanghao.text(),  # user_id
                "strategy_id": self.lineEdit_celuebianhao.text(),  # strategy_id
                # "on_off": # 策略开关int，1开、0关
                "trade_model": self.comboBox_jiaoyimoxing.currentText(),  # 交易模型
                "order_algorithm": self.comboBox_xiadansuanfa.currentText(),  # 下单算法
                "instrument_a_scale": int(self.lineEdit_Achengshu.text()),  # A合约乘数
                "instrument_b_scale": int(self.lineEdit_Bchengshu.text()),  # B合约乘数
                "lots": int(self.lineEdit_zongshou.text()),  # 总手
                "lots_batch": int(self.lineEdit_meifen.text()),  # 每份
                "stop_loss": float(self.spinBox_zhisun.text()),  # 止损跳数
                "spread_shift": float(self.spinBox_rangjia.text()),  # 超价发单跳数
                "a_limit_price_shift": int(self.spinBox_Abaodanpianyi.text()),  # A报单偏移
                "b_limit_price_shift": int(self.spinBox_Bbaodanpianyi.text()),  # B报单偏移
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
        # json_StrategyEditWithoutPosition = json.dumps(dict_args)
        # self.__client_main.signal_send_msg.emit(json_StrategyEditWithoutPosition)
        print(">>> QAccountWidget.on_pushButton_set_strategy_clicked() dict_args =", dict_args)
        self.signal_send_msg.emit(dict_args)  # 发送信号到SocketManager.slot_send_msg

    @pyqtSlot()
    def on_pushButton_set_position_clicked(self):
        # print(">>> QAccountWidget.on_pushButton_set_position_clicked() widget_name=", self.__widget_name, "self.pushButton_set_position.text()=", self.pushButton_set_position.text())

        # 策略开关为“开”时不能修改策略，弹窗提示，并return
        print(">>> QAccountWidget.on_pushButton_set_position_clicked() self.get_clicked_strategy_on_off() =", self.get_clicked_strategy_on_off())
        if self.get_clicked_strategy_on_off() == 1:
            # MessageBox().showMessage("错误", "策略运行时不允许修改持仓！")
            dict_args = {"title": "消息", "main": "策略运行时不允许修改持仓"}
            self.signal_show_alert.emit(dict_args)
            return

        # 参数排错：期货账号、策略编号不能为空
        if len(self.lineEdit_qihuozhanghao.text()) == 0 or len(self.lineEdit_celuebianhao.text()) == 0:
            print(">>> QAccountWidget.on_pushButton_set_position_clicked() 期货账号或策略编号为空")
            return
        # 参数排错：用户想要设置的持仓必须小于策略运行中的持仓
        # user_id = self.lineEdit_qihuozhanghao.text()  # user_id
        # strategy_id = self.lineEdit_celuebianhao.text()  # strategy_id
        position_a_buy = int(self.lineEdit_Azongbuy.text())  # A总买
        position_a_buy_today = int(self.lineEdit_Azongbuy.text()) - int(self.lineEdit_Azuobuy.text())  # A今买
        position_a_buy_yesterday = int(self.lineEdit_Azuobuy.text())  # A昨买
        position_a_sell = int(self.lineEdit_Azongsell.text())  # A总卖
        position_a_sell_today = int(self.lineEdit_Azongsell.text()) - int(self.lineEdit_Azuosell.text())  # A今卖
        position_a_sell_yesterday = int(self.lineEdit_Azuosell.text())  # A昨卖
        position_b_buy = int(self.lineEdit_Bzongbuy.text())  # B总买
        position_b_buy_today = int(self.lineEdit_Bzongbuy.text()) - int(self.lineEdit_Bzuobuy.text())  # B今买
        position_b_buy_yesterday = int(self.lineEdit_Bzuobuy.text())  # B昨买
        position_b_sell = int(self.lineEdit_Bzongsell.text())  # B总卖
        position_b_sell_today = int(self.lineEdit_Bzongsell.text()) - int(self.lineEdit_Bzuosell.text())  # B今卖
        position_b_sell_yesterday = int(self.lineEdit_Bzuosell.text())  # B昨卖
        list_update_group_box_data = self.get_list_update_group_box_data()  # 获取显示到groupBox中的内核数据
        if position_a_buy > int(list_update_group_box_data[32]) and position_a_buy != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_a_buy_yesterday > int(list_update_group_box_data[33]) and position_a_buy_yesterday != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_a_buy_today > int(list_update_group_box_data[32]) - int(list_update_group_box_data[32]) != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_a_sell > int(list_update_group_box_data[30]) and position_a_sell != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_a_sell_yesterday > int(list_update_group_box_data[31]) and position_a_sell_yesterday != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_a_sell_today > int(list_update_group_box_data[30]) - int(list_update_group_box_data[31]) and position_a_sell_today != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_b_buy > int(list_update_group_box_data[6]) and position_b_buy != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_b_buy_yesterday > int(list_update_group_box_data[35]) and position_b_buy_yesterday != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_b_buy_today > int(list_update_group_box_data[6]) - int(list_update_group_box_data[35]) and position_b_buy_today != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_b_sell > int(list_update_group_box_data[5]) and position_b_sell != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_b_sell_yesterday > int(list_update_group_box_data[34]) and position_b_sell_yesterday != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return
        if position_b_sell_today > int(list_update_group_box_data[5]) - int(list_update_group_box_data[34]) and position_b_sell_today != 0:
            # MessageBox().showMessage("错误", "修改持仓不得大于策略持仓量")
            dict_args = {"title": "消息", "main": "修改持仓不得大于策略持仓量"}
            self.signal_show_alert.emit(dict_args)
            return

        if self.pushButton_set_position.text() == "设置持仓":
            self.pushButton_set_position.setText("发送持仓")  # 修改按钮显示的字符
            # 解禁仓位显示lineEdit，允许编辑
            self.lineEdit_Azongbuy.setReadOnly(False)  # 文本框允许编辑
            self.lineEdit_Azongbuy.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.lineEdit_Azuobuy.setReadOnly(False)
            self.lineEdit_Azuobuy.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.lineEdit_Azongsell.setReadOnly(False)
            self.lineEdit_Azongsell.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.lineEdit_Azuosell.setReadOnly(False)
            self.lineEdit_Azuosell.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.lineEdit_Bzongbuy.setReadOnly(False)
            self.lineEdit_Bzongbuy.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.lineEdit_Bzuobuy.setReadOnly(False)
            self.lineEdit_Bzuobuy.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.lineEdit_Bzongsell.setReadOnly(False)
            self.lineEdit_Bzongsell.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.lineEdit_Bzuosell.setReadOnly(False)
            self.lineEdit_Bzuosell.setStyleSheet("QLineEdit { background: rgb(221, 255, 221);}")
            self.set_allow_update_group_box_position(False)  # 允许刷新groupBox中的持仓变量LineEdit为False
        elif self.pushButton_set_position.text() == "发送持仓":
            # self.pushButton_set_position.setText("设置持仓")  # 修改按钮显示的字符
            self.lineEdit_Azongsell.setReadOnly(True)  # 文本框只读
            self.lineEdit_Azongsell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.lineEdit_Azuosell.setReadOnly(True)
            self.lineEdit_Azuosell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.lineEdit_Bzongbuy.setReadOnly(True)
            self.lineEdit_Bzongbuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.lineEdit_Bzuobuy.setReadOnly(True)
            self.lineEdit_Bzuobuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.lineEdit_Azongbuy.setReadOnly(True)
            self.lineEdit_Azongbuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.lineEdit_Azuobuy.setReadOnly(True)
            self.lineEdit_Azuobuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.lineEdit_Bzongsell.setReadOnly(True)
            self.lineEdit_Bzongsell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.lineEdit_Bzuosell.setReadOnly(True)
            self.lineEdit_Bzuosell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
            self.pushButton_set_position.setEnabled(False)  # 禁用按钮
            dict_setPosition = {
                "MsgRef": self.__socket_manager.msg_ref_add(),
                "MsgSendFlag": 0,  # 发送标志，客户端发出0，服务端发出1
                "MsgType": 12,  # 修改单条策略持仓
                "TraderID": self.__socket_manager.get_trader_id(),  # trader_id
                "UserID": self.lineEdit_qihuozhanghao.text(),  # user_id
                "StrategyID": self.lineEdit_celuebianhao.text(),  # strategy_id
                "MsgSrc": 0,
                "Info": [{
                    "trader_id": self.__socket_manager.get_trader_id(),  # trader_id
                    "user_id": self.lineEdit_qihuozhanghao.text(),  # user_id
                    "strategy_id": self.lineEdit_celuebianhao.text(),  # strategy_id
                    "position_a_buy": int(self.lineEdit_Azongbuy.text()),  # A总买
                    "position_a_buy_today": int(self.lineEdit_Azongbuy.text()) - int(self.lineEdit_Azuobuy.text()),  # A今买
                    "position_a_buy_yesterday": int(self.lineEdit_Azuobuy.text()),  # A昨买
                    "position_a_sell": int(self.lineEdit_Azongsell.text()),  # A总卖
                    "position_a_sell_today": int(self.lineEdit_Azongsell.text()) - int(self.lineEdit_Azuosell.text()),  # A今卖
                    "position_a_sell_yesterday": int(self.lineEdit_Azuosell.text()),  # A昨卖
                    "position_b_buy": int(self.lineEdit_Bzongbuy.text()),  # B总买
                    "position_b_buy_today": int(self.lineEdit_Bzongbuy.text()) - int(self.lineEdit_Bzuobuy.text()),  # B今买
                    "position_b_buy_yesterday": int(self.lineEdit_Bzuobuy.text()),  # B昨买
                    "position_b_sell": int(self.lineEdit_Bzongsell.text()),  # B总卖
                    "position_b_sell_today": int(self.lineEdit_Bzongsell.text()) - int(self.lineEdit_Bzuosell.text()),  # B今卖
                    "position_b_sell_yesterday": int(self.lineEdit_Bzuosell.text())  # B昨卖
                }]
            }
            # json_setPosition = json.dumps(dict_setPosition)
            self.signal_send_msg.emit(dict_setPosition)  # 发送信号到SocketManager.slot_send_msg

    # 激活设置持仓按钮，禁用仓位输入框
    @QtCore.pyqtSlot()
    def on_pushButton_set_position_active(self):
        # print(">>> QAccountWidget.on_pushButton_set_position_active() called")
        self.set_allow_update_group_box_position(False)  # 允许刷新groupBox中的持仓变量LineEdit为False
        self.lineEdit_Azongsell.setReadOnly(True)  # 文本框只读
        self.lineEdit_Azongsell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Azuosell.setReadOnly(True)
        self.lineEdit_Azuosell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzongbuy.setReadOnly(True)
        self.lineEdit_Bzongbuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzuobuy.setReadOnly(True)
        self.lineEdit_Bzuobuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Azongbuy.setReadOnly(True)
        self.lineEdit_Azongbuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Azuobuy.setReadOnly(True)
        self.lineEdit_Azuobuy.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzongsell.setReadOnly(True)
        self.lineEdit_Bzongsell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
        self.lineEdit_Bzuosell.setReadOnly(True)
        self.lineEdit_Bzuosell.setStyleSheet("QLineEdit { background: rgb(255, 255, 245);}")
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
        # 单账户窗口中查询单账户的所有策略，总账户窗口中查询所有期货账户策略
        # str_user_id = self.__widget_name if self.is_single_user_widget() else ''
        str_user_id = self.lineEdit_qihuozhanghao.text()
        str_strategy_id = self.lineEdit_celuebianhao.text()
        if len(str_user_id) == 0 or len(str_strategy_id) == 0:
            # MessageBox().showMessage("消息", "请先选中要查询的策略")
            dict_args = {"title": "消息", "main": "请先选中要查询的策略"}
            self.signal_show_alert.emit(dict_args)
            return
        self.pushButton_query_strategy.setEnabled(False)  # 点击按钮之后禁用，等收到消息后激活
        dict_query_strategy = {'MsgRef': self.__socket_manager.msg_ref_add(),
                               'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                               'MsgSrc': 0,  # 消息源，客户端0，服务端1
                               'MsgType': 22,  # 查询策略，查询特定单个策略
                               'TraderID': self.__socket_manager.get_trader_id(),
                               'UserID': str_user_id,
                               'StrategyID': str_strategy_id}
        # json_query_strategy = json.dumps(dict_query_strategy)
        self.signal_send_msg.emit(dict_query_strategy)

        # 测试用：触发保存df_order和df_trade保存到本地
        # 进程间通信，触发特殊指令：保存策略的OnRtnOrder和OnRtnTrade到本地
        # dict_Queue_main = self.__socket_manager.get_dict_Queue_main()
        # for user_id in dict_Queue_main:
        #     buff = {"MsgType": 91, "PrintListPoisitionDetail": 1, 'UserID': }
        #     dict_Queue_main[user_id].put(buff)
        # 给特定user子进程发送消息
        buff = {"UserID": str_user_id, "StrategyID": str_strategy_id, "MsgType": 91, "PrintListPoisitionDetail": 1}
        dict_Queue_main = self.__socket_manager.get_dict_Queue_main()
        dict_Queue_main[str_user_id].put(buff)
        self.__socket_manager.print_strategy_data(str_user_id, str_strategy_id)  # soketManager输出特定策略的变量，输出格式如下
        # A总卖 0 A昨卖 0
        # B总买 0 B昨卖 0
        # A总买 0 A昨买 0
        # B总卖 0 B昨卖 0

    # 激活“查询”按钮
    def slot_activate_query_strategy_pushbutton(self):
        self.pushButton_query_strategy.setEnabled(True)
        self.slot_tab_changed(self.__current_tab_index)  # 主动触发一次tab_changed操作，目的更新界面全部元素
        # print(">>> QAccountWidget.slot_activate_query_strategy_pushbutton() 主动触发一次tab_changed操作，目的更新界面全部元素")

    @pyqtSlot(bool)
    def on_checkBox_kongtoukai_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        # raise NotImplementedError

    @pyqtSlot(QModelIndex)
    def on_tableView_Trade_Args_clicked(self, index):
        """
        Slot documentation goes here.

        @param index DESCRIPTION
        @type QModelIndex
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        row = index.row()
        column = index.column()
        self.__clicked_user_id = self.tableView_Trade_Args.model().index(row, 1).data()
        self.__clicked_strategy_id = self.tableView_Trade_Args.model().index(row, 2).data()
        str_on_off = self.tableView_Trade_Args.model().index(row, 0).data()
        if str_on_off == '开':
            self.__clicked_strategy_on_off = 1
        else:
            self.__clicked_strategy_on_off = 0
        # print(">>> QAccountWidget.on_tableView_Trade_Args_clicked() self.__clicked_strategy_on_off =", self.__clicked_strategy_on_off)
        self.__dict_clicked_info[self.__current_tab_name] = {'user_id': self.__clicked_user_id,
                                                             'strategy_id': self.__clicked_strategy_id,
                                                             'row': row,
                                                             'column': column,
                                                             'strategy_on_off': self.__clicked_strategy_on_off}

        # print(">>> QAccountWidget.on_tableView_Trade_Args_clicked() self.__dict_clicked_info =", self.__dict_clicked_info)
        self.__socket_manager.set_clicked_info(row, column, self.__clicked_user_id, self.__clicked_strategy_id)
        self.get_list_update_group_box_data()  # 获取最新groupBox的更新数据
        # a_instrument_id = self.__list_update_group_box_data[3][:6]
        # b_instrument_id = self.__list_update_group_box_data[3][7:]
        a_instrument_id = self.__list_update_group_box_data[45]
        b_instrument_id = self.__list_update_group_box_data[46]
        list_instrument_id = [a_instrument_id, b_instrument_id]
        # self.__socket_manager.get_market_manager().group_box_sub_market(list_instrument_id)
        self.__clicked_list_instrument_id = list_instrument_id
        self.__Queue_sub_instrument.put(list_instrument_id)
        self.slot_update_group_box()

    @pyqtSlot(QModelIndex)
    def on_tableView_Trade_Args_activated(self, index):
        """
        Slot documentation goes here.

        @param index DESCRIPTION
        @type QModelIndex
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        pass

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
        # print(">>> QAccountWidget.on_comboBox_qihuozhanghao_currentIndexChanged()")

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
        self.popMenu.exec_(QtGui.QCursor.pos())  # 在鼠标点击位置显示菜单窗口

    # 鼠标右击捕获事件
    @pyqtSlot(QPoint)
    def on_tableView_Trade_Args_customContextMenuRequested(self, pos):
        print("QAccountWidget.on_tableWidget_Trade_Args_customContextMenuRequested() called 鼠标右击捕获事件")
        """
        Slot documentation goes here.

        @param pos DESCRIPTION
        @type QPoint
        """
        # TODO: not implemented yet
        index = self.tableView_Trade_Args.indexAt(pos)
        if index.isValid():
            self.action_del.setDisabled(False)
            self.popMenu.exec_(QtGui.QCursor.pos())  # 在鼠标点击位置显示菜单窗口
        else:
            self.action_del.setDisabled(True)
            self.popMenu.exec_(QtGui.QCursor.pos())  # 在鼠标点击位置显示菜单窗口


    # 找出策略所在的行标，如果不存在该窗口则返回None，存在于该窗口中则返回具体行数int值
    def find_strategy(self, obj_strategy):
        if self.tableWidget_Trade_Args.rowCount() == 0:
            return None  # 窗口中无策略，返回None
        for i_row in range(self.tableWidget_Trade_Args.rowCount()):
            if self.tableWidget_Trade_Args.item(i_row, 2).text() == obj_strategy.get_user_id()  \
                    and self.tableWidget_Trade_Args.item( i_row, 3).text() == obj_strategy.get_strategy_id():
                return i_row  # 返回策略在窗口中的函数
        return None  # 策略不属于该窗口，返回None

    # 设置窗口鼠标点击到形参中策略，若窗口中不存在该策略则跳出
    @pyqtSlot(int, int)
    def set_on_tableWidget_Trade_Args_cellClicked(self, i_row, i_column):
        print("QAccountWidget.set_on_tableWidget_Trade_Args_cellClicked() self.sender()=", self.sender(), "widget_name=", self.__widget_name)
        if self.tableWidget_Trade_Args.rowCount() > 0:
            self.on_tableWidget_Trade_Args_cellClicked(i_row, i_column)

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
        # 设置鼠标点击触发的设置属性
        # self.__clicked_item = self.tableWidget_Trade_Args.item(row, column)  # 局部变量，鼠标点击的item设置为QAccountWidget的属性
        # self.__client_main.set_clicked_item(self.__clicked_item)  # 全局变量，鼠标点击的item设置为ClientMain的属性，全局唯一
        # self.__clicked_status = {'row': row, 'column': column, 'widget_name': self.__widget_name, 'user_id': self.tableWidget_Trade_Args.item(row, 1).text(), 'strategy_id': self.tableWidget_Trade_Args.item(row, 2).text()}
        # self.__client_main.set_clicked_status(self.__clicked_status)  # 保存鼠标点击状态到ClientMain的属性，保存全局唯一一个鼠标最后点击位置
        self.__clicked_user_id = self.tableWidget_Trade_Args.item(row, 1).text()
        self.__clicked_strategy_id = self.tableWidget_Trade_Args.item(row, 2).text()
        self.tableWidget_Trade_Args.setCurrentCell(row, column)  # 设置当前Cell
        print(">>> QAccountWidget.on_tableWidget_Trade_Args_cellClicked() self.__clicked_user_id =", self.__clicked_user_id, "self.__clicked_strategy_id =", self.__clicked_strategy_id)
        self.__dict_clicked_info[self.__current_tab_name] = {'user_id': self.__clicked_user_id,
                                                             'strategy_id': self.__clicked_strategy_id,
                                                             'row': row}
        self.update_groupBox()  # 更新界面groupBox

        """
        # 找到鼠标点击的策略对象
        for i_strategy in self.__list_strategy:
            print(">>> i_strategy.get_user_id() == self.__clicked_status['user_id'] and i_strategy.get_strategy_id() == self.__clicked_status['strategy_id'] ", i_strategy.get_user_id(), self.__clicked_status['user_id'], i_strategy.get_strategy_id(), self.__clicked_status['strategy_id'])
            if i_strategy.get_user_id() == self.__clicked_status['user_id'] \
                    and i_strategy.get_strategy_id() == self.__clicked_status['strategy_id']:
                self.__client_main.set_clicked_strategy(i_strategy)  # 全局变量，鼠标点击的策略对象设置为ClientMain属性
                self.__clicked_strategy = i_strategy  # 局部变量，鼠标点击的策略对象设置为QAccountWidget属性
                break
        print("QAccountWidget.on_tableWidget_Trade_Args_cellClicked() widget_name=", self.__widget_name, "鼠标点击位置=row %d, column %d" % (row, column), "值=", self.__clicked_item.text(), "user_id=", self.__clicked_strategy.get_user_id(), "strategy_id=", self.__clicked_strategy.get_strategy_id())

        # 监测交易开关、只平开关变化，并触发修改指令
        if self.__ctp_manager.get_init_UI_finished():
            self.tableWidget_Trade_Args.setCurrentItem(self.__clicked_item)
            # 判断策略开关item的checkState()状态变化
            if column == 0:
                # checkState值与内核值不同，则发送修改指令
                on_off_checkState = 0 if self.__clicked_item.checkState() == 0 else 1
                # print(">>> QAccountWidget.on_tableWidget_Trade_Args_cellClicked()", on_off_checkState, self.__client_main.get_clicked_strategy().get_on_off())
                if on_off_checkState != self.__client_main.get_clicked_strategy().get_on_off():
                    self.__clicked_item.setFlags(self.__clicked_item.flags() & (~QtCore.Qt.ItemIsEnabled))  # 设置当前item的状态属性(与操作)
                    self.__item_on_off_status = {'widget_name': self.__widget_name,
                                                 'user_id': self.tableWidget_Trade_Args.item(row, 2).text(),
                                                 'strategy_id': self.tableWidget_Trade_Args.item(row, 3).text(),
                                                 'enable': 0}  # enable值为1启用、0禁用
                    dict_strategy_onoff = {
                        'MsgRef': self.__socket_manager.msg_ref_add(),
                        'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                        'MsgSrc': 0,  # 消息源，客户端0，服务端1
                        'MsgType': 13,  # 策略交易开关
                        'TraderID': self.__ctp_manager.get_trader_id(),
                        'UserID': self.__clicked_strategy.get_user_id(),
                        'StrategyID': self.__clicked_strategy.get_strategy_id(),
                        'OnOff': on_off_checkState  # 0关、1开
                        }
                    # print(">>> QAccountWidget.on_tableWidget_Trade_Args_cellClicked() 发送“开关”修改指令", dict_strategy_onoff)
                    json_strategy_onoff = json.dumps(dict_strategy_onoff)
                    self.signal_send_msg.emit(json_strategy_onoff)
            # 判断策略只平item的checkState()状态变化
            elif column == 1:
                only_close_checkState = 0 if self.__clicked_item.checkState() == 0 else 1
                if only_close_checkState != self.__client_main.get_clicked_strategy().get_only_close():
                    self.__clicked_item.setFlags(self.__clicked_item.flags() & (~QtCore.Qt.ItemIsEnabled))  # 设置当前item的状态属性(与操作)
                    self.__item_only_close_status = {'widget_name': self.__widget_name,
                                                     'user_id': self.tableWidget_Trade_Args.item(row, 2).text(),
                                                     'strategy_id': self.tableWidget_Trade_Args.item(row, 3).text(),
                                                     'enable': 0}  # enable值为1启用、0禁用
                    dict_strategy_only_close = {
                        'MsgRef': self.__socket_manager.msg_ref_add(),
                        'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                        'MsgSrc': 0,  # 消息源，客户端0，服务端1
                        'MsgType': 14,  # 策略只平开关
                        'TraderID': self.__ctp_manager.get_trader_id(),
                        'UserID': self.__clicked_strategy.get_user_id(),
                        'StrategyID': self.__clicked_strategy.get_strategy_id(),
                        'OnOff': only_close_checkState  # 0关、1开
                        }
                    print(">>> QAccountWidget.on_tableWidget_Trade_Args_cellClicked() 发送“只平”修改指令", dict_strategy_only_close)
                    json_strategy_only_close = json.dumps(dict_strategy_only_close)
                    self.signal_send_msg.emit(json_strategy_only_close)

        # 设置所有策略的属性，策略在当前窗口中是否被选中
        if self.is_single_user_widget():  # 单账户窗口
            # if i_strategy.get_user_id() == self.__clicked_status['user_id'] and i_strategy.get_strategy_id() == self.__clicked_status['strategy_id']:
            #     i_strategy.set_clicked_signal(True)
            #     # print(">>> QAccountWidget.on_tableWidget_Trade_Args_cellClicked() 鼠标点击单账户窗口，user_id=", i_strategy.get_user_id(), "strategy_id=", i_strategy.get_strategy_id())
            # else:
            #     i_strategy.set_clicked_signal(False)
            # if i_strategy == self.__clicked_strategy:
            #     i_strategy.set_clicked_signal(True)
            # else:
            #     i_strategy.set_clicked_signal(False)
            for i_strategy in self.__list_strategy:
                i_strategy.set_clicked_signal(True if i_strategy == self.__clicked_strategy else False)
        else:  # 总账户窗口
            # if i_strategy.get_user_id() == self.__clicked_status['user_id'] and i_strategy.get_strategy_id() == self.__clicked_status['strategy_id']:
            #     i_strategy.set_clicked_total(True)
            #     # print(">>> QAccountWidget.on_tableWidget_Trade_Args_cellClicked() 鼠标点击总账户窗口，user_id=", i_strategy.get_user_id(), "strategy_id=", i_strategy.get_strategy_id())
            # else:
            #     i_strategy.set_clicked_total(False)
            for i_strategy in self.__list_strategy:
                i_strategy.set_clicked_total(True if i_strategy == self.__clicked_strategy else False)

        self.slot_update_strategy(self.__clicked_strategy)  # 更新策略所有变量在界面的显示（包含tableWidget和groupBox）
        # self.slot_update_strategy_position(self.__clicked_strategy)  # 更新策略持仓在界面的显示（包含tableWidget和groupBox）
        """

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
        pass




# if __name__ == "__main__":
#     import sys
#     app = QtGui.QApplication(sys.argv)
#     Form = QAccountWidget()
#     Form.show()
#
#     #设置tablewidget的行数
#     Form.tableWidget_Trade_Args.setRowCount(5)
#     # print("0 header name %s, %d ttttttttt" % (Form.tableWidget_Trade_Args.horizontalHeaderItem(0).text(), 2))
#
#     #创建QTableWidgetItem
#     for i in range(13):
#         item = QtGui.QTableWidgetItem()
#         item.setText("hello: %d你好" % i)
#         if i == 0:
#             item.setCheckState(False)
#         Form.tableWidget_Trade_Args.setItem(0, i, item)
#
#
#
#     sys.exit(app.exec_())