# -*- coding: utf-8 -*-

"""
Module implementing QCTP.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QCloseEvent
from PyQt4 import QtCore
from QMessageCenter import MessageCenter


from Ui_QCTP import Ui_MainWindow

from PyQt4 import QtCore, QtGui

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


class QCTP(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    # 定义信号：TabWidget的tab页被鼠标点击（切换tab页），形参为tab_name
    signal_on_tab_accounts_currentChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QCTP, self).__init__(parent)
        self.setupUi(self)

        # 托盘
        self.hideAction = QtGui.QAction("&隐藏", self, triggered=self.hide)
        self.hideAction.setIcon(QtGui.QIcon("image/trayicon_hide.ico"))
        self.showAction = QtGui.QAction("&显示", self, triggered=self.showNormal)
        self.showAction.setIcon(QtGui.QIcon("image/trayicon_show.ico"))
        self.quitAction = QtGui.QAction("&退出", self, triggered=self.quitWindow)
        self.quitAction.setIcon(QtGui.QIcon("image/trayicon_exit.ico"))
        # self.quitAction = QtGui.QAction("&退出", self, triggered=QtGui.qApp.quit)
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.hideAction)
        self.trayIconMenu.addAction(self.showAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.icon = QtGui.QIcon('img/rocket.ico')
        self.trayIcon = QtGui.QSystemTrayIcon()
        self.trayIcon.setToolTip("小蜜蜂套利系统")
        self.trayIcon.setIcon(self.icon)
        self.setWindowIcon(self.icon)
        self.trayIcon.activated.connect(self.iconActivated)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.show()

        self.message_center = MessageCenter(self)

        status_bar = QtGui.QStatusBar()  # 创建状态栏
        status_bar.addWidget(self.message_center, stretch=1)  # 设置状态栏格式
        self.setStatusBar(status_bar)
        self.__init_finished = False  # QCTP界面初始化完成标志位，初始值为False

    # 托盘图标被点击，槽函数
    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
            self.show()
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            # this will activate the window
            self.activateWindow()

    # 托盘菜单：退出
    @pyqtSlot()
    def quitWindow(self):
        print(">>> QCTP.quitWindow() ")
        self.widget_QAccountWidget.get_SocketManager().set_recive_msg_flag(False)
        QtCore.QCoreApplication.instance().quit()

    def set_ClientMain(self, obj_ClientMain):
        self.__client_main = obj_ClientMain

    def get_ClientMain(self):
        return self.__client_main

    def set_CTPManager(self, obj_CTPManager):
        self.__ctp_manager = obj_CTPManager

    def get_CTPManager(self):
        return self.__ctp_manager

    def set_QLogin(self, obj_QLogin):
        self.__q_login = obj_QLogin

    def get_QLogin(self):
        return self.__q_login

    def set_SocketManager(self, obj_SocketManager):
        self.__socket_manager = obj_SocketManager

    def get_SocketManager(self):
        return self.__socket_manager

    # 隐藏登录框且显示自己
    def show_me(self):
        self.__q_login.hide()
        self.show()

    # @pyqtSlot(int)
    # def on_tab_accounts_currentChanged(self, index):
    #     """
    #     Slot documentation goes here.
    #
    #     @param index DESCRIPTION
    #     @type int
    #     """
    #     # TODO: not implemented yet
    #     # raise NotImplementedError
    #     pass
    #     tab_name = self.tab_accounts.tabText(index)
    #     self.signal_on_tab_accounts_currentChanged.emit(tab_name)

    @pyqtSlot(int)
    def on_tab_records_currentChanged(self, index):
        """
        Slot documentation goes here.

        @param index DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        pass

    def closeEvent(self, QCloseEvent):
        print(">>> QCTP.closeEvent() ")
        # self.trayIcon.showMessage("小蜜蜂套利系统", "隐藏在右下角")
        self.trayIcon.showMessage("小蜜蜂套利系统", "隐藏在右下角", QtGui.QSystemTrayIcon.NoIcon, 2 * 1000)
        # self.widget_QAccountWidget.get_SocketManager().set_recive_msg_flag(False)
        # QtCore.QCoreApplication.instance().quit()
