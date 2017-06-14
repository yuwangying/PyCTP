from PyQt4 import QtGui
import sys


class MessageBox(QtGui.QWidget):
    def __init__(self):
        super(MessageBox, self).__init__()
        self.msg_box = QtGui.QMessageBox(self)

    def showMessage(self, info_type, info_content):
        self.msg_box.about(self, info_type, info_content)
        # self.msg_box.show()

    def showMessage_list(self, list_input):
        self.msg_box.about(self, list_input[0], list_input[1])
        # self.msg_box.show()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MessageBox().showMessage("leixing", "hah")
    sys.exit(app.exec_())