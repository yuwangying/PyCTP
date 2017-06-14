# -*- coding: utf-8 -*-

"""
Module implementing MessageCenter.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget
from PyQt4 import QtGui
import sys

from Ui_QMessageCenter import Ui_MessageForm


class MessageCenter(QWidget, Ui_MessageForm):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MessageCenter, self).__init__(parent)
        self.setupUi(self)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = MessageCenter()
    ex.show()
    sys.exit(app.exec_())
    pass
