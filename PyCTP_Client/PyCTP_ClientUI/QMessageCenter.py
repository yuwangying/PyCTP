# -*- coding: utf-8 -*-

"""
Module implementing MessageCenter.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget

from .Ui_QMessageCenter import Ui_MessageForm


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
