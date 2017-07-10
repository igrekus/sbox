import sys
import dbman
import typedefs
import logindialog
from mapmodel import MapModel
from suggestionmodel import SuggestionModel
from suggestionsearchproxymodel import SuggestionSearchProxyModel
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QDataWidgetMapper, QMessageBox, QDialog
from PyQt5.QtCore import Qt, QItemSelectionModel, QByteArray


# TODO record commentaries from other users
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self.ui = uic.loadUi("mw.ui", self)

        self._dbman = dbman.DbManager(self)

        self._model_authors = MapModel(self)

        # self._model_search_proxy = QSortFilterProxyModel(self)
        self._model_suggestions = SuggestionModel(parent=self, dbmanager=self._dbman)
        self._model_search_proxy = SuggestionSearchProxyModel(self)
        self._model_search_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._model_search_proxy.setSourceModel(self._model_suggestions)

        self._data_mapper = QDataWidgetMapper(self)

        self._logged_user = {}

        self.initDialog()

    def closeEvent(self, event):
        if not self._logged_user:
            event.accept()
            sys.exit(10)

        result = QMessageBox.question(self, "Вопрос", "Завершить работу?\nВсе данные будут сохранены.")
        if result != QMessageBox.Yes:
            print("Cancel quit.")
            event.ignore()
            return

        self._model_suggestions.saveDirtyData()
        print("Accept quit.")
        event.accept()

    def logIn(self, users):
        dialog = logindialog.LoginDialog(parent=self, users=users, dbman=self._dbman)
        if dialog.exec() == QDialog.Accepted:
            self._logged_user = dialog.logged_user
            return True
        return False

    def initDialog(self):
        self.ui.btnReject.setVisible(False)
        self.ui.btnApprove.setVisible(False)
        self.show()

        # setup db connection
        ok, error_text = self._dbman.connectToDatabase()
        if not ok:
            # TODO error handling
            QMessageBox.warning(self, "Ошибка!",
                                "Ошибка инииализации:\n\n" + error_text + "\n\nОбратитесь к разработчику ПО.")
            self.close()

        # init models
        self._model_suggestions.initModel()

        # login
        if not self.logIn(self._model_suggestions._users):
            self.close()
            return
        self.setWindowTitle(self.windowTitle() + ", пользователь: " + self._logged_user["name"])

        self._model_authors.initModel(self._model_suggestions._users)

        # init instances
        self._data_mapper.setModel(self._model_search_proxy)
        self._data_mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self._data_mapper.setOrientation(Qt.Horizontal)
        self._data_mapper.addMapping(self.ui.editId, 0)
        self._data_mapper.addMapping(self.ui.textText, 2)
        self._data_mapper.addMapping(self.ui.editAuthor, 3)
        self._data_mapper.addMapping(self.ui.editApprover, 4)
        self._data_mapper.addMapping(self.ui.checkActive, 5)

        # init UI
        self.ui.comboAuthorFilter.setModel(self._model_authors)

        self.ui.tableSuggestions.setModel(self._model_search_proxy)
        self.ui.tableSuggestions.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableSuggestions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableSuggestions.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableSuggestions.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.ui.tableSuggestions.horizontalHeader().setHighlightSections(False)
        self.ui.tableSuggestions.horizontalHeader().setFixedHeight(24)
        self.ui.tableSuggestions.horizontalHeader().setStretchLastSection(True)
        self.ui.tableSuggestions.verticalHeader().setVisible(False)
        self.ui.tableSuggestions.verticalHeader().setDefaultSectionSize(20)

        self.ui.btnSave.setEnabled(False)

        # setup signals
        # table
        self.ui.tableSuggestions.selectionModel().currentChanged.connect(self.onSelectionChanged)
        self.ui.tableSuggestions.clicked.connect(self.onTableClicked)
        # buttons
        self.ui.btnAdd.clicked.connect(self.onBtnAddClicked)
        self.ui.btnDel.clicked.connect(self.onBtnDelClicked)
        self.ui.btnSave.clicked.connect(self.onBtnSaveClicked)
        self.ui.btnApprove.clicked.connect(self.onBtnApproveClicked)
        self.ui.btnReject.clicked.connect(self.onBtnRejectClicked)
        # data input widgets
        self.ui.textText.textChanged.connect(self.onTextChanged)
        self.ui.checkActive.stateChanged.connect(self.onCheckClicked)
        # search widgets
        self.ui.editSearch.textChanged.connect(self.onEditSearchTextChanged)
        self.ui.comboAuthorFilter.currentIndexChanged.connect(self.onComboAuthorFilterIndexChanged)
        self.ui.comboActiveFilter.currentIndexChanged.connect(self.onComboActiveFilterIndexChanged)
        self.ui.comboStatusFilter.currentIndexChanged.connect(self.onComboStatusFilterIndexChanged)

        # update UI depending on user level
        self.setupControls()
        self.refreshView()

    # UI utility methods
    def refreshView(self):
        twidth = self.ui.tableSuggestions.frameGeometry().width() - 30
        self.ui.tableSuggestions.setColumnWidth(0, twidth * 0.05)
        self.ui.tableSuggestions.setColumnWidth(1, twidth * 0.10)
        self.ui.tableSuggestions.setColumnWidth(2, twidth * 0.55)
        self.ui.tableSuggestions.setColumnWidth(3, twidth * 0.10)
        self.ui.tableSuggestions.setColumnWidth(4, twidth * 0.15)
        self.ui.tableSuggestions.setColumnWidth(5, twidth * 0.05)

    def setupControls(self):
        if self._logged_user["level"] == typedefs.LevelAdmin:
            self.ui.btnApprove.setVisible(True)
            self.ui.btnReject.setVisible(True)
            self.ui.checkActive.setEnabled(True)
            # self.ui.textText.setEnabled(True)
            self.ui.textText.setReadOnly(False)
            self.ui.btnDel.setEnabled(True)

    def updateUiControls(self):
        self._model_search_proxy.invalidate()
        if self._model_suggestions.has_dirty_data:
            self.ui.btnSave.setEnabled(True)
        else:
            self.ui.btnSave.setEnabled(False)

    # business logic
    def addSuggestion(self):
        source_index = self._model_suggestions.addSuggestionRecord(self._logged_user["id"])

        index_to_select = self._model_search_proxy.mapFromSource(source_index)
        self.ui.tableSuggestions.selectionModel().clear()
        self.ui.tableSuggestions.selectionModel().setCurrentIndex(index_to_select, QItemSelectionModel.Select
                                                                  | QItemSelectionModel.Rows)
        self.updateUiControls()

    def saveSuggestions(self):
        self._model_suggestions.saveDirtyData()
        self.updateUiControls()

    def delSuggestion(self, index):
        self._model_suggestions.deleteSuggestionRecordAtIndex(index)

    def updateSuggestionData(self):
        self._data_mapper.submit()
        self.updateUiControls()

    def approveSuggestion(self, index):
        status = index.data(typedefs.RoleStatus)
        if status == typedefs.StatusApproved:
            QMessageBox.information(self, "Ошибка", "Предложение уже одобрено.")
            return
        elif status == typedefs.StatusRejected:
            result = QMessageBox.question(self, "Вопрос", "Одобрить уже отклонённое предложение?")
            if result != QMessageBox.Yes:
                return

        self._model_suggestions.approveSuggestion(index, self._logged_user["id"])
        self.updateUiControls()

    def rejectSuggestion(self, index):
        status = index.data(typedefs.RoleStatus)
        if status == typedefs.StatusRejected:
            QMessageBox.information(self, "Ошибка", "Предложение уже отклонено.")
            return
        elif status == typedefs.StatusApproved:
            result = QMessageBox.question(self, "Вопрос", "Отклонить уже одобренное предложение?")
            if result != QMessageBox.Yes:
                return

        self._model_suggestions.rejectSuggestion(index, self._logged_user["id"])
        self.updateUiControls()

    # event handlers
    def resizeEvent(self, event):
        self.refreshView()

    def onSelectionChanged(self, current, previous):
        if not self.ui.tableSuggestions.selectionModel().hasSelection():
            return

        # TODO extract access rights check to a separate method
        current_mapped = self._model_search_proxy.mapToSource(current)
        if self._logged_user["level"] != typedefs.LevelAdmin:
            if current_mapped.data(typedefs.RoleAuthor) == self._logged_user["id"]:
                self.ui.checkActive.setEnabled(True)
                # self.ui.textText.setEnabled(True)
                self.ui.textText.setReadOnly(False)
                self.ui.btnDel.setEnabled(True)
            else:
                self.ui.checkActive.setEnabled(False)
                # self.ui.textText.setEnabled(False)
                self.ui.textText.setReadOnly(True)
                self.ui.btnDel.setEnabled(False)

        self._data_mapper.setCurrentModelIndex(current)

    def onTableClicked(self, index):
        self._data_mapper.setCurrentModelIndex(index)

    def onBtnAddClicked(self):
        self.addSuggestion()

    def onBtnSaveClicked(self):
        self.saveSuggestions()

    def onBtnDelClicked(self):
        if not self.ui.tableSuggestions.selectionModel().hasSelection():
            QMessageBox.information(self, "Ошибка", "Удалить: пожалуйста, выберите запись.")
            return

        selected_index = self.ui.tableSuggestions.selectionModel().selectedIndexes()[0]
        index_to_delete = self._model_search_proxy.mapToSource(selected_index)

        # TODO extract permission checks to a separate method(object)?
        if self._logged_user["level"] != typedefs.LevelAdmin and \
                        index_to_delete.data(typedefs.RoleAuthor) != self._logged_user["id"]:
            QMessageBox.warning(self, "Ошибка", "У вас недостаточно прав для удаления данной записи.")
            return

        result = QMessageBox.question(self, "Внимание!", "Вы действительно хотите удалить выбранную запись?")
        if result != QMessageBox.Yes:
            return

        self.delSuggestion(index_to_delete)

    def onBtnApproveClicked(self):
        if not self.ui.tableSuggestions.selectionModel().hasSelection():
            QMessageBox.information(self, "Ошибка", "Одобрить: пожалуйста, выберите запись.")
            return

        selected_index = self.ui.tableSuggestions.selectionModel().selectedIndexes()[0]
        index_to_approve = self._model_search_proxy.mapToSource(selected_index)
        self.approveSuggestion(index_to_approve)

    def onBtnRejectClicked(self):
        if not self.ui.tableSuggestions.selectionModel().hasSelection():
            QMessageBox.information(self, "Ошибка", "Отклонить: пожалуйста, выберите запись.")
            return

        selected_index = self.ui.tableSuggestions.selectionModel().selectedIndexes()[0]
        index_to_reject = self._model_search_proxy.mapToSource(selected_index)
        self.rejectSuggestion(index_to_reject)

    def onTextChanged(self):
        if self.ui.textText.hasFocus():
            self.updateSuggestionData()

    def onCheckClicked(self, checked):
        if self.ui.checkActive.hasFocus():
            self.updateSuggestionData()

    def onComboAuthorFilterIndexChanged(self, index):
        self._model_search_proxy.filterAuthor = self.ui.comboAuthorFilter.currentData(typedefs.RoleNodeId)
        self._model_search_proxy.invalidate()

    def onComboActiveFilterIndexChanged(self, index):
        self._model_search_proxy.filterActive = index
        self._model_search_proxy.invalidate()

    def onComboStatusFilterIndexChanged(self, index):
        self._model_search_proxy.filterStatus = index
        self._model_search_proxy.invalidate()

    def onEditSearchTextChanged(self, text):
        self._model_search_proxy.filterString = text
        self._model_search_proxy.invalidate()
