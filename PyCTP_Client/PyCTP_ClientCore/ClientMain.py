import sys
from CTPManager import CTPManager
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QApplication, QCompleter, QLineEdit, QStringListModel
import QLogin  # from QLogin import QLoginForm
from QCTP import QCTP
from QAccountWidget import QAccountWidget
from QStrategySetting import NewStrategy
from SocketManager import SocketManager
import json
import Utils
import time
import threading
from MarketManager import MarketManager
from Trader import Trader
from User import User
from Strategy import Strategy


class ClientMain(QtCore.QObject):
    signal_send_msg = QtCore.pyqtSignal(str)  # 定义信号：发送到服务端的json格式数据
    signal_pushButton_query_strategy_setEnabled = QtCore.pyqtSignal(bool)  # 定义信号：控制查询是否可用
    signal_pushButton_set_position_setEnabled = QtCore.pyqtSignal()  # 定义信号：按钮设置为可用

    def __init__(self, parent=None):
        super(ClientMain, self).__init__(parent)  # 显示调用父类初始化方法，使用其信号槽机制
        self.__list_QAccountWidget = list()  # 存放账户窗口
        self.__create_QAccountWidget_finished = False  # 窗口创建完成
        self.__showEvent = False  # 有任何一个QAccountWidget窗口显示

    def set_SocketManager(self, obj_sm):
        self.__sm = obj_sm
        self.__sm.signal_send_message.connect(self.slot_output_message)  # 绑定信号槽函数:
        self.signal_send_msg.connect(self.__sm.send_msg)  # 绑定信号槽函数

    def set_QLoginForm(self, qloginform):
        self.__QLoginForm = qloginform

    def set_QCTP(self, obj_QCTP):
        self.__QCTP = obj_QCTP

    def set_QAccountWidget(self, obj_QAccountWidget):
        self.__QAccoutWidget = obj_QAccountWidget

    def set_dict_QAccountWidget(self, dict_QAccountWidget):
        self.__dict_QAccountWidget = dict_QAccountWidget

    def set_QOrderWidget(self, obj_QOrderWidget):
        self.__QOrderWidget = obj_QOrderWidget

    def set_CTPManager(self, obj_CTPManager):
        self.__CTPManager = obj_CTPManager

    # 设置当前显示在最前端窗口对象为本类属性
    def set_showQAccountWidget(self, obj_QAccountWidget):
        self.__showQAccountWidget = obj_QAccountWidget
        # 绑定信号：当前最前端窗口对象(通过信槽绑定的标志来判断，不能重复绑定信号槽)
        if self.__showQAccountWidget.get_signal_pushButton_set_position_setEnabled_connected() is False:
            self.signal_pushButton_set_position_setEnabled.connect(self.__showQAccountWidget.on_pushButton_set_position_active)  # , QtCore.Qt.UniqueConnection
            self.__showQAccountWidget.set_signal_pushButton_set_position_setEnabled_connected(True)  # 信号槽绑定状态设置为True
            # print(">>> ClientMain.set_showQAccountWidget() 绑定信号槽，widget_name=", self.__showQAccountWidget.get_widget_name())

    def get_showQAccountWidget(self):
        return self.__showQAccountWidget

    def set_hideQAccountWidget(self, obj_QAccountWidget):
        self.__hideQAccountWidget = obj_QAccountWidget
        # 解绑信号：隐藏的窗口
        if self.__hideQAccountWidget.get_signal_pushButton_set_position_setEnabled_connected():
            self.signal_pushButton_set_position_setEnabled.disconnect(self.__hideQAccountWidget.on_pushButton_set_position_active)
            self.__hideQAccountWidget.set_signal_pushButton_set_position_setEnabled_connected(False)  # 信号槽绑定状态设置为False
            # print(">>> ClientMain.set_hideQAccountWidget() 解绑信号槽，widget_name=", self.__hideQAccountWidget.get_widget_name())

    def get_hideQAccountWidget(self):
        return self.__hideQAccountWidget

    def create_QAccountWidget(self):
        print(">>> ClientMain.create_QAccountWidget() CTPManager内核初始化完成，开始创建窗口")

        # 创建总账户窗口，将user对象列表设置为其属性，将窗口对象存放到list里，总账户窗口初始化函数内部将总账户窗口对象设置为各user对象的属性。
        tmpQ = QAccountWidget(str_widget_name='总账户', list_user=self.get_CTPManager().get_list_user(), ClientMain=self)
        # tmpQ.set_ClientMain(self)  # ClientMain设置为窗口对象的属性
        # 总账户窗口实例设置为所有策略的属性
        for i_strategy in self.get_CTPManager().get_list_strategy():
            i_strategy.set_QAccountWidgetTotal(tmpQ)
        tmpQ.init_table_widget()  # 初始化界面：策略列表，tableWidget_Trade_Args
        self.__list_QAccountWidget.append(tmpQ)  # 将窗口对象存放到list集合里
        self.signal_pushButton_set_position_setEnabled.connect(tmpQ.on_pushButton_set_position_active)  # , QtCore.Qt.UniqueConnection
        tmpQ.set_signal_pushButton_set_position_setEnabled_connected(True)  # 信号槽绑定标志设置为True

        # 创建单个账户窗口，将user对象设置为其属性，将窗口对象存放到list里
        for i_user in self.get_CTPManager().get_list_user():
            tmpQ = QAccountWidget(str_widget_name=i_user.get_user_id().decode(),
                                  obj_user=i_user,
                                  ClientMain=self)  # 创建窗口，并将user设置为其属性
            i_user.set_QAccountWidget(tmpQ)  # 窗口实例设置为user的对象
            # tmpQ.set_ClientMain(self)  # ClientMain这是为窗口的属性
            # 单账户窗口实例设置为对应期货账户下面所有策略的属性
            for i_strategy in tmpQ.get_user().get_list_strategy():
                i_strategy.set_QAccountWidget(tmpQ)
            tmpQ.init_table_widget()  # 初始化界面：策略列表，tableWidget_Trade_Args
            self.__list_QAccountWidget.append(tmpQ)  # 将窗口对象存放到list集合里
            self.signal_pushButton_set_position_setEnabled.connect(tmpQ.on_pushButton_set_position_active)  # , QtCore.Qt.UniqueConnection
            tmpQ.set_signal_pushButton_set_position_setEnabled_connected(True)  # 信号槽绑定标志设置为True

        # 账户窗口创建完成，账户窗口添加到QCTP窗口的tab
        for i in self.__list_QAccountWidget:
            self.get_QCTP().tab_accounts.addTab(i, i.get_widget_name())
            self.signal_pushButton_query_strategy_setEnabled.connect(i.pushButton_query_strategy.setEnabled)
            i.signal_update_groupBox_trade_args_for_query.connect(i.update_groupBox_trade_args_for_query)
            self.__CTPManager.signal_insert_row_table_widget.connect(i.insert_row_table_widget)
            self.__CTPManager.signal_remove_row_table_widget.connect(i.remove_row_table_widget)

        # 创建“新建策略”弹窗
        q_new_strategy = NewStrategy()
        completer = QCompleter()
        model = QStringListModel()
        model.setStringList(self.__CTPManager.get_list_instrument_id())
        completer.setModel(model)
        q_new_strategy.lineEdit_a_instrument.setCompleter(completer)
        q_new_strategy.lineEdit_b_instrument.setCompleter(completer)
        q_new_strategy.set_ClientMain(self)  # ClientMain设置为其属性
        self.set_QNewStrategy(q_new_strategy)  # 设置为ClientMain属性
        self.__CTPManager.signal_hide_new_strategy.connect(self.get_QNewStrategy().hide)  # 绑定信号槽，新创建策略成功后隐藏“新建策略弹窗”

        self.__create_QAccountWidget_finished = True  # 界面初始化完成标志位

        self.__QLoginForm.hide()  # 隐藏登录窗口
        self.__QCTP.show()  # 显示主窗口

        print(">>> ClientMain.create_QAccountWidget() 界面初始化完成")

    def get_SocketManager(self):
        return self.__sm

    def get_QLoginForm(self):
        return self.__QLoginForm

    def get_QCTP(self):
        return self.__QCTP

    def get_QAccoutWidget(self):
        return self.__QAccoutWidget

    def get_QOrderWidget(self):
        return self.__QOrderWidget

    def get_CTPManager(self):
        return self.__CTPManager

    def get_listMarketInfo(self):
        return self.__listMarketInfo

    def get_listUserInfo(self):
        return self.__listUserInfo

    def get_listStrategyInfo(self):
        return self.__listStrategyInfo

    def get_list_QAccountWidget(self):
        return self.__list_QAccountWidget

    def get_listAlgorithmInfo(self):
        return self.__listAlgorithmInfo

    # 设置鼠标点击状态，信息包含:item所在行、item所在列、widget_name、user_id、strategy_id
    def set_clicked_status(self, in_dict):
        self.__clicked_status = in_dict

    def get_clicked_status(self):
        return self.__clicked_status

    # 显示在最前端窗口名称
    def set_show_widget_name(self, str_widget_name):
        self.__show_widget_name = str_widget_name

    def get_show_widget_name(self):
        return self.__show_widget_name

    def get_create_QAccountWidget_finished(self):
        return self.__create_QAccountWidget_finished

    def get_TraderID(self):
        return self.__TraderID

    def get_TraderName(self):
        return self.__TraderName

    def get__TraderName(self):
        return self.__TraderName

    def set_QNewStrategy(self, obj_QNewStrategy):
        self.__QNewStrategy = obj_QNewStrategy

    def get_QNewStrategy(self):
        return self.__QNewStrategy

    # 最后新建的策略设置为其属性
    def set_obj_new_strategy(self, obj_strategy):
        self.__obj_new_strategy = obj_strategy

    def get_obj_new_strategy(self):
        return self.__obj_new_strategy

    # 是否有任何窗口showEvent
    def set_showEvent(self, bool_input):
        self.__showEvent = bool_input

    def get_showEvent(self):
        return self.__showEvent

    # 处理socket_manager发来的消息
    @QtCore.pyqtSlot(dict)
    def slot_output_message(self, buff):
        # 消息源MsgSrc值：0客户端、1服务端
        if buff['MsgSrc'] == 0:  # 由客户端发起的消息类型
            # 内核初始化未完成
            if self.__CTPManager.get_init_finished() is False:
                if buff['MsgType'] == 1:  # 交易员登录验证，MsgType=1
                    print("ClientMain.slot_output_message() MsgType=1", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 验证通过
                        # self.get_QLoginForm().label_login_error.setText(buff['MsgErrorReason'])  # 界面提示信息
                        self.get_QLoginForm().label_login_error.setText('登陆成功，初始化中...')  # 界面提示信息
                        self.__CTPManager.set_trader_id(buff['TraderID'])  # 将TraderID设置为CTPManager的属性
                        self.__CTPManager.set_trader_name(buff['TraderName'])  # 将TraderID设置为CTPManager的属性
                        # self.__CTPManager.create_trader({"trader_id": buff['TraderID'], "trader_name": buff['TraderName']})
                        self.__TraderID = buff['TraderID']
                        self.__TraderName = buff['TraderName']
                        self.QryMarketInfo()  # 查询行情配置
                        # self.__sm.signal_send_message.emit(self.slot_output_message)  # 绑定自定义信号槽
                    elif buff['MsgResult'] == 1:  # 验证不通过
                        self.get_QLoginForm().label_login_error.setText(buff['MsgErrorReason'])  # 界面提示错误信息
                        self.get_QLoginForm().pushButton_login.setEnabled(True)  # 登录按钮激活
                elif buff['MsgType'] == 4:  # 查询行情配置，MsgType=4
                    print("ClientMain.slot_output_message() MsgType=4", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listMarketInfo = buff['Info']  # 转存行情信息到本类的属性里
                        self.QryUserInfo()  # 查询期货账户
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 2:  # 查询期货账户，MsgType=2
                    print("ClientMain.slot_output_message() MsgType=2", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listUserInfo = buff['Info']  # 转存期货账户信息到本类的属性里
                        self.QryAlgorithmInfo()  # 查询下单算法信息
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 11:  # 查询下单算法编号，MsgType=11
                    print("ClientMain.slot_output_message() MsgType=11", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listAlgorithmInfo = buff['Info']  # 转存期货账户信息到本类的属性里
                        self.QryStrategyInfo()  # 查询策略信息
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 3:  # 查询策略，MsgType=3
                    print("ClientMain.slot_output_message() MsgType=3", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listStrategyInfo = buff['Info']  # 转存策略信息到本类的属性里
                        self.QryYesterdayPosition()
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
                elif buff['MsgType'] == 10:  # 查询策略昨仓，MsgType=10
                    print("ClientMain.slot_output_message() MsgType=10", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listYesterdayPosition = buff['Info']  # 所有策略昨仓的list
                        self.__CTPManager.set_YesterdayPosition(buff['Info'])  # 所有策略昨仓的list设置为CTPManager属性
                        if self.__CTPManager.get_init_finished() is False:
                            self.__CTPManager.init()  # 跳转到开始初始化程序，有CTPManager开始初始化
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        pass
            # 内核初始化完成
            elif self.__CTPManager.get_init_finished():
                if buff['MsgType'] == 3:  # 查询策略，MsgType=3
                    print("ClientMain.slot_output_message() MsgType=3", buff)  # 输出错误消息
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.__listStrategyInfoOnce = buff['Info']  # 转存策略信息到本类的属性里(单次查询)
                        # 遍历查询到的消息结果列表
                        for i_Info in self.__listStrategyInfoOnce:
                            # 遍历策略对象列表，将服务器查询到的策略参数传递给策略，并调用set_arguments方法更新内核参数值
                            for i_strategy in self.__CTPManager.get_list_strategy():
                                if i_Info['user_id'] == i_strategy.get_user_id() and i_Info['strategy_id'] == i_strategy.get_strategy_id():
                                    i_strategy.set_arguments(i_Info)  # 将查询参数结果设置到策略内核，所有的策略
                        # 遍历窗口实例，找到显示在最前端的窗口
                        for i_widget in self.__list_QAccountWidget:
                            if i_widget.get_widget_name() == self.get_show_widget_name():
                                # print(">>> 找到显示在最前的窗口， widget_name=", self.get_show_widget_name())
                                # 遍历策略实例
                                for i_strategy in self.__CTPManager.get_list_strategy():
                                    # 找到被鼠标选中的策略
                                    # if i_strategy.get_user_id() == i_widget.get_clicked_status()['user_id'] and i_strategy.get_strategy_id() == i_widget.get_clicked_status()['strategy_id']:
                                    # 找到groupBox中显示的策略
                                    if i_strategy.get_user_id() == i_widget.comboBox_qihuozhanghao.currentText() \
                                            and i_strategy.get_strategy_id() == i_widget.comboBox_celuebianhao.currentText():
                                        # 通过信号槽，将策略参数传递给界面对象，更新参数框
                                        print(">>> ClientMain.slot_output_message() i_strategy.get_arguments()=", i_strategy.get_arguments())
                                        i_widget.signal_update_groupBox_trade_args_for_query.emit(i_strategy.get_arguments())
                                        break
                                break
                        self.signal_pushButton_query_strategy_setEnabled.emit(True)  # 收到消息后将按钮激活
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=3 查询策略失败")
                elif buff['MsgType'] == 6:  # 新建策略，MsgType=6
                    print("ClientMain.slot_output_message() MsgType=6", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        self.get_CTPManager().create_strategy(buff['Info'][0])  # 内核创建策略对象
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() ", buff['MsgErrorReason'])
                elif buff['MsgType'] == 5:  # 修改策略参数，MsgType=5
                    print("ClientMain.slot_output_message() MsgType=5", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        for i_strategy in self.__CTPManager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] \
                                    and i_strategy.get_strategy_id() == buff['StrategyID']:
                                i_strategy.set_arguments(buff['Info'][0])
                            break
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=5 修改策略参数失败")
                elif buff['MsgType'] == 12:  # 修改策略持仓，MsgType=12
                    print("ClientMain.slot_output_message() MsgType=12", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        # 更新内核中的策略持仓
                        for i_strategy in self.__CTPManager.get_list_strategy():
                            if i_strategy.get_user_id() == buff['UserID'] \
                                    and i_strategy.get_strategy_id() == buff['StrategyID']:
                                i_strategy.set_position(buff['Info'][0])
                            break
                        self.signal_pushButton_set_position_setEnabled.emit()  # 激活设置持仓按钮，禁用仓位输入框
                        pass
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=12 修改策略持仓失败")
                elif buff['MsgType'] == 7:  # 删除策略，MsgType=7
                    print("ClientMain.slot_output_message() MsgType=7", buff)
                    if buff['MsgResult'] == 0:  # 消息结果成功
                        dict_args = {'user_id': buff['UserID'], 'strategy_id': buff['StrategyID']}
                        self.__CTPManager.delete_strategy(dict_args)
                    elif buff['MsgResult'] == 1:  # 消息结果失败
                        print("ClientMain.slot_output_message() MsgType=7 删除策略失败")
        elif buff['MsgSrc'] == 1:  # 由服务端发起的消息类型
            pass

    # 查询行情信息
    def QryMarketInfo(self):
        dict_QryMarketInfo = {'MsgRef': self.__sm.msg_ref_add(),
                              'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                              'MsgSrc': 0,  # 消息源，客户端0，服务端1
                              'MsgType': 4,  # 查询行情信息
                              'TraderID': self.__TraderID
                              }
        json_QryMarketInfo = json.dumps(dict_QryMarketInfo)
        self.get_SocketManager().send_msg(json_QryMarketInfo)

    # 查询期货账户
    def QryUserInfo(self):
        dict_QryUserInfo = {'MsgRef': self.__sm.msg_ref_add(),
                            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                            'MsgSrc': 0,  # 消息源，客户端0，服务端1
                            'MsgType': 2,  # 查询期货账户
                            'TraderID': self.__TraderID,
                            'UserID': ''
                            }
        json_QryUserInfo = json.dumps(dict_QryUserInfo)
        self.get_SocketManager().send_msg(json_QryUserInfo)

    # 查询下单算法
    def QryAlgorithmInfo(self):
        dict_QryAlgorithmInfo = {'MsgRef': self.__sm.msg_ref_add(),
                                 'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                 'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                 'MsgType': 11,  # 查询期货账户
                                 'TraderID': self.__TraderID,
                                 }
        json_QryAlgorithmInfo = json.dumps(dict_QryAlgorithmInfo)
        self.get_SocketManager().send_msg(json_QryAlgorithmInfo)

    # 查询策略
    def QryStrategyInfo(self, UserID="", StrategyID=""):
        dict_QryStrategyInfo = {'MsgRef': self.__sm.msg_ref_add(),
                                'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                'MsgType': 3,  # 查询策略
                                'TraderID': self.__TraderID,
                                'UserID': UserID,
                                'StrategyID': StrategyID
                                }
        json_QryStrategyInfo = json.dumps(dict_QryStrategyInfo)
        # self.get_SocketManager().send_msg(json_QryStrategyInfo)
        self.signal_send_msg.emit(json_QryStrategyInfo)

    # 查询策略昨仓
    def QryYesterdayPosition(self):
        dict_QryYesterdayPosition = {
            'MsgRef': self.__sm.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 10,  # 查询策略昨仓
            'TraderID': self.__CTPManager.get_trader_id(),
            'UserID': ""  # self.__user_id, 键值为空时查询所有UserID的策略
            }
        json_QryYesterdayPosition = json.dumps(dict_QryYesterdayPosition)
        self.get_SocketManager().send_msg(json_QryYesterdayPosition)

    # 新建策略
    def CreateStrategy(self, dict_info):
        dict_CreateStrategy = {
            'MsgRef': self.__sm.msg_ref_add(),
            'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
            'MsgSrc': 0,  # 消息源，客户端0，服务端1
            'MsgType': 6,  # 新建策略
            'TraderID': self.get_TraderID(),
            'UserID': dict_info['user_id'],
            'Info': [dict_info]
        }
        json_CreateStrategy = json.dumps(dict_CreateStrategy)
        # self.get_SocketManager().send_msg(json_CreateStrategy)
        self.signal_send_msg.emit(json_CreateStrategy)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    # 添加样式表
    file = QtCore.QFile('img/silvery.css')
    file.open(QtCore.QFile.ReadOnly)
    styleSheet = file.readAll().data().decode("utf-8")
    file.close()
    # QtGui.qApp.setStyleSheet(styleSheet)

    q_client_main = ClientMain()  # 创建客户端主界面实例
    ctp_manager = CTPManager()  # 创建客户端内核管理实例
    ctp_manager.set_ClientMain(q_client_main)  # 客户端界面实例与内核管理实例相互设置为对方的属性
    q_client_main.set_CTPManager(ctp_manager)

    q_login_form = QLogin.QLoginForm()  # 创建登录界面
    q_login_form.set_QClientMain(q_client_main)  # 登录界面与客户端主界面相互设置为对方的属性
    q_client_main.set_QLoginForm(q_login_form)
    q_login_form.show()

    q_ctp = QCTP()  # 创建最外围的大窗口
    q_login_form.set_QCTP(q_ctp)
    q_client_main.set_QCTP(q_ctp)

    # q_login_form.set_dict_QAccountWidget(dict_QAccountWidget)  # 账户窗口字典设置为LoginForm的属性
    # q_client_main.set_dict_QAccountWidget(dict_QAccountWidget)  # 账户窗口字典设置为ClientMain的属性
    # q_ctp.tab_accounts.addTab(dict_QAccountWidget['总账户'], '总账户')  # 账户窗口添加到QCTP窗口的tab
    # print('>>>>>>>>>>>len(ctp_manager.get_list_user()=', len(ctp_manager.get_list_user()))
    # for i in ctp_manager.get_list_user():
    #     tmp = QAccountWidget()
    #     dict_QAccountWidget = {i.get_user_id(): tmp}  # 创建单个账户QAccountWidget，键名为user_id
    #     q_ctp.tab_accounts.addTab(dict_QAccountWidget[i.get_user_id()], i.get_user_id())  # 账户窗口添加到QCTP窗口的tab

    print("if __name__ == '__main__'")
    sys.exit(app.exec_())


