# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\CTP\PyCTP\PyCTP_Client\PyCTP_ClientUI\QCTP.ui'
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1425, 900)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/image/bee.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralWidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralWidget.sizePolicy().hasHeightForWidth())
        self.centralWidget.setSizePolicy(sizePolicy)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setMargin(5)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter_mainwindow = QtGui.QSplitter(self.centralWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_mainwindow.sizePolicy().hasHeightForWidth())
        self.splitter_mainwindow.setSizePolicy(sizePolicy)
        self.splitter_mainwindow.setOrientation(QtCore.Qt.Vertical)
        self.splitter_mainwindow.setHandleWidth(2)
        self.splitter_mainwindow.setChildrenCollapsible(False)
        self.splitter_mainwindow.setObjectName(_fromUtf8("splitter_mainwindow"))
        self.widget_QAccountWidget = QAccountWidget(self.splitter_mainwindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_QAccountWidget.sizePolicy().hasHeightForWidth())
        self.widget_QAccountWidget.setSizePolicy(sizePolicy)
        self.widget_QAccountWidget.setObjectName(_fromUtf8("widget_QAccountWidget"))
        self.tab_records = QtGui.QTabWidget(self.splitter_mainwindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_records.sizePolicy().hasHeightForWidth())
        self.tab_records.setSizePolicy(sizePolicy)
        self.tab_records.setMinimumSize(QtCore.QSize(0, 330))
        self.tab_records.setObjectName(_fromUtf8("tab_records"))
        self.verticalLayout.addWidget(self.splitter_mainwindow)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1425, 26))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menu_file = QtGui.QMenu(self.menuBar)
        self.menu_file.setObjectName(_fromUtf8("menu_file"))
        self.menu_account = QtGui.QMenu(self.menuBar)
        self.menu_account.setObjectName(_fromUtf8("menu_account"))
        self.menu_market = QtGui.QMenu(self.menuBar)
        self.menu_market.setObjectName(_fromUtf8("menu_market"))
        self.menu_trademodel = QtGui.QMenu(self.menuBar)
        self.menu_trademodel.setObjectName(_fromUtf8("menu_trademodel"))
        self.menu_report = QtGui.QMenu(self.menuBar)
        self.menu_report.setObjectName(_fromUtf8("menu_report"))
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.menuBar.addAction(self.menu_file.menuAction())
        self.menuBar.addAction(self.menu_account.menuAction())
        self.menuBar.addAction(self.menu_market.menuAction())
        self.menuBar.addAction(self.menu_trademodel.menuAction())
        self.menuBar.addAction(self.menu_report.menuAction())

        self.retranslateUi(MainWindow)
        self.tab_records.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "小蜜蜂套利交易系统", None))
        self.menu_file.setTitle(_translate("MainWindow", "文件", None))
        self.menu_account.setTitle(_translate("MainWindow", "账户", None))
        self.menu_market.setTitle(_translate("MainWindow", "行情", None))
        self.menu_trademodel.setTitle(_translate("MainWindow", "交易模型", None))
        self.menu_report.setTitle(_translate("MainWindow", "报告", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))

from QAccountWidget import QAccountWidget
import img_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

