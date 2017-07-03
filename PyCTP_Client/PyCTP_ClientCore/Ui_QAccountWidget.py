# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\CTP\PyCTP\PyCTP_Client\PyCTP_ClientUI\QAccountWidget.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(1409, 519)
        Form.setStyleSheet(_fromUtf8("QTabWidget::pane { /* The tab widget frame */\n"
"      border-top: 2px solid #C2C7CB;\n"
"}\n"
"\n"
"  QTabWidget::tab-bar {\n"
"      left: 5px; /* move to the right by 5px */\n"
"  }\n"
"\n"
"  /* Style the tab using the tab sub-control. Note that\n"
"      it reads QTabBar _not_ QTabWidget */\n"
"  QTabBar::tab {\n"
"        \n"
"    font: 11pt \"微软雅黑\";\n"
"      background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                  stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,\n"
"                                  stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);\n"
"      border: 2px solid #C4C4C3;\n"
"      border-bottom-color: #C2C7CB; /* same as the pane color */\n"
"      border-top-left-radius: 4px;\n"
"      border-top-right-radius: 4px;\n"
"      min-width: 100px;\n"
"      padding: 2px;\n"
"  }\n"
"\n"
"  QTabBar::tab:selected, QTabBar::tab:hover {\n"
"      background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                  stop: 0 #fafafa, stop: 0.4 #f4f4f4,\n"
"                                  stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);\n"
"  }\n"
"\n"
"  QTabBar::tab:selected {\n"
"      border-color: #9B9B9B;\n"
"      border-bottom-color: #C2C7CB; /* same as pane color */\n"
"  }\n"
"\n"
"  QTabBar::tab:!selected {\n"
"      margin-top: 2px; /* make non-selected tabs look smaller */\n"
"  }\n"
"\n"
"\n"
"/*鼠标右击菜单样式*/\n"
"QMenu {\n"
"      background-color: #ABABAB; /* sets background of the menu */\n"
"      border: 1px solid black;\n"
"  }\n"
"\n"
"  QMenu::item {\n"
"      /* sets background of menu item. set this to something non-transparent\n"
"          if you want menu color and menu item color to be different */\n"
"      background-color: transparent;\n"
"  }\n"
"\n"
"  QMenu::item:selected { /* when user selects item using mouse or keyboard */\n"
"      background-color: #654321;\n"
"  }\n"
"\n"
"/*右下角托盘样式*/\n"
"  QMenuBar {\n"
"      background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"                                        stop:0 lightgray, stop:1 darkgray);\n"
"  }\n"
"\n"
"  QMenuBar::item {\n"
"      spacing: 3px; /* spacing between menu bar items */\n"
"      padding: 1px 4px;\n"
"      background: transparent;\n"
"      border-radius: 4px;\n"
"  }\n"
"\n"
"  QMenuBar::item:selected { /* when selected using mouse or keyboard */\n"
"      background: #a8a8a8;\n"
"  }\n"
"\n"
"  QMenuBar::item:pressed {\n"
"      background: #888888;\n"
"  }\n"
"\n"
""))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setMargin(2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter_qaccount = QtGui.QSplitter(Form)
        self.splitter_qaccount.setOrientation(QtCore.Qt.Vertical)
        self.splitter_qaccount.setHandleWidth(1)
        self.splitter_qaccount.setChildrenCollapsible(False)
        self.splitter_qaccount.setObjectName(_fromUtf8("splitter_qaccount"))
        self.widget_tabbar = QtGui.QWidget(self.splitter_qaccount)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_tabbar.sizePolicy().hasHeightForWidth())
        self.widget_tabbar.setSizePolicy(sizePolicy)
        self.widget_tabbar.setMinimumSize(QtCore.QSize(0, 30))
        self.widget_tabbar.setMaximumSize(QtCore.QSize(16777215, 30))
        self.widget_tabbar.setStyleSheet(_fromUtf8("background-color: rgb(162, 162, 162);"))
        self.widget_tabbar.setObjectName(_fromUtf8("widget_tabbar"))
        self.panel_show_account = QtGui.QWidget(self.splitter_qaccount)
        self.panel_show_account.setMinimumSize(QtCore.QSize(0, 70))
        self.panel_show_account.setMaximumSize(QtCore.QSize(16777215, 70))
        self.panel_show_account.setStyleSheet(_fromUtf8("background-color: rgb(109, 109, 109);\n"
"color: rgb(250, 250, 250);\n"
"font: 100 10pt \"微软雅黑\";"))
        self.panel_show_account.setObjectName(_fromUtf8("panel_show_account"))
        self.horizontalLayout_panel_show_account = QtGui.QHBoxLayout(self.panel_show_account)
        self.horizontalLayout_panel_show_account.setContentsMargins(1, 0, 1, 1)
        self.horizontalLayout_panel_show_account.setSpacing(1)
        self.horizontalLayout_panel_show_account.setObjectName(_fromUtf8("horizontalLayout_panel_show_account"))
        self.widget_dongtaiquanyi = QtGui.QWidget(self.panel_show_account)
        self.widget_dongtaiquanyi.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_dongtaiquanyi.setObjectName(_fromUtf8("widget_dongtaiquanyi"))
        self.gridLayout_5 = QtGui.QGridLayout(self.widget_dongtaiquanyi)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_value_dongtaiquanyi = QtGui.QLabel(self.widget_dongtaiquanyi)
        self.label_value_dongtaiquanyi.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_dongtaiquanyi.setObjectName(_fromUtf8("label_value_dongtaiquanyi"))
        self.gridLayout_5.addWidget(self.label_value_dongtaiquanyi, 1, 0, 1, 1)
        self.label_dongtaiquanyi = QtGui.QLabel(self.widget_dongtaiquanyi)
        self.label_dongtaiquanyi.setAlignment(QtCore.Qt.AlignCenter)
        self.label_dongtaiquanyi.setObjectName(_fromUtf8("label_dongtaiquanyi"))
        self.gridLayout_5.addWidget(self.label_dongtaiquanyi, 0, 0, 1, 1)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_dongtaiquanyi)
        self.line_13 = QtGui.QFrame(self.panel_show_account)
        self.line_13.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_13.setFrameShape(QtGui.QFrame.VLine)
        self.line_13.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_13.setObjectName(_fromUtf8("line_13"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_13)
        self.widget_jingtaiquanyi = QtGui.QWidget(self.panel_show_account)
        self.widget_jingtaiquanyi.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_jingtaiquanyi.setObjectName(_fromUtf8("widget_jingtaiquanyi"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget_jingtaiquanyi)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_jingtaiquanyi = QtGui.QLabel(self.widget_jingtaiquanyi)
        self.label_jingtaiquanyi.setAlignment(QtCore.Qt.AlignCenter)
        self.label_jingtaiquanyi.setObjectName(_fromUtf8("label_jingtaiquanyi"))
        self.verticalLayout_3.addWidget(self.label_jingtaiquanyi)
        self.label_value_jingtaiquanyi = QtGui.QLabel(self.widget_jingtaiquanyi)
        self.label_value_jingtaiquanyi.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_jingtaiquanyi.setObjectName(_fromUtf8("label_value_jingtaiquanyi"))
        self.verticalLayout_3.addWidget(self.label_value_jingtaiquanyi)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_jingtaiquanyi)
        self.line_14 = QtGui.QFrame(self.panel_show_account)
        self.line_14.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_14.setFrameShape(QtGui.QFrame.VLine)
        self.line_14.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_14.setObjectName(_fromUtf8("line_14"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_14)
        self.widget_chicangyingkui = QtGui.QWidget(self.panel_show_account)
        self.widget_chicangyingkui.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_chicangyingkui.setObjectName(_fromUtf8("widget_chicangyingkui"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.widget_chicangyingkui)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.label_chicangyingkui = QtGui.QLabel(self.widget_chicangyingkui)
        self.label_chicangyingkui.setAlignment(QtCore.Qt.AlignCenter)
        self.label_chicangyingkui.setObjectName(_fromUtf8("label_chicangyingkui"))
        self.verticalLayout_8.addWidget(self.label_chicangyingkui)
        self.label_value_chicangyingkui = QtGui.QLabel(self.widget_chicangyingkui)
        self.label_value_chicangyingkui.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_chicangyingkui.setObjectName(_fromUtf8("label_value_chicangyingkui"))
        self.verticalLayout_8.addWidget(self.label_value_chicangyingkui)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_chicangyingkui)
        self.line_15 = QtGui.QFrame(self.panel_show_account)
        self.line_15.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_15.setFrameShape(QtGui.QFrame.VLine)
        self.line_15.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_15.setObjectName(_fromUtf8("line_15"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_15)
        self.widget_pingcangyingkui = QtGui.QWidget(self.panel_show_account)
        self.widget_pingcangyingkui.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_pingcangyingkui.setObjectName(_fromUtf8("widget_pingcangyingkui"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.widget_pingcangyingkui)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.label_pingcangyingkui = QtGui.QLabel(self.widget_pingcangyingkui)
        self.label_pingcangyingkui.setAlignment(QtCore.Qt.AlignCenter)
        self.label_pingcangyingkui.setObjectName(_fromUtf8("label_pingcangyingkui"))
        self.verticalLayout_9.addWidget(self.label_pingcangyingkui)
        self.label_value_pingcangyingkui = QtGui.QLabel(self.widget_pingcangyingkui)
        self.label_value_pingcangyingkui.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_pingcangyingkui.setObjectName(_fromUtf8("label_value_pingcangyingkui"))
        self.verticalLayout_9.addWidget(self.label_value_pingcangyingkui)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_pingcangyingkui)
        self.line_16 = QtGui.QFrame(self.panel_show_account)
        self.line_16.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_16.setFrameShape(QtGui.QFrame.VLine)
        self.line_16.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_16.setObjectName(_fromUtf8("line_16"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_16)
        self.widget_shouxufei = QtGui.QWidget(self.panel_show_account)
        self.widget_shouxufei.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_shouxufei.setObjectName(_fromUtf8("widget_shouxufei"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.widget_shouxufei)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.label_shouxufei = QtGui.QLabel(self.widget_shouxufei)
        self.label_shouxufei.setAlignment(QtCore.Qt.AlignCenter)
        self.label_shouxufei.setObjectName(_fromUtf8("label_shouxufei"))
        self.verticalLayout_10.addWidget(self.label_shouxufei)
        self.label_value_shouxufei = QtGui.QLabel(self.widget_shouxufei)
        self.label_value_shouxufei.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_shouxufei.setObjectName(_fromUtf8("label_value_shouxufei"))
        self.verticalLayout_10.addWidget(self.label_value_shouxufei)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_shouxufei)
        self.line_17 = QtGui.QFrame(self.panel_show_account)
        self.line_17.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_17.setFrameShape(QtGui.QFrame.VLine)
        self.line_17.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_17.setObjectName(_fromUtf8("line_17"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_17)
        self.widget_keyongzijin = QtGui.QWidget(self.panel_show_account)
        self.widget_keyongzijin.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_keyongzijin.setObjectName(_fromUtf8("widget_keyongzijin"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.widget_keyongzijin)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.label_keyongzijin = QtGui.QLabel(self.widget_keyongzijin)
        self.label_keyongzijin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_keyongzijin.setObjectName(_fromUtf8("label_keyongzijin"))
        self.verticalLayout_11.addWidget(self.label_keyongzijin)
        self.label_value_keyongzijin = QtGui.QLabel(self.widget_keyongzijin)
        self.label_value_keyongzijin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_keyongzijin.setObjectName(_fromUtf8("label_value_keyongzijin"))
        self.verticalLayout_11.addWidget(self.label_value_keyongzijin)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_keyongzijin)
        self.line_18 = QtGui.QFrame(self.panel_show_account)
        self.line_18.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_18.setFrameShape(QtGui.QFrame.VLine)
        self.line_18.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_18.setObjectName(_fromUtf8("line_18"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_18)
        self.widget_zhanyongbaozhengjin = QtGui.QWidget(self.panel_show_account)
        self.widget_zhanyongbaozhengjin.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_zhanyongbaozhengjin.setObjectName(_fromUtf8("widget_zhanyongbaozhengjin"))
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.widget_zhanyongbaozhengjin)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.label_zhanyongbaozhengjin = QtGui.QLabel(self.widget_zhanyongbaozhengjin)
        self.label_zhanyongbaozhengjin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_zhanyongbaozhengjin.setObjectName(_fromUtf8("label_zhanyongbaozhengjin"))
        self.verticalLayout_12.addWidget(self.label_zhanyongbaozhengjin)
        self.label_value_zhanyongbaozhengjin = QtGui.QLabel(self.widget_zhanyongbaozhengjin)
        self.label_value_zhanyongbaozhengjin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_zhanyongbaozhengjin.setObjectName(_fromUtf8("label_value_zhanyongbaozhengjin"))
        self.verticalLayout_12.addWidget(self.label_value_zhanyongbaozhengjin)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_zhanyongbaozhengjin)
        self.line_19 = QtGui.QFrame(self.panel_show_account)
        self.line_19.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_19.setFrameShape(QtGui.QFrame.VLine)
        self.line_19.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_19.setObjectName(_fromUtf8("line_19"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_19)
        self.widget_fengxiandu = QtGui.QWidget(self.panel_show_account)
        self.widget_fengxiandu.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_fengxiandu.setObjectName(_fromUtf8("widget_fengxiandu"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.widget_fengxiandu)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_fengxiandu = QtGui.QLabel(self.widget_fengxiandu)
        self.label_fengxiandu.setAlignment(QtCore.Qt.AlignCenter)
        self.label_fengxiandu.setObjectName(_fromUtf8("label_fengxiandu"))
        self.verticalLayout_5.addWidget(self.label_fengxiandu)
        self.label_value_fengxiandu = QtGui.QLabel(self.widget_fengxiandu)
        self.label_value_fengxiandu.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_fengxiandu.setObjectName(_fromUtf8("label_value_fengxiandu"))
        self.verticalLayout_5.addWidget(self.label_value_fengxiandu)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_fengxiandu)
        self.line_10 = QtGui.QFrame(self.panel_show_account)
        self.line_10.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_10.setFrameShape(QtGui.QFrame.VLine)
        self.line_10.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_10.setObjectName(_fromUtf8("line_10"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_10)
        self.widget_jinrirujin = QtGui.QWidget(self.panel_show_account)
        self.widget_jinrirujin.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_jinrirujin.setObjectName(_fromUtf8("widget_jinrirujin"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.widget_jinrirujin)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.label_jinrirujin = QtGui.QLabel(self.widget_jinrirujin)
        self.label_jinrirujin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_jinrirujin.setObjectName(_fromUtf8("label_jinrirujin"))
        self.verticalLayout_6.addWidget(self.label_jinrirujin)
        self.label_value_jinrirujin = QtGui.QLabel(self.widget_jinrirujin)
        self.label_value_jinrirujin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_jinrirujin.setObjectName(_fromUtf8("label_value_jinrirujin"))
        self.verticalLayout_6.addWidget(self.label_value_jinrirujin)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_jinrirujin)
        self.line_11 = QtGui.QFrame(self.panel_show_account)
        self.line_11.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_11.setFrameShape(QtGui.QFrame.VLine)
        self.line_11.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_11.setObjectName(_fromUtf8("line_11"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_11)
        self.widget_jinrichujin = QtGui.QWidget(self.panel_show_account)
        self.widget_jinrichujin.setStyleSheet(_fromUtf8("border-right-color: rgb(170, 164, 162);"))
        self.widget_jinrichujin.setObjectName(_fromUtf8("widget_jinrichujin"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.widget_jinrichujin)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_jinrichujin = QtGui.QLabel(self.widget_jinrichujin)
        self.label_jinrichujin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_jinrichujin.setObjectName(_fromUtf8("label_jinrichujin"))
        self.verticalLayout_7.addWidget(self.label_jinrichujin)
        self.label_value_jinrichujin = QtGui.QLabel(self.widget_jinrichujin)
        self.label_value_jinrichujin.setAlignment(QtCore.Qt.AlignCenter)
        self.label_value_jinrichujin.setObjectName(_fromUtf8("label_value_jinrichujin"))
        self.verticalLayout_7.addWidget(self.label_value_jinrichujin)
        self.horizontalLayout_panel_show_account.addWidget(self.widget_jinrichujin)
        self.line_12 = QtGui.QFrame(self.panel_show_account)
        self.line_12.setStyleSheet(_fromUtf8("background-color: rgb(150, 150, 150);"))
        self.line_12.setFrameShape(QtGui.QFrame.VLine)
        self.line_12.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_12.setObjectName(_fromUtf8("line_12"))
        self.horizontalLayout_panel_show_account.addWidget(self.line_12)
        self.pushButton_query_account = QtGui.QPushButton(self.panel_show_account)
        self.pushButton_query_account.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton_query_account.setStyleSheet(_fromUtf8("QPushButton{\n"
"    background-color: rgb(255, 255, 255);\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(109, 109, 109);\n"
"    color: rgb(255, 255, 255);\n"
"}"))
        self.pushButton_query_account.setObjectName(_fromUtf8("pushButton_query_account"))
        self.horizontalLayout_panel_show_account.addWidget(self.pushButton_query_account)
        self.pushButton_start_strategy = QtGui.QPushButton(self.panel_show_account)
        self.pushButton_start_strategy.setStyleSheet(_fromUtf8("QPushButton{\n"
"    background-color: rgb(255, 255, 255);\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(109, 109, 109);\n"
"    color: rgb(255, 255, 255);\n"
"}"))
        self.pushButton_start_strategy.setObjectName(_fromUtf8("pushButton_start_strategy"))
        self.horizontalLayout_panel_show_account.addWidget(self.pushButton_start_strategy)
        self.splitter = QtGui.QSplitter(self.splitter_qaccount)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setMinimumSize(QtCore.QSize(0, 0))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tableView_Trade_Args = QtGui.QTableView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(32)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_Trade_Args.sizePolicy().hasHeightForWidth())
        self.tableView_Trade_Args.setSizePolicy(sizePolicy)
        self.tableView_Trade_Args.setMinimumSize(QtCore.QSize(0, 380))
        self.tableView_Trade_Args.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tableView_Trade_Args.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tableView_Trade_Args.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 245);"))
        self.tableView_Trade_Args.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView_Trade_Args.setObjectName(_fromUtf8("tableView_Trade_Args"))
        self.groupBox_trade_args = QtGui.QGroupBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(6)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_trade_args.sizePolicy().hasHeightForWidth())
        self.groupBox_trade_args.setSizePolicy(sizePolicy)
        self.groupBox_trade_args.setMinimumSize(QtCore.QSize(416, 410))
        self.groupBox_trade_args.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 245);\n"
""))
        self.groupBox_trade_args.setFlat(False)
        self.groupBox_trade_args.setCheckable(False)
        self.groupBox_trade_args.setObjectName(_fromUtf8("groupBox_trade_args"))
        self.label_kongtoujiacha = QtGui.QLabel(self.groupBox_trade_args)
        self.label_kongtoujiacha.setGeometry(QtCore.QRect(12, 180, 60, 16))
        self.label_kongtoujiacha.setObjectName(_fromUtf8("label_kongtoujiacha"))
        self.label_qihuozhanghao = QtGui.QLabel(self.groupBox_trade_args)
        self.label_qihuozhanghao.setGeometry(QtCore.QRect(12, 30, 60, 16))
        self.label_qihuozhanghao.setObjectName(_fromUtf8("label_qihuozhanghao"))
        self.label_jiaoyimoxing = QtGui.QLabel(self.groupBox_trade_args)
        self.label_jiaoyimoxing.setGeometry(QtCore.QRect(12, 60, 60, 16))
        self.label_jiaoyimoxing.setObjectName(_fromUtf8("label_jiaoyimoxing"))
        self.label_chaojiachufa = QtGui.QLabel(self.groupBox_trade_args)
        self.label_chaojiachufa.setGeometry(QtCore.QRect(12, 150, 60, 16))
        self.label_chaojiachufa.setObjectName(_fromUtf8("label_chaojiachufa"))
        self.label_duotoujiacha = QtGui.QLabel(self.groupBox_trade_args)
        self.label_duotoujiacha.setGeometry(QtCore.QRect(12, 210, 60, 16))
        self.label_duotoujiacha.setObjectName(_fromUtf8("label_duotoujiacha"))
        self.checkBox_kongtoukai = QtGui.QCheckBox(self.groupBox_trade_args)
        self.checkBox_kongtoukai.setGeometry(QtCore.QRect(12, 240, 72, 19))
        self.checkBox_kongtoukai.setObjectName(_fromUtf8("checkBox_kongtoukai"))
        self.checkBox_duotouping = QtGui.QCheckBox(self.groupBox_trade_args)
        self.checkBox_duotouping.setGeometry(QtCore.QRect(12, 300, 72, 19))
        self.checkBox_duotouping.setObjectName(_fromUtf8("checkBox_duotouping"))
        self.checkBox_duotoukai = QtGui.QCheckBox(self.groupBox_trade_args)
        self.checkBox_duotoukai.setGeometry(QtCore.QRect(12, 330, 72, 19))
        self.checkBox_duotoukai.setObjectName(_fromUtf8("checkBox_duotoukai"))
        self.label_zongshou = QtGui.QLabel(self.groupBox_trade_args)
        self.label_zongshou.setGeometry(QtCore.QRect(244, 90, 30, 16))
        self.label_zongshou.setObjectName(_fromUtf8("label_zongshou"))
        self.comboBox_jiaoyimoxing = QtGui.QComboBox(self.groupBox_trade_args)
        self.comboBox_jiaoyimoxing.setGeometry(QtCore.QRect(80, 60, 120, 21))
        self.comboBox_jiaoyimoxing.setObjectName(_fromUtf8("comboBox_jiaoyimoxing"))
        self.checkBox_kongtouping = QtGui.QCheckBox(self.groupBox_trade_args)
        self.checkBox_kongtouping.setGeometry(QtCore.QRect(12, 270, 72, 19))
        self.checkBox_kongtouping.setObjectName(_fromUtf8("checkBox_kongtouping"))
        self.label_celuebianhao = QtGui.QLabel(self.groupBox_trade_args)
        self.label_celuebianhao.setGeometry(QtCore.QRect(12, 90, 60, 16))
        self.label_celuebianhao.setObjectName(_fromUtf8("label_celuebianhao"))
        self.label_xiadansuanfa = QtGui.QLabel(self.groupBox_trade_args)
        self.label_xiadansuanfa.setGeometry(QtCore.QRect(128, 90, 60, 16))
        self.label_xiadansuanfa.setObjectName(_fromUtf8("label_xiadansuanfa"))
        self.label_meifen = QtGui.QLabel(self.groupBox_trade_args)
        self.label_meifen.setGeometry(QtCore.QRect(326, 90, 30, 16))
        self.label_meifen.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_meifen.setObjectName(_fromUtf8("label_meifen"))
        self.spinBox_rangjia = QtGui.QSpinBox(self.groupBox_trade_args)
        self.spinBox_rangjia.setGeometry(QtCore.QRect(80, 150, 46, 21))
        self.spinBox_rangjia.setMinimum(-999999999)
        self.spinBox_rangjia.setMaximum(999999999)
        self.spinBox_rangjia.setObjectName(_fromUtf8("spinBox_rangjia"))
        self.lineEdit_kongtoujiacha = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_kongtoujiacha.setGeometry(QtCore.QRect(68, 180, 120, 21))
        self.lineEdit_kongtoujiacha.setStyleSheet(_fromUtf8(""))
        self.lineEdit_kongtoujiacha.setText(_fromUtf8(""))
        self.lineEdit_kongtoujiacha.setObjectName(_fromUtf8("lineEdit_kongtoujiacha"))
        self.lineEdit_duotoujiacha = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_duotoujiacha.setGeometry(QtCore.QRect(68, 210, 120, 21))
        self.lineEdit_duotoujiacha.setText(_fromUtf8(""))
        self.lineEdit_duotoujiacha.setObjectName(_fromUtf8("lineEdit_duotoujiacha"))
        self.doubleSpinBox_kongtoukai = QtGui.QDoubleSpinBox(self.groupBox_trade_args)
        self.doubleSpinBox_kongtoukai.setGeometry(QtCore.QRect(76, 240, 120, 21))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_kongtoukai.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_kongtoukai.setSizePolicy(sizePolicy)
        self.doubleSpinBox_kongtoukai.setBaseSize(QtCore.QSize(0, 0))
        self.doubleSpinBox_kongtoukai.setMinimum(-99999999.0)
        self.doubleSpinBox_kongtoukai.setMaximum(99999999.0)
        self.doubleSpinBox_kongtoukai.setProperty("value", 0.0)
        self.doubleSpinBox_kongtoukai.setObjectName(_fromUtf8("doubleSpinBox_kongtoukai"))
        self.doubleSpinBox_kongtouping = QtGui.QDoubleSpinBox(self.groupBox_trade_args)
        self.doubleSpinBox_kongtouping.setGeometry(QtCore.QRect(76, 270, 120, 21))
        self.doubleSpinBox_kongtouping.setMinimum(-99999999.0)
        self.doubleSpinBox_kongtouping.setMaximum(99999999.0)
        self.doubleSpinBox_kongtouping.setProperty("value", 0.0)
        self.doubleSpinBox_kongtouping.setObjectName(_fromUtf8("doubleSpinBox_kongtouping"))
        self.doubleSpinBox_duotouping = QtGui.QDoubleSpinBox(self.groupBox_trade_args)
        self.doubleSpinBox_duotouping.setGeometry(QtCore.QRect(76, 300, 120, 21))
        self.doubleSpinBox_duotouping.setMinimum(-99999999.0)
        self.doubleSpinBox_duotouping.setMaximum(99999999.0)
        self.doubleSpinBox_duotouping.setProperty("value", 0.0)
        self.doubleSpinBox_duotouping.setObjectName(_fromUtf8("doubleSpinBox_duotouping"))
        self.doubleSpinBox_duotoukai = QtGui.QDoubleSpinBox(self.groupBox_trade_args)
        self.doubleSpinBox_duotoukai.setGeometry(QtCore.QRect(76, 330, 120, 21))
        self.doubleSpinBox_duotoukai.setMinimum(-99999999.0)
        self.doubleSpinBox_duotoukai.setMaximum(99999999.0)
        self.doubleSpinBox_duotoukai.setProperty("value", 0.0)
        self.doubleSpinBox_duotoukai.setObjectName(_fromUtf8("doubleSpinBox_duotoukai"))
        self.label_Adengdai = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Adengdai.setGeometry(QtCore.QRect(142, 120, 70, 16))
        self.label_Adengdai.setObjectName(_fromUtf8("label_Adengdai"))
        self.spinBox_Adengdai = QtGui.QSpinBox(self.groupBox_trade_args)
        self.spinBox_Adengdai.setGeometry(QtCore.QRect(216, 120, 46, 21))
        self.spinBox_Adengdai.setMinimum(-999999999)
        self.spinBox_Adengdai.setMaximum(999999999)
        self.spinBox_Adengdai.setObjectName(_fromUtf8("spinBox_Adengdai"))
        self.label_Bdengdai = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bdengdai.setGeometry(QtCore.QRect(280, 120, 70, 16))
        self.label_Bdengdai.setObjectName(_fromUtf8("label_Bdengdai"))
        self.spinBox_Bdengdai = QtGui.QSpinBox(self.groupBox_trade_args)
        self.spinBox_Bdengdai.setGeometry(QtCore.QRect(356, 120, 46, 21))
        self.spinBox_Bdengdai.setMinimum(-999999999)
        self.spinBox_Bdengdai.setMaximum(999999999)
        self.spinBox_Bdengdai.setObjectName(_fromUtf8("spinBox_Bdengdai"))
        self.label_Azongsell = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Azongsell.setGeometry(QtCore.QRect(216, 240, 38, 16))
        self.label_Azongsell.setObjectName(_fromUtf8("label_Azongsell"))
        self.lineEdit_Azongsell = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Azongsell.setEnabled(True)
        self.lineEdit_Azongsell.setGeometry(QtCore.QRect(260, 240, 40, 21))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_Azongsell.setFont(font)
        self.lineEdit_Azongsell.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Azongsell.setText(_fromUtf8(""))
        self.lineEdit_Azongsell.setReadOnly(True)
        self.lineEdit_Azongsell.setObjectName(_fromUtf8("lineEdit_Azongsell"))
        self.label_Bzongbuy = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bzongbuy.setGeometry(QtCore.QRect(216, 270, 38, 16))
        self.label_Bzongbuy.setObjectName(_fromUtf8("label_Bzongbuy"))
        self.lineEdit_Bzongbuy = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bzongbuy.setEnabled(True)
        self.lineEdit_Bzongbuy.setGeometry(QtCore.QRect(260, 270, 40, 21))
        self.lineEdit_Bzongbuy.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Bzongbuy.setText(_fromUtf8(""))
        self.lineEdit_Bzongbuy.setReadOnly(True)
        self.lineEdit_Bzongbuy.setObjectName(_fromUtf8("lineEdit_Bzongbuy"))
        self.label_Azongbuy = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Azongbuy.setGeometry(QtCore.QRect(216, 300, 38, 16))
        self.label_Azongbuy.setObjectName(_fromUtf8("label_Azongbuy"))
        self.lineEdit_Azongbuy = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Azongbuy.setEnabled(True)
        self.lineEdit_Azongbuy.setGeometry(QtCore.QRect(260, 300, 40, 21))
        self.lineEdit_Azongbuy.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Azongbuy.setText(_fromUtf8(""))
        self.lineEdit_Azongbuy.setReadOnly(True)
        self.lineEdit_Azongbuy.setObjectName(_fromUtf8("lineEdit_Azongbuy"))
        self.label_Bzongsell = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bzongsell.setGeometry(QtCore.QRect(216, 330, 38, 16))
        self.label_Bzongsell.setObjectName(_fromUtf8("label_Bzongsell"))
        self.lineEdit_Bzongsell = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bzongsell.setEnabled(True)
        self.lineEdit_Bzongsell.setGeometry(QtCore.QRect(260, 330, 40, 21))
        self.lineEdit_Bzongsell.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Bzongsell.setText(_fromUtf8(""))
        self.lineEdit_Bzongsell.setReadOnly(True)
        self.lineEdit_Bzongsell.setObjectName(_fromUtf8("lineEdit_Bzongsell"))
        self.label_Achedanxianzhi = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Achedanxianzhi.setGeometry(QtCore.QRect(202, 180, 39, 16))
        self.label_Achedanxianzhi.setObjectName(_fromUtf8("label_Achedanxianzhi"))
        self.lineEdit_Achedanxianzhi = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Achedanxianzhi.setGeometry(QtCore.QRect(244, 180, 40, 21))
        self.lineEdit_Achedanxianzhi.setObjectName(_fromUtf8("lineEdit_Achedanxianzhi"))
        self.label_Achedan = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Achedan.setGeometry(QtCore.QRect(294, 180, 37, 16))
        self.label_Achedan.setObjectName(_fromUtf8("label_Achedan"))
        self.lineEdit_Achedan = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Achedan.setGeometry(QtCore.QRect(338, 180, 64, 21))
        self.lineEdit_Achedan.setStyleSheet(_fromUtf8(""))
        self.lineEdit_Achedan.setText(_fromUtf8(""))
        self.lineEdit_Achedan.setObjectName(_fromUtf8("lineEdit_Achedan"))
        self.label_Bchedan = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bchedan.setGeometry(QtCore.QRect(294, 210, 37, 16))
        self.label_Bchedan.setObjectName(_fromUtf8("label_Bchedan"))
        self.lineEdit_Bchedan = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bchedan.setGeometry(QtCore.QRect(338, 210, 64, 21))
        self.lineEdit_Bchedan.setText(_fromUtf8(""))
        self.lineEdit_Bchedan.setObjectName(_fromUtf8("lineEdit_Bchedan"))
        self.label_Ajinsell = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Ajinsell.setGeometry(QtCore.QRect(316, 240, 38, 16))
        self.label_Ajinsell.setObjectName(_fromUtf8("label_Ajinsell"))
        self.lineEdit_Azuosell = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Azuosell.setEnabled(True)
        self.lineEdit_Azuosell.setGeometry(QtCore.QRect(362, 240, 40, 21))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_Azuosell.sizePolicy().hasHeightForWidth())
        self.lineEdit_Azuosell.setSizePolicy(sizePolicy)
        self.lineEdit_Azuosell.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Azuosell.setText(_fromUtf8(""))
        self.lineEdit_Azuosell.setReadOnly(True)
        self.lineEdit_Azuosell.setObjectName(_fromUtf8("lineEdit_Azuosell"))
        self.label_Bjinbuy = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bjinbuy.setGeometry(QtCore.QRect(316, 270, 38, 16))
        self.label_Bjinbuy.setObjectName(_fromUtf8("label_Bjinbuy"))
        self.lineEdit_Bzuobuy = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bzuobuy.setEnabled(True)
        self.lineEdit_Bzuobuy.setGeometry(QtCore.QRect(362, 270, 40, 21))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_Bzuobuy.sizePolicy().hasHeightForWidth())
        self.lineEdit_Bzuobuy.setSizePolicy(sizePolicy)
        self.lineEdit_Bzuobuy.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Bzuobuy.setText(_fromUtf8(""))
        self.lineEdit_Bzuobuy.setReadOnly(True)
        self.lineEdit_Bzuobuy.setObjectName(_fromUtf8("lineEdit_Bzuobuy"))
        self.label_Ajinbuy = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Ajinbuy.setGeometry(QtCore.QRect(316, 300, 38, 16))
        self.label_Ajinbuy.setObjectName(_fromUtf8("label_Ajinbuy"))
        self.lineEdit_Azuobuy = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Azuobuy.setEnabled(True)
        self.lineEdit_Azuobuy.setGeometry(QtCore.QRect(362, 300, 40, 21))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_Azuobuy.sizePolicy().hasHeightForWidth())
        self.lineEdit_Azuobuy.setSizePolicy(sizePolicy)
        self.lineEdit_Azuobuy.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Azuobuy.setText(_fromUtf8(""))
        self.lineEdit_Azuobuy.setReadOnly(True)
        self.lineEdit_Azuobuy.setObjectName(_fromUtf8("lineEdit_Azuobuy"))
        self.label_Bjinsell = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bjinsell.setGeometry(QtCore.QRect(316, 330, 38, 16))
        self.label_Bjinsell.setObjectName(_fromUtf8("label_Bjinsell"))
        self.lineEdit_Bzuosell = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bzuosell.setEnabled(True)
        self.lineEdit_Bzuosell.setGeometry(QtCore.QRect(362, 330, 40, 21))
        self.lineEdit_Bzuosell.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);"))
        self.lineEdit_Bzuosell.setText(_fromUtf8(""))
        self.lineEdit_Bzuosell.setReadOnly(True)
        self.lineEdit_Bzuosell.setObjectName(_fromUtf8("lineEdit_Bzuosell"))
        self.pushButton_liandongjia = QtGui.QPushButton(self.groupBox_trade_args)
        self.pushButton_liandongjia.setGeometry(QtCore.QRect(126, 360, 50, 18))
        self.pushButton_liandongjia.setStyleSheet(_fromUtf8("QPushButton{\n"
"    font: 100 10pt \"微软雅黑\";\n"
"    background-color: rgb(255, 255, 255);\n"
"    border: 1px solid #6D6D6D;\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(109, 109, 109);\n"
"    color: rgb(255, 255, 255);\n"
"}"))
        self.pushButton_liandongjia.setObjectName(_fromUtf8("pushButton_liandongjia"))
        self.pushButton_liandongjian = QtGui.QPushButton(self.groupBox_trade_args)
        self.pushButton_liandongjian.setGeometry(QtCore.QRect(126, 380, 50, 18))
        self.pushButton_liandongjian.setStyleSheet(_fromUtf8("QPushButton{\n"
"    font: 100 10pt \"微软雅黑\";\n"
"    background-color: rgb(255, 255, 255);\n"
"    border: 1px solid #6D6D6D;\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(109, 109, 109);\n"
"    color: rgb(255, 255, 255);\n"
"}"))
        self.pushButton_liandongjian.setObjectName(_fromUtf8("pushButton_liandongjian"))
        self.label_zhisun = QtGui.QLabel(self.groupBox_trade_args)
        self.label_zhisun.setGeometry(QtCore.QRect(12, 120, 60, 16))
        self.label_zhisun.setObjectName(_fromUtf8("label_zhisun"))
        self.spinBox_zhisun = QtGui.QSpinBox(self.groupBox_trade_args)
        self.spinBox_zhisun.setGeometry(QtCore.QRect(80, 120, 46, 21))
        self.spinBox_zhisun.setMinimum(-999999999)
        self.spinBox_zhisun.setMaximum(999999999)
        self.spinBox_zhisun.setObjectName(_fromUtf8("spinBox_zhisun"))
        self.pushButton_set_strategy = QtGui.QPushButton(self.groupBox_trade_args)
        self.pushButton_set_strategy.setEnabled(True)
        self.pushButton_set_strategy.setGeometry(QtCore.QRect(12, 360, 100, 40))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_set_strategy.sizePolicy().hasHeightForWidth())
        self.pushButton_set_strategy.setSizePolicy(sizePolicy)
        self.pushButton_set_strategy.setStyleSheet(_fromUtf8("QPushButton{\n"
"    font: 100 10pt \"微软雅黑\";\n"
"    background-color: rgb(255, 255, 255);\n"
"    border: 1px solid #6D6D6D;\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(109, 109, 109);\n"
"    color: rgb(255, 255, 255);\n"
"}"))
        self.pushButton_set_strategy.setObjectName(_fromUtf8("pushButton_set_strategy"))
        self.pushButton_query_strategy = QtGui.QPushButton(self.groupBox_trade_args)
        self.pushButton_query_strategy.setEnabled(True)
        self.pushButton_query_strategy.setGeometry(QtCore.QRect(190, 360, 100, 40))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_query_strategy.sizePolicy().hasHeightForWidth())
        self.pushButton_query_strategy.setSizePolicy(sizePolicy)
        self.pushButton_query_strategy.setStyleSheet(_fromUtf8("QPushButton{\n"
"    font: 100 10pt \"微软雅黑\";\n"
"    background-color: rgb(255, 255, 255);\n"
"    border: 1px solid #6D6D6D;\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(109, 109, 109);\n"
"    color: rgb(255, 255, 255);\n"
"}"))
        self.pushButton_query_strategy.setCheckable(False)
        self.pushButton_query_strategy.setObjectName(_fromUtf8("pushButton_query_strategy"))
        self.comboBox_xiadansuanfa = QtGui.QComboBox(self.groupBox_trade_args)
        self.comboBox_xiadansuanfa.setGeometry(QtCore.QRect(194, 90, 40, 21))
        self.comboBox_xiadansuanfa.setEditable(False)
        self.comboBox_xiadansuanfa.setObjectName(_fromUtf8("comboBox_xiadansuanfa"))
        self.label_Bchedanxianzhi = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bchedanxianzhi.setGeometry(QtCore.QRect(202, 210, 39, 16))
        self.label_Bchedanxianzhi.setObjectName(_fromUtf8("label_Bchedanxianzhi"))
        self.lineEdit_Bchedanxianzhi = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bchedanxianzhi.setGeometry(QtCore.QRect(244, 210, 40, 21))
        self.lineEdit_Bchedanxianzhi.setObjectName(_fromUtf8("lineEdit_Bchedanxianzhi"))
        self.lineEdit_zongshou = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_zongshou.setGeometry(QtCore.QRect(278, 90, 40, 21))
        self.lineEdit_zongshou.setObjectName(_fromUtf8("lineEdit_zongshou"))
        self.lineEdit_meifen = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_meifen.setGeometry(QtCore.QRect(362, 90, 40, 21))
        self.lineEdit_meifen.setObjectName(_fromUtf8("lineEdit_meifen"))
        self.pushButton_set_position = QtGui.QPushButton(self.groupBox_trade_args)
        self.pushButton_set_position.setEnabled(True)
        self.pushButton_set_position.setGeometry(QtCore.QRect(304, 360, 100, 40))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_set_position.sizePolicy().hasHeightForWidth())
        self.pushButton_set_position.setSizePolicy(sizePolicy)
        self.pushButton_set_position.setStyleSheet(_fromUtf8("QPushButton{\n"
"    font: 100 10pt \"微软雅黑\";\n"
"    background-color: rgb(255, 255, 255);\n"
"    border: 1px solid #6D6D6D;\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(109, 109, 109);\n"
"    color: rgb(255, 255, 255);\n"
"}"))
        self.pushButton_set_position.setObjectName(_fromUtf8("pushButton_set_position"))
        self.lineEdit_qihuozhanghao = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_qihuozhanghao.setEnabled(True)
        self.lineEdit_qihuozhanghao.setGeometry(QtCore.QRect(80, 30, 120, 21))
        self.lineEdit_qihuozhanghao.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);"))
        self.lineEdit_qihuozhanghao.setText(_fromUtf8(""))
        self.lineEdit_qihuozhanghao.setReadOnly(True)
        self.lineEdit_qihuozhanghao.setObjectName(_fromUtf8("lineEdit_qihuozhanghao"))
        self.lineEdit_celuebianhao = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_celuebianhao.setEnabled(True)
        self.lineEdit_celuebianhao.setGeometry(QtCore.QRect(80, 90, 40, 21))
        self.lineEdit_celuebianhao.setStyleSheet(_fromUtf8("color: rgb(0, 0, 0);"))
        self.lineEdit_celuebianhao.setText(_fromUtf8(""))
        self.lineEdit_celuebianhao.setReadOnly(True)
        self.lineEdit_celuebianhao.setObjectName(_fromUtf8("lineEdit_celuebianhao"))
        self.label_Bbaodanpianyi = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bbaodanpianyi.setGeometry(QtCore.QRect(280, 150, 70, 16))
        self.label_Bbaodanpianyi.setObjectName(_fromUtf8("label_Bbaodanpianyi"))
        self.spinBox_Bbaodanpianyi = QtGui.QSpinBox(self.groupBox_trade_args)
        self.spinBox_Bbaodanpianyi.setGeometry(QtCore.QRect(356, 150, 46, 21))
        self.spinBox_Bbaodanpianyi.setMinimum(-999999999)
        self.spinBox_Bbaodanpianyi.setMaximum(999999999)
        self.spinBox_Bbaodanpianyi.setObjectName(_fromUtf8("spinBox_Bbaodanpianyi"))
        self.label_Abaodanpianyi = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Abaodanpianyi.setGeometry(QtCore.QRect(142, 150, 70, 16))
        self.label_Abaodanpianyi.setObjectName(_fromUtf8("label_Abaodanpianyi"))
        self.spinBox_Abaodanpianyi = QtGui.QSpinBox(self.groupBox_trade_args)
        self.spinBox_Abaodanpianyi.setGeometry(QtCore.QRect(216, 150, 46, 21))
        self.spinBox_Abaodanpianyi.setMinimum(-999999999)
        self.spinBox_Abaodanpianyi.setMaximum(999999999)
        self.spinBox_Abaodanpianyi.setObjectName(_fromUtf8("spinBox_Abaodanpianyi"))
        self.label_Aheyue = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Aheyue.setGeometry(QtCore.QRect(210, 30, 40, 16))
        self.label_Aheyue.setObjectName(_fromUtf8("label_Aheyue"))
        self.lineEdit_Aheyue = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Aheyue.setGeometry(QtCore.QRect(256, 30, 58, 21))
        self.lineEdit_Aheyue.setText(_fromUtf8(""))
        self.lineEdit_Aheyue.setObjectName(_fromUtf8("lineEdit_Aheyue"))
        self.label_Achengshu = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Achengshu.setGeometry(QtCore.QRect(326, 30, 30, 16))
        self.label_Achengshu.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_Achengshu.setObjectName(_fromUtf8("label_Achengshu"))
        self.lineEdit_Achengshu = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Achengshu.setGeometry(QtCore.QRect(362, 30, 40, 21))
        self.lineEdit_Achengshu.setObjectName(_fromUtf8("lineEdit_Achengshu"))
        self.lineEdit_Bheyue = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bheyue.setGeometry(QtCore.QRect(256, 60, 58, 21))
        self.lineEdit_Bheyue.setText(_fromUtf8(""))
        self.lineEdit_Bheyue.setObjectName(_fromUtf8("lineEdit_Bheyue"))
        self.lineEdit_Bchengshu = QtGui.QLineEdit(self.groupBox_trade_args)
        self.lineEdit_Bchengshu.setGeometry(QtCore.QRect(362, 60, 40, 21))
        self.lineEdit_Bchengshu.setObjectName(_fromUtf8("lineEdit_Bchengshu"))
        self.label_Bheyue = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bheyue.setGeometry(QtCore.QRect(210, 60, 40, 16))
        self.label_Bheyue.setObjectName(_fromUtf8("label_Bheyue"))
        self.label_Bchengshu = QtGui.QLabel(self.groupBox_trade_args)
        self.label_Bchengshu.setGeometry(QtCore.QRect(326, 60, 30, 16))
        self.label_Bchengshu.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_Bchengshu.setObjectName(_fromUtf8("label_Bchengshu"))
        self.verticalLayout.addWidget(self.splitter_qaccount)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_value_dongtaiquanyi.setText(_translate("Form", "0", None))
        self.label_dongtaiquanyi.setText(_translate("Form", "动态权益", None))
        self.label_jingtaiquanyi.setText(_translate("Form", "静态权益", None))
        self.label_value_jingtaiquanyi.setText(_translate("Form", "0", None))
        self.label_chicangyingkui.setText(_translate("Form", "持仓盈亏", None))
        self.label_value_chicangyingkui.setText(_translate("Form", "0", None))
        self.label_pingcangyingkui.setText(_translate("Form", "平仓盈亏", None))
        self.label_value_pingcangyingkui.setText(_translate("Form", "0", None))
        self.label_shouxufei.setText(_translate("Form", "手续费", None))
        self.label_value_shouxufei.setText(_translate("Form", "0", None))
        self.label_keyongzijin.setText(_translate("Form", "可用资金", None))
        self.label_value_keyongzijin.setText(_translate("Form", "0", None))
        self.label_zhanyongbaozhengjin.setText(_translate("Form", "占用保证金", None))
        self.label_value_zhanyongbaozhengjin.setText(_translate("Form", "0", None))
        self.label_fengxiandu.setText(_translate("Form", "风险度", None))
        self.label_value_fengxiandu.setText(_translate("Form", "0%", None))
        self.label_jinrirujin.setText(_translate("Form", "今日入金", None))
        self.label_value_jinrirujin.setText(_translate("Form", "0", None))
        self.label_jinrichujin.setText(_translate("Form", "今日出金", None))
        self.label_value_jinrichujin.setText(_translate("Form", "0", None))
        self.pushButton_query_account.setText(_translate("Form", "查询账户", None))
        self.pushButton_start_strategy.setText(_translate("Form", "开始策略", None))
        self.groupBox_trade_args.setTitle(_translate("Form", "策略参数", None))
        self.label_kongtoujiacha.setText(_translate("Form", "卖价差", None))
        self.label_qihuozhanghao.setText(_translate("Form", "期货账号", None))
        self.label_jiaoyimoxing.setText(_translate("Form", "交易模型", None))
        self.label_chaojiachufa.setText(_translate("Form", "超价触发", None))
        self.label_duotoujiacha.setText(_translate("Form", "买价差", None))
        self.checkBox_kongtoukai.setText(_translate("Form", "卖开", None))
        self.checkBox_duotouping.setText(_translate("Form", "卖平", None))
        self.checkBox_duotoukai.setText(_translate("Form", "买开", None))
        self.label_zongshou.setText(_translate("Form", "总手", None))
        self.checkBox_kongtouping.setText(_translate("Form", "买平", None))
        self.label_celuebianhao.setText(_translate("Form", "策略编号", None))
        self.label_xiadansuanfa.setText(_translate("Form", "下单算法", None))
        self.label_meifen.setText(_translate("Form", "每份", None))
        self.label_Adengdai.setText(_translate("Form", "A撤单等待", None))
        self.label_Bdengdai.setText(_translate("Form", "B撤单等待", None))
        self.label_Azongsell.setText(_translate("Form", "A总卖", None))
        self.label_Bzongbuy.setText(_translate("Form", "B总买", None))
        self.label_Azongbuy.setText(_translate("Form", "A总买", None))
        self.label_Bzongsell.setText(_translate("Form", "B总卖", None))
        self.label_Achedanxianzhi.setText(_translate("Form", "A限制", None))
        self.lineEdit_Achedanxianzhi.setText(_translate("Form", "480", None))
        self.label_Achedan.setText(_translate("Form", "A撤单", None))
        self.label_Bchedan.setText(_translate("Form", "B撤单", None))
        self.label_Ajinsell.setText(_translate("Form", "A昨卖", None))
        self.label_Bjinbuy.setText(_translate("Form", "B昨买", None))
        self.label_Ajinbuy.setText(_translate("Form", "A昨买", None))
        self.label_Bjinsell.setText(_translate("Form", "B昨卖", None))
        self.pushButton_liandongjia.setText(_translate("Form", "▲", None))
        self.pushButton_liandongjian.setText(_translate("Form", "▼", None))
        self.label_zhisun.setText(_translate("Form", "价差止损", None))
        self.pushButton_set_strategy.setText(_translate("Form", "发送", None))
        self.pushButton_query_strategy.setText(_translate("Form", "查询", None))
        self.label_Bchedanxianzhi.setText(_translate("Form", "B限制", None))
        self.lineEdit_Bchedanxianzhi.setText(_translate("Form", "480", None))
        self.lineEdit_zongshou.setText(_translate("Form", "1", None))
        self.lineEdit_meifen.setText(_translate("Form", "1", None))
        self.pushButton_set_position.setText(_translate("Form", "设置持仓", None))
        self.label_Bbaodanpianyi.setText(_translate("Form", "B报单偏移", None))
        self.label_Abaodanpianyi.setText(_translate("Form", "A报单偏移", None))
        self.label_Aheyue.setText(_translate("Form", "A合约", None))
        self.label_Achengshu.setText(_translate("Form", "乘数", None))
        self.lineEdit_Achengshu.setText(_translate("Form", "1", None))
        self.lineEdit_Bchengshu.setText(_translate("Form", "1", None))
        self.label_Bheyue.setText(_translate("Form", "B合约", None))
        self.label_Bchengshu.setText(_translate("Form", "乘数", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

