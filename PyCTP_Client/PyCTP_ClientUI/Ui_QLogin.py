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
        LoginForm.resize(400, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginForm.sizePolicy().hasHeightForWidth())
        LoginForm.setSizePolicy(sizePolicy)
        LoginForm.setStyleSheet(_fromUtf8(""))
        self.verticalLayout = QtGui.QVBoxLayout(LoginForm)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_login_form = QtGui.QGroupBox(LoginForm)
        self.groupBox_login_form.setObjectName(_fromUtf8("groupBox_login_form"))
        self.pushButton_login = QtGui.QPushButton(self.groupBox_login_form)
        self.pushButton_login.setGeometry(QtCore.QRect(42, 210, 93, 28))
        self.pushButton_login.setObjectName(_fromUtf8("pushButton_login"))
        self.pushButton_cancel = QtGui.QPushButton(self.groupBox_login_form)
        self.pushButton_cancel.setGeometry(QtCore.QRect(154, 210, 93, 28))
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.label_trader_id = QtGui.QLabel(self.groupBox_login_form)
        self.label_trader_id.setGeometry(QtCore.QRect(42, 46, 83, 16))
        self.label_trader_id.setObjectName(_fromUtf8("label_trader_id"))
        self.lineEdit_trader_id = QtGui.QLineEdit(self.groupBox_login_form)
        self.lineEdit_trader_id.setGeometry(QtCore.QRect(154, 46, 113, 21))
        self.lineEdit_trader_id.setObjectName(_fromUtf8("lineEdit_trader_id"))
        self.label_trader_password = QtGui.QLabel(self.groupBox_login_form)
        self.label_trader_password.setGeometry(QtCore.QRect(42, 86, 83, 16))
        self.label_trader_password.setObjectName(_fromUtf8("label_trader_password"))
        self.lineEdit_trader_password = QtGui.QLineEdit(self.groupBox_login_form)
        self.lineEdit_trader_password.setGeometry(QtCore.QRect(154, 86, 113, 21))
        self.lineEdit_trader_password.setObjectName(_fromUtf8("lineEdit_trader_password"))
        self.checkBox_isoffline = QtGui.QCheckBox(self.groupBox_login_form)
        self.checkBox_isoffline.setGeometry(QtCore.QRect(42, 136, 91, 19))
        self.checkBox_isoffline.setObjectName(_fromUtf8("checkBox_isoffline"))
        self.label_login_error = QtGui.QLabel(self.groupBox_login_form)
        self.label_login_error.setGeometry(QtCore.QRect(154, 136, 187, 51))
        self.label_login_error.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.label_login_error.setText(_fromUtf8(""))
        self.label_login_error.setObjectName(_fromUtf8("label_login_error"))
        self.verticalLayout.addWidget(self.groupBox_login_form)

        self.retranslateUi(LoginForm)
        QtCore.QMetaObject.connectSlotsByName(LoginForm)

    def retranslateUi(self, LoginForm):
        LoginForm.setWindowTitle(_translate("LoginForm", "Form", None))
        self.groupBox_login_form.setTitle(_translate("LoginForm", "登录项", None))
        self.pushButton_login.setText(_translate("LoginForm", "登录", None))
        self.pushButton_cancel.setText(_translate("LoginForm", "取消", None))
        self.label_trader_id.setText(_translate("LoginForm", "交易员账户", None))
        self.label_trader_password.setText(_translate("LoginForm", "交易员密码", None))
        self.checkBox_isoffline.setText(_translate("LoginForm", "脱机登录", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LoginForm = QtGui.QWidget()
    ui = Ui_LoginForm()
    ui.setupUi(LoginForm)
    LoginForm.show()
    sys.exit(app.exec_())

