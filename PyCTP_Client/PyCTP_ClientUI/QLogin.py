# -*- coding: utf-8 -*-

"""
Module implementing QLoginForm.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget
from PyQt4 import QtGui

from Ui_QLogin import Ui_LoginForm


class QLoginForm(QWidget, Ui_LoginForm):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QLoginForm, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_pushButton_login_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSlot()
    def on_pushButton_cancel_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSlot(bool)
    def on_checkBox_isoffline_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSlot(int)
    def on_checkBox_isoffline_stateChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type int
        """
        # TODO: not implemented yet
        raise NotImplementedError

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QLoginForm()
    Form.show()
    sys.exit(app.exec_())
