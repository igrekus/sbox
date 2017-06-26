import typedefs
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QBrush, QColor


class SuggestionModel(QAbstractTableModel):
    ColumnId = 0
    ColumnText = ColumnId + 1
    ColumnAuthor = ColumnText + 1
    ColumnApprover = ColumnAuthor + 1
    ColumnActive = ColumnApprover + 1
    ColumnCount = ColumnActive + 1

    m_headers = ["Номер", "Текст", "Автор", "Одобрил", "Активно"]

    def __init__(self, parent=None, dbmanager=None):
        super(SuggestionModel, self).__init__(parent)

        self.m_dbman = dbmanager
        self.m_data = list()
        self.m_users = dict()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, )

    def initModel(self):
        print("init suggestion model")
        self.m_users = self.m_dbman.getUserDict()

        tmplst = self.m_dbman.getSuggestionList()
        self.beginInsertRows(QModelIndex(), 0, len(tmplst)-1)
        self.m_data = tmplst
        self.endInsertRows()

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self.m_headers):
            return QVariant(self.m_headers[section])
        return QVariant()

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.isValid():
            return 0
        return len(self.m_data)

    def columnCount(self, parent=None, *args, **kwargs):
        return self.ColumnCount

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()

        print("data call")
        col = index.column()
        row = index.row()
        if role == Qt.DisplayRole:
            if col == self.ColumnId:
                return QVariant(self.m_data[row].item_id)
            elif col == self.ColumnText:
                return QVariant(self.m_data[row].item_text)
            elif col == self.ColumnAuthor:
                return QVariant(self.m_users[self.m_data[row].item_author])
            elif col == self.ColumnApprover:
                if self.m_data[row].item_approver == 0:
                    if not self.m_data[row].item_active:
                        return QVariant("Отклонено")
                    elif self.m_data[row].item_active:
                        return QVariant("На рассмотрении")
                return QVariant(self.m_users[self.m_data[row].item_approver])
                # return self.m_users[self.m_data[row].item_approver]
            elif col == self.ColumnActive:
                if self.m_data[row].item_active:
                    return QVariant("Да")
                else:
                    return QVariant("Нет")
        elif role == Qt.BackgroundRole:
            if col == self.ColumnApprover:
                if self.m_data[row].item_approver == 0:
                    if not self.m_data[row].item_active:
                        return QVariant(QBrush(QColor(typedefs.ColorRejected)))
                    elif self.m_data[row].item_active:
                        return QVariant(QBrush(QColor(typedefs.ColorPending)))
                return QVariant(QBrush(QColor(typedefs.ColorApproved)))
        elif role == typedefs.RoleNodeId:
            return QVariant(self.m_data[row].item_id)

        return QVariant()
