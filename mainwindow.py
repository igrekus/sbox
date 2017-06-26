import dbman
from suggestionmodel import SuggestionModel
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QDataWidgetMapper
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # super(MyDialog, self).__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # create instance variables
        self.ui = uic.loadUi("mw.ui", self)

        self.m_dbman = dbman.DbManager(self)

        self.m_model_suggestions = SuggestionModel(parent=self, dbmanager=self.m_dbman)
        self.m_model_search_proxy = QSortFilterProxyModel(self)
        self.m_model_search_proxy.setSourceModel(self.m_model_suggestions)

        self.m_data_mapper = QDataWidgetMapper(self)

        self.initApp()

    def initApp(self):
        # init instabces
        ok = self.m_dbman.connectToDatabase()
        if not ok:
            raise RuntimeError("Database connection problem.")

        # init models
        self.m_model_suggestions.initModel()

        self.m_data_mapper.setModel(self.m_model_search_proxy)
        # self.m_data_mapper.setModel(self.m_model_suggestions)
        self.m_data_mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.m_data_mapper.setOrientation(Qt.Horizontal)
        self.m_data_mapper.addMapping(self.ui.editId, 0)
        self.m_data_mapper.addMapping(self.ui.textText, 1)
        self.m_data_mapper.addMapping(self.ui.editAuthor, 2)
        self.m_data_mapper.addMapping(self.ui.editApprover, 3)
        self.m_data_mapper.addMapping(self.ui.radioActive, 4)
        self.m_data_mapper.toFirst()

        # init UI
        # self.ui.tableSuggestions.setModel(self.m_model_search_proxy)
        # self.ui.tableSuggestions.setModel(self.m_model_suggestions)
        self.ui.tableSuggestions.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableSuggestions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableSuggestions.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableSuggestions.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.ui.tableSuggestions.horizontalHeader().setHighlightSections(False)
        self.ui.tableSuggestions.horizontalHeader().setFixedHeight(24)
        self.ui.tableSuggestions.horizontalHeader().setStretchLastSection(True)
        self.ui.tableSuggestions.verticalHeader().setVisible(False)
        self.ui.tableSuggestions.verticalHeader().setDefaultSectionSize(20)

        self.refreshView()
        self.show()
        self.m_data_mapper.setCurrentIndex(0)

    def refreshView(self):
        twidth = self.ui.tableSuggestions.frameGeometry().width() - 30
        self.ui.tableSuggestions.hide()
        self.ui.tableSuggestions.setColumnWidth(0, twidth * 0.05)
        self.ui.tableSuggestions.setColumnWidth(1, twidth * 0.70)
        self.ui.tableSuggestions.setColumnWidth(2, twidth * 0.10)
        self.ui.tableSuggestions.setColumnWidth(3, twidth * 0.10)
        self.ui.tableSuggestions.setColumnWidth(4, twidth * 0.05)
        self.ui.tableSuggestions.show()

    def resizeEvent(self, event):
        self.refreshView()
