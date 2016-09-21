# -*- coding: utf-8 -*-

"""
Module implementing QCTP.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow

from Ui_QCTP import Ui_MainWindow


class QCTP(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QCTP, self).__init__(parent)
        self.setupUi(self)
