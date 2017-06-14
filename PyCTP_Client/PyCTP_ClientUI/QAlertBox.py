# -*- coding: utf-8 -*-

"""
Module implementing QAlertBox.py.
"""

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QWidget

from .Ui_QAlertBox import Ui_Form


class QAlertBox.py(QWidget, Ui_Form):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(QAlertBox.py, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
