from PyQt4 import QtGui
import sys


class QMessageBox(QtGui.QWidget):
    def __init__(self):
        super(QMessageBox, self).__init__()

    def showMessage(self, info_type, info_content):
        QtGui.QMessageBox.about(self, info_type, info_content)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QMessageBox().showMessage("leixing", "hah")
    sys.exit(app.exec_())