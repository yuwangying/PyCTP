import sys
import ClientCore
import QAccountWidget
from PyQt4 import QtGui
from PyQt4 import QtCore
import QLogin  # from QLogin import QLoginForm
from QCTP import QCTP
from QAccountWidget import QAccountWidget
import SocketManager


class ClientMain(QtCore.QObject):

    def __init__(self, parent=None):
        super(ClientMain, self).__init__(parent) #显示调用父类初始化方法，使用其信号槽机制

    def set_SocketManager(self, obj_sm):
        self.__sockmanager = obj_sm
        obj_sm.signal_send_message.connect(self.slot_output_message)

    def set_QLoginForm(self, qloginform):
        self.__QLoginForm = qloginform

    def set_QCTP(self, obj_QCTP):
        self.__QCTP = obj_QCTP

    def set_QAccountWidget(self, obj_QAccountWidget):
        self.__QAccoutWidget = obj_QAccountWidget

    def set_QOrderWidget(self, obj_QOrderWidget):
        self.__QOrderWidget = obj_QOrderWidget

    def get_SocketManager(self):
        return self.__sockmanager

    def get_QLoginForm(self):
        return self.__QLoginForm

    def get_QCTP(self, obj_QCTP):
        return self.__QCTP

    def get_QAccoutWidget(self):
        return self.__QAccoutWidget

    def get_QOrderWidget(self):
        return self.__QOrderWidget

    # 处理socket_manager发来的消息
    @QtCore.pyqtSlot(dict)
    def slot_output_message(self, buff):
        print("ClientMain Receive Message", buff)
        # 对buff进行数据处理
        if buff['MsgSendFlag'] == 's2c':  # server to client
            if buff['MsgType'] == 4:  # trader登录消息
                if buff['MsgResult'] == 0:  # 登录结果为成功
                    self.__QLoginForm.hide()
                    self.__QCTP.setVisible(True)
        elif buff['MsgSendFlag'] == 'c2s':  # client to server


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    q_client_main = ClientMain()

    q_login_form = QLogin.QLoginForm()  # 创建登录窗口
    q_login_form.set_QClientMain(q_client_main)
    q_client_main.set_QLoginForm(q_login_form)
    q_login_form.show()

    q_ctp = QCTP()  # 创建最外围的大窗口
    q_login_form.set_QCTP(q_ctp)
    q_client_main.set_QCTP(q_ctp)

    q_account_widget = QAccountWidget()  # 创建账户窗口
    q_login_form.set_QAccountWidget(q_account_widget)
    q_client_main.set_QAccountWidget(q_account_widget)

    q_account_widget2 = QAccountWidget()  # 创建账户窗口
    q_login_form.set_QAccountWidget(q_account_widget2)
    q_client_main.set_QAccountWidget(q_account_widget2)

    q_ctp.tab_accounts.addTab(q_account_widget, "总账户")  # 账户窗口添加到QCTP窗口的tab
    q_ctp.tab_records.addTab(q_account_widget2, "总持仓")

    # q_account_widget.setVisible(False)

    sys.exit(app.exec_())

