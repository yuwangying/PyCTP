# -*- coding: utf-8 -*-

"""
Module implementing QAlertBox.py.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget
from PyQt4 import QtGui, QtCore

from Ui_QAlertBox import Ui_Form


class QAlertBox(QWidget, Ui_Form):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QAlertBox, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass
        self.hide()

    # 形参：{窗口标题, 消息主体}
    def slot_show_alert(self, dict_input):
        self.setWindowTitle(dict_input['title'])
        self.label.setText(dict_input['main'])
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        # this will activate the window
        self.activateWindow()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    abox = QAlertBox()
    abox.label.setText("haha")  # 消息主体
    abox.setWindowTitle("提示")  # 窗口标题
    abox.show()
    sys.exit(app.exec_())