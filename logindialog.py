from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, parent=None, users=None, dbman=None):
        super(LoginDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self.ui = uic.loadUi("logindialog.ui", self)

        self._dbman = dbman
        self._users = users

        self._logged_user = {}

        # setup signals
        self.ui.btnOk.clicked.connect(self.onInputComplete)

        #
        self.initDialog()

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, d):
        if d is not None:
            self._users = d

    @property
    def logged_user(self):
        return self._logged_user

    def initDialog(self):
        self.ui.comboLogin.addItems(self._users.values())

    def onInputComplete(self):
        usr = self.ui.comboLogin.currentText()
        pw = self.ui.editPass.text()
        id_ = 0
        for id_, name in self._users.items():
            if name == usr:
                break

        ok, level = self._dbman.checkLogin(id_, pw)
        if not ok:
            QMessageBox.warning(self, "Ошибка", "Введите правильный пароль.")
            self.ui.editPass.setFocus()
            self.ui.editPass.selectAll()
            return

        self._logged_user = {"id": id_, "name": usr, "level": level}
        self.accept()
