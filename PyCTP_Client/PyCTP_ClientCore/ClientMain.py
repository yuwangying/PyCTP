import sys
from CTPManager import CTPManager
from PyQt4 import QtGui
from PyQt4 import QtCore
import QLogin  # from QLogin import QLoginForm
from QCTP import QCTP
from QAccountWidget import QAccountWidget
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
    def __init__(self, parent=None):
        super(ClientMain, self).__init__(parent) # 显示调用父类初始化方法，使用其信号槽机制
        self.__list_QAccountWidget = list()  # 存放账户窗口

    def set_SocketManager(self, obj_sm):
        self.__sm = obj_sm
        self.__sm.signal_send_message.connect(self.slot_output_message)  # 绑定自定义信号槽

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

    # 设置内核初始化状态
    def set_core_init_finished(self, bool_input):
        self.__core_init_finished = bool_input
        # 如果内核初始化完成，隐藏登录窗口，显示主窗口
        if self.__core_init_finished is True:
            print("ClientMain.set_core_init_finished() 内核初始化完成")
            self.__QLoginForm.hide()  # 隐藏登录窗口
            self.__QCTP.show()  # 显示主窗口

            # 创建总账户窗口，将user对象列表设置为其属性，将窗口对象存放到list里，总账户窗口初始化函数内部将总账户窗口对象设置为各user对象的属性。
            tmpQ = QAccountWidget(str_widget_name='总账户', list_user=self.get_CTPManager().get_list_user())
            tmpQ.set_ClientMain(self)  # ClientMain设置为窗口对象的属性
            # 总账户窗口实例设置为所有策略的属性
            for i_strategy in self.get_CTPManager().get_list_strategy():
                i_strategy.set_QAccountWidgetTotal(tmpQ)
            tmpQ.init_table_widget()  # 初始化界面：策略列表，tableWidget_Trade_Args
            self.__list_QAccountWidget.append(tmpQ)  # 将窗口对象存放到list集合里

            # 创建单个账户窗口，将user对象设置为其属性，将窗口对象存放到list里
            for i_user in self.get_CTPManager().get_list_user():
                tmpQ = QAccountWidget(str_widget_name=i_user.get_user_id().decode(), obj_user=i_user)  # 创建窗口，并将user设置为其属性
                i_user.set_QAccountWidget(tmpQ)  # 窗口实例设置为user的对象
                tmpQ.set_ClientMain(self)  # ClientMain这是为窗口的属性
                # 单账户窗口实例设置为对应期货账户下面所有策略的属性
                for i_strategy in tmpQ.get_user().get_list_strategy():
                    i_strategy.set_QAccountWidget(tmpQ)
                tmpQ.init_table_widget()  # 初始化界面：策略列表，tableWidget_Trade_Args
                self.__list_QAccountWidget.append(tmpQ)  # 将窗口对象存放到list集合里

            # 账户窗口添加到QCTP窗口的tab
            for i in self.__list_QAccountWidget:
                self.get_QCTP().tab_accounts.addTab(i, i.get_widget_name())

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

    def get_listAlgorithmWidget(self):
        return self.__listAlgorithmInfo

    # 获取内核初始化状态
    def get_core_init_finished(self):
        return self.__core_init_finished

    # 设置鼠标点击状态，信息包含:item所在行、item所在列、widget_name、user_id、strategy_id
    def set_clicked_status(self, in_dict):
        self.__clicked_status = in_dict

    def get_clicked_status(self):
        return self.__clicked_status

    # 处理socket_manager发来的消息
    @QtCore.pyqtSlot(dict)
    def slot_output_message(self, buff):
        # 消息源MsgSrc值：0客户端、1服务端
        if buff['MsgSrc'] == 0:  # 由客户端发起的消息类型
            if buff['MsgType'] == 1:  # 交易员登录验证，MsgType=1
                print("ClientMain.slot_output_message() MsgType=1", buff)  # 输出错误消息
                if buff['MsgResult'] == 0:  # 验证通过
                    # self.get_QLoginForm().label_login_error.setText(buff['MsgErrorReason'])  # 界面提示信息
                    self.get_QLoginForm().label_login_error.setText('登陆成功，初始化中...')  # 界面提示信息
                    self.__CTPManager.set_TraderID(buff['TraderID'])  # 将TraderID设置为CTPManager的属性
                    self.__TraderID = self.__QLoginForm.get_dict_login()['TraderID']
                    self.__Password = self.__QLoginForm.get_dict_login()['Password']
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
                    self.QryAlgorithmInfo()  # 查询策略信息
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
                    self.__CTPManager.init()  # 跳转到开始初始化程序，有CTPManager开始初始化
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    pass
            elif buff['MsgType'] == 6:  # 新增策略，MsgType=6
                print("ClientMain.slot_output_message() MsgType=6", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    pass
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    pass
            elif buff['MsgType'] == 5:  # 修改策略，MsgType=5
                print("ClientMain.slot_output_message() MsgType=5", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    pass
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    pass
            elif buff['MsgType'] == 7:  # 删除策略，MsgType=7
                print("ClientMain.slot_output_message() MsgType=7", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    pass
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    pass
            elif buff['MsgType'] == 10:  # 查询策略昨仓，MsgType=10
                print("ClientMain.slot_output_message() MsgType=10", buff)
                if buff['MsgResult'] == 0:  # 消息结果成功
                    for i in self.__CTPManager.get_list_user():  # 遍历user对象列表
                        if i.get_user_id().decode() == buff['UserID']:  # 找到对应的user对象
                            if len(i.get_list_strategy()) == 0:
                                continue
                            for j in i.get_list_strategy():  # 遍历strategy对象列表
                                if j.get_strategy_id() == buff['StrategyID']:  # 找到对应的strategy对象
                                    j.OnRspQryStrategyYesterdayPosition(buff['Info'][0])  # 将查询结果给到Strategy的回调函数
                                    print(">>> ClientMain.slot_output_message() ")
                                    j.init_yesterday_position()  # 初始化策略昨仓
                elif buff['MsgResult'] == 1:  # 消息结果失败
                    pass
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
    def QryStrategyInfo(self):
        dict_QryStrategyInfo = {'MsgRef': self.__sm.msg_ref_add(),
                                'MsgSendFlag': 0,  # 发送标志，客户端发出0，服务端发出1
                                'MsgSrc': 0,  # 消息源，客户端0，服务端1
                                'MsgType': 3,  # 查询策略
                                'TraderID': self.__TraderID,
                                'UserID': ''
                                }
        json_QryStrategyInfo = json.dumps(dict_QryStrategyInfo)
        self.get_SocketManager().send_msg(json_QryStrategyInfo)


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


