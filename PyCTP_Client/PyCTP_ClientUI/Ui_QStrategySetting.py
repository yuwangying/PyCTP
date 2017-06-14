# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\CTP\PyCTP\PyCTP_Client\PyCTP_ClientUI\QStrategySetting.ui'
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

class Ui_NewStrategy(object):
    def setupUi(self, NewStrategy):
        NewStrategy.setObjectName(_fromUtf8("NewStrategy"))
        NewStrategy.resize(326, 294)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(NewStrategy.sizePolicy().hasHeightForWidth())
        NewStrategy.setSizePolicy(sizePolicy)
        NewStrategy.setMinimumSize(QtCore.QSize(326, 294))
        NewStrategy.setMaximumSize(QtCore.QSize(326, 294))
        NewStrategy.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 245);"))
        self.label_user_id = QtGui.QLabel(NewStrategy)
        self.label_user_id.setGeometry(QtCore.QRect(40, 40, 117, 16))
        self.label_user_id.setObjectName(_fromUtf8("label_user_id"))
        self.label_strategy_id = QtGui.QLabel(NewStrategy)
        self.label_strategy_id.setGeometry(QtCore.QRect(40, 80, 117, 16))
        self.label_strategy_id.setObjectName(_fromUtf8("label_strategy_id"))
        self.label_a_instrument = QtGui.QLabel(NewStrategy)
        self.label_a_instrument.setGeometry(QtCore.QRect(40, 120, 117, 16))
        self.label_a_instrument.setObjectName(_fromUtf8("label_a_instrument"))
        self.label_b_instrument = QtGui.QLabel(NewStrategy)
        self.label_b_instrument.setGeometry(QtCore.QRect(40, 160, 117, 16))
        self.label_b_instrument.setObjectName(_fromUtf8("label_b_instrument"))
        self.comboBox_user_id = QtGui.QComboBox(NewStrategy)
        self.comboBox_user_id.setGeometry(QtCore.QRect(160, 40, 117, 21))
        self.comboBox_user_id.setObjectName(_fromUtf8("comboBox_user_id"))
        self.lineEdit_a_instrument = QtGui.QLineEdit(NewStrategy)
        self.lineEdit_a_instrument.setGeometry(QtCore.QRect(160, 120, 117, 21))
        self.lineEdit_a_instrument.setObjectName(_fromUtf8("lineEdit_a_instrument"))
        self.lineEdit_b_instrument = QtGui.QLineEdit(NewStrategy)
        self.lineEdit_b_instrument.setGeometry(QtCore.QRect(160, 160, 117, 21))
        self.lineEdit_b_instrument.setObjectName(_fromUtf8("lineEdit_b_instrument"))
        self.pushButton_cancel = QtGui.QPushButton(NewStrategy)
        self.pushButton_cancel.setGeometry(QtCore.QRect(167, 240, 110, 28))
        self.pushButton_cancel.setStyleSheet(_fromUtf8("QPushButton{\n"
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
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.pushButton_ok = QtGui.QPushButton(NewStrategy)
        self.pushButton_ok.setGeometry(QtCore.QRect(40, 240, 110, 28))
        self.pushButton_ok.setStyleSheet(_fromUtf8("QPushButton{\n"
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
        self.pushButton_ok.setObjectName(_fromUtf8("pushButton_ok"))
        self.label_error_msg = QtGui.QLabel(NewStrategy)
        self.label_error_msg.setGeometry(QtCore.QRect(42, 192, 237, 37))
        self.label_error_msg.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.label_error_msg.setText(_fromUtf8(""))
        self.label_error_msg.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_error_msg.setObjectName(_fromUtf8("label_error_msg"))
        self.lineEdit_strategy_id = QtGui.QLineEdit(NewStrategy)
        self.lineEdit_strategy_id.setGeometry(QtCore.QRect(160, 80, 117, 21))
        self.lineEdit_strategy_id.setObjectName(_fromUtf8("lineEdit_strategy_id"))

        self.retranslateUi(NewStrategy)
        QtCore.QMetaObject.connectSlotsByName(NewStrategy)
        NewStrategy.setTabOrder(self.comboBox_user_id, self.lineEdit_strategy_id)
        NewStrategy.setTabOrder(self.lineEdit_strategy_id, self.lineEdit_a_instrument)
        NewStrategy.setTabOrder(self.lineEdit_a_instrument, self.lineEdit_b_instrument)
        NewStrategy.setTabOrder(self.lineEdit_b_instrument, self.pushButton_ok)
        NewStrategy.setTabOrder(self.pushButton_ok, self.pushButton_cancel)

    def retranslateUi(self, NewStrategy):
        NewStrategy.setWindowTitle(_translate("NewStrategy", "新建策略", None))
        self.label_user_id.setText(_translate("NewStrategy", "期货账号", None))
        self.label_strategy_id.setText(_translate("NewStrategy", "策略编号", None))
        self.label_a_instrument.setText(_translate("NewStrategy", "A合约代码", None))
        self.label_b_instrument.setText(_translate("NewStrategy", "B合约代码", None))
        self.pushButton_cancel.setText(_translate("NewStrategy", "取消", None))
        self.pushButton_ok.setText(_translate("NewStrategy", "确定", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    NewStrategy = QtGui.QWidget()
    ui = Ui_NewStrategy()
    ui.setupUi(NewStrategy)
    NewStrategy.show()
    sys.exit(app.exec_())

