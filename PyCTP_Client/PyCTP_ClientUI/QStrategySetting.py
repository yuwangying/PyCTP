# -*- coding: utf-8 -*-

"""
Module implementing NewStrategy.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget

from .Ui_QStrategySetting import Ui_NewStrategy


class NewStrategy(QWidget, Ui_NewStrategy):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(NewStrategy, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_pushButton_cancel_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSlot()
    def on_pushButton_ok_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
