# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\CTP\PyCTP\PyCTP_Client\PyCTP_ClientUI\QMessageCenter.ui'
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

class Ui_MessageForm(object):
    def setupUi(self, MessageForm):
        MessageForm.setObjectName(_fromUtf8("MessageForm"))
        MessageForm.resize(1425, 33)
        self.horizontalLayout = QtGui.QHBoxLayout(MessageForm)
        self.horizontalLayout.setContentsMargins(10, 0, 5, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_message = QtGui.QLabel(MessageForm)
        self.label_message.setObjectName(_fromUtf8("label_message"))
        self.horizontalLayout.addWidget(self.label_message)
        self.line = QtGui.QFrame(MessageForm)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.label_trade_connect_status = QtGui.QLabel(MessageForm)
        self.label_trade_connect_status.setObjectName(_fromUtf8("label_trade_connect_status"))
        self.horizontalLayout.addWidget(self.label_trade_connect_status)
        self.line_2 = QtGui.QFrame(MessageForm)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.horizontalLayout.addWidget(self.line_2)
        self.label_market_connect_status = QtGui.QLabel(MessageForm)
        self.label_market_connect_status.setObjectName(_fromUtf8("label_market_connect_status"))
        self.horizontalLayout.addWidget(self.label_market_connect_status)
        self.line_3 = QtGui.QFrame(MessageForm)
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.horizontalLayout.addWidget(self.line_3)
        self.label_CFFEX_time = QtGui.QLabel(MessageForm)
        self.label_CFFEX_time.setObjectName(_fromUtf8("label_CFFEX_time"))
        self.horizontalLayout.addWidget(self.label_CFFEX_time)
        self.line_4 = QtGui.QFrame(MessageForm)
        self.line_4.setFrameShape(QtGui.QFrame.VLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.horizontalLayout.addWidget(self.line_4)
        self.label_SHFE_time = QtGui.QLabel(MessageForm)
        self.label_SHFE_time.setObjectName(_fromUtf8("label_SHFE_time"))
        self.horizontalLayout.addWidget(self.label_SHFE_time)
        self.line_5 = QtGui.QFrame(MessageForm)
        self.line_5.setFrameShape(QtGui.QFrame.VLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName(_fromUtf8("line_5"))
        self.horizontalLayout.addWidget(self.line_5)
        self.label_CZCE_time = QtGui.QLabel(MessageForm)
        self.label_CZCE_time.setObjectName(_fromUtf8("label_CZCE_time"))
        self.horizontalLayout.addWidget(self.label_CZCE_time)
        self.line_6 = QtGui.QFrame(MessageForm)
        self.line_6.setFrameShape(QtGui.QFrame.VLine)
        self.line_6.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_6.setObjectName(_fromUtf8("line_6"))
        self.horizontalLayout.addWidget(self.line_6)
        self.label_DCE_time = QtGui.QLabel(MessageForm)
        self.label_DCE_time.setObjectName(_fromUtf8("label_DCE_time"))
        self.horizontalLayout.addWidget(self.label_DCE_time)
        self.horizontalLayout.setStretch(0, 14)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)
        self.horizontalLayout.setStretch(4, 1)
        self.horizontalLayout.setStretch(5, 1)
        self.horizontalLayout.setStretch(6, 1)
        self.horizontalLayout.setStretch(7, 1)
        self.horizontalLayout.setStretch(8, 1)
        self.horizontalLayout.setStretch(9, 1)
        self.horizontalLayout.setStretch(10, 1)
        self.horizontalLayout.setStretch(11, 1)
        self.horizontalLayout.setStretch(12, 1)

        self.retranslateUi(MessageForm)
        QtCore.QMetaObject.connectSlotsByName(MessageForm)

    def retranslateUi(self, MessageForm):
        MessageForm.setWindowTitle(_translate("MessageForm", "MessageCenter", None))
        self.label_message.setText(_translate("MessageForm", "SHFE:收盘", None))
        self.label_trade_connect_status.setText(_translate("MessageForm", "交易连接", None))
        self.label_market_connect_status.setText(_translate("MessageForm", "行情连接", None))
        self.label_CFFEX_time.setText(_translate("MessageForm", "15:00:10", None))
        self.label_SHFE_time.setText(_translate("MessageForm", "15:00:10", None))
        self.label_CZCE_time.setText(_translate("MessageForm", "15:00:10", None))
        self.label_DCE_time.setText(_translate("MessageForm", "15:00:10", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MessageForm = QtGui.QWidget()
    ui = Ui_MessageForm()
    ui.setupUi(MessageForm)
    MessageForm.show()
    sys.exit(app.exec_())

