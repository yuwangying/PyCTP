# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\CTP\PyCTP\PyCTP_Client\PyCTP_ClientUI\QLogin.ui'
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

class Ui_LoginForm(object):
    def setupUi(self, LoginForm):
        LoginForm.setObjectName(_fromUtf8("LoginForm"))
        LoginForm.setEnabled(True)
        LoginForm.resize(881, 600)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginForm.sizePolicy().hasHeightForWidth())
        LoginForm.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/image/bee.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LoginForm.setWindowIcon(icon)
        LoginForm.setStyleSheet(_fromUtf8("font: 100 10pt \"微软雅黑\";\n"
"background-color: rgb(188, 247, 255);\n"
"background-color: rgb(255, 255, 245);\n"
""))
        self.groupBox_login_form = QtGui.QGroupBox(LoginForm)
        self.groupBox_login_form.setGeometry(QtCore.QRect(482, 280, 379, 253))
        self.groupBox_login_form.setStyleSheet(_fromUtf8("border:none;\n"
"background:transparent;\n"
""))
        self.groupBox_login_form.setTitle(_fromUtf8(""))
        self.groupBox_login_form.setObjectName(_fromUtf8("groupBox_login_form"))
        self.pushButton_login = QtGui.QPushButton(self.groupBox_login_form)
        self.pushButton_login.setGeometry(QtCore.QRect(60, 200, 130, 50))
        self.pushButton_login.setStyleSheet(_fromUtf8("QPushButton {\n"
"      border: 2px solid #8f8f91;\n"
"      border-radius: 6px;\n"
"      background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                        stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
"      min-width: 80px;\n"
"  }\n"
"\n"
"  QPushButton:pressed {\n"
"      background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                        stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
"  }\n"
"\n"
"  QPushButton:flat {\n"
"      border: none; /* no border for a flat push button */\n"
"  }\n"
"\n"
"  QPushButton:default {\n"
"      border-color: navy; /* make the default button prominent */\n"
"  }"))
        self.pushButton_login.setObjectName(_fromUtf8("pushButton_login"))
        self.pushButton_cancel = QtGui.QPushButton(self.groupBox_login_form)
        self.pushButton_cancel.setGeometry(QtCore.QRect(200, 200, 130, 50))
        self.pushButton_cancel.setStyleSheet(_fromUtf8("QPushButton {\n"
"      border: 2px solid #8f8f91;\n"
"      border-radius: 6px;\n"
"      background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                        stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
"      min-width: 80px;\n"
"  }\n"
"\n"
"  QPushButton:pressed {\n"
"      background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                        stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
"  }\n"
"\n"
"  QPushButton:flat {\n"
"      border: none; /* no border for a flat push button */\n"
"  }\n"
"\n"
"  QPushButton:default {\n"
"      border-color: navy; /* make the default button prominent */\n"
"  }"))
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.label_trader_id = QtGui.QLabel(self.groupBox_login_form)
        self.label_trader_id.setGeometry(QtCore.QRect(60, 43, 90, 16))
        self.label_trader_id.setObjectName(_fromUtf8("label_trader_id"))
        self.lineEdit_trader_id = QtGui.QLineEdit(self.groupBox_login_form)
        self.lineEdit_trader_id.setGeometry(QtCore.QRect(190, 40, 130, 27))
        self.lineEdit_trader_id.setStyleSheet(_fromUtf8("border:1px solid black;"))
        self.lineEdit_trader_id.setObjectName(_fromUtf8("lineEdit_trader_id"))
        self.label_trader_password = QtGui.QLabel(self.groupBox_login_form)
        self.label_trader_password.setGeometry(QtCore.QRect(60, 86, 90, 16))
        self.label_trader_password.setObjectName(_fromUtf8("label_trader_password"))
        self.lineEdit_trader_password = QtGui.QLineEdit(self.groupBox_login_form)
        self.lineEdit_trader_password.setGeometry(QtCore.QRect(190, 80, 130, 27))
        self.lineEdit_trader_password.setStyleSheet(_fromUtf8("border:1px solid black;"))
        self.lineEdit_trader_password.setObjectName(_fromUtf8("lineEdit_trader_password"))
        self.checkBox_isoffline = QtGui.QCheckBox(self.groupBox_login_form)
        self.checkBox_isoffline.setEnabled(False)
        self.checkBox_isoffline.setGeometry(QtCore.QRect(60, 120, 90, 19))
        self.checkBox_isoffline.setObjectName(_fromUtf8("checkBox_isoffline"))
        self.label_login_error = QtGui.QLabel(self.groupBox_login_form)
        self.label_login_error.setGeometry(QtCore.QRect(60, 160, 247, 23))
        self.label_login_error.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.label_login_error.setText(_fromUtf8(""))
        self.label_login_error.setObjectName(_fromUtf8("label_login_error"))
        self.label_login_image = QtGui.QLabel(LoginForm)
        self.label_login_image.setGeometry(QtCore.QRect(0, 0, 957, 599))
        self.label_login_image.setStyleSheet(_fromUtf8("background: url(:/image/login_bee.png) no-repeat;\n"
""))
        self.label_login_image.setText(_fromUtf8(""))
        self.label_login_image.setObjectName(_fromUtf8("label_login_image"))
        self.label_software_name = QtGui.QLabel(LoginForm)
        self.label_software_name.setGeometry(QtCore.QRect(590, 118, 265, 103))
        self.label_software_name.setObjectName(_fromUtf8("label_software_name"))
        self.label_version = QtGui.QLabel(LoginForm)
        self.label_version.setGeometry(QtCore.QRect(14, 557, 105, 27))
        self.label_version.setAlignment(QtCore.Qt.AlignCenter)
        self.label_version.setObjectName(_fromUtf8("label_version"))
        self.label_login_image.raise_()
        self.label_software_name.raise_()
        self.label_version.raise_()
        self.groupBox_login_form.raise_()

        self.retranslateUi(LoginForm)
        QtCore.QMetaObject.connectSlotsByName(LoginForm)
        LoginForm.setTabOrder(self.lineEdit_trader_id, self.lineEdit_trader_password)
        LoginForm.setTabOrder(self.lineEdit_trader_password, self.checkBox_isoffline)
        LoginForm.setTabOrder(self.checkBox_isoffline, self.pushButton_login)
        LoginForm.setTabOrder(self.pushButton_login, self.pushButton_cancel)

    def retranslateUi(self, LoginForm):
        LoginForm.setWindowTitle(_translate("LoginForm", "小蜜蜂套利交易系统", None))
        self.pushButton_login.setText(_translate("LoginForm", "登录", None))
        self.pushButton_login.setShortcut(_translate("LoginForm", "Return", None))
        self.pushButton_cancel.setText(_translate("LoginForm", "取消", None))
        self.pushButton_cancel.setShortcut(_translate("LoginForm", "Esc", None))
        self.label_trader_id.setText(_translate("LoginForm", "交易员账户", None))
        self.label_trader_password.setText(_translate("LoginForm", "交易员密码", None))
        self.checkBox_isoffline.setText(_translate("LoginForm", "脱机登录", None))
        self.label_software_name.setText(_translate("LoginForm", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'微软雅黑\'; font-size:10pt; font-weight:96; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600; color:#595959;\">小蜜蜂套利系统</span></p></body></html>", None))
        self.label_version.setText(_translate("LoginForm", "<html><head/><body><p><span style=\" font-weight:400;\">1.0</span></p></body></html>", None))

import img_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LoginForm = QtGui.QWidget()
    ui = Ui_LoginForm()
    ui.setupUi(LoginForm)
    LoginForm.show()
    sys.exit(app.exec_())

