import typedefs
import suggestionitem
from copy import copy
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QDate
from PyQt5.QtGui import QBrush, QColor


class SuggestionModel(QAbstractTableModel):
    ColumnId = 0
    ColumnDate = ColumnId + 1
    ColumnText = ColumnDate + 1
    ColumnAuthor = ColumnText + 1
    ColumnStatus = ColumnAuthor + 1
    ColumnActive = ColumnStatus + 1
    ColumnCount = ColumnActive + 1

    _headers = ["Номер", "Дата", "Текст", "Автор", "Статус", "Активно"]

    def __init__(self, parent=None, dbmanager=None):
        super(SuggestionModel, self).__init__(parent)
        self._dbman = dbmanager
        self._data = []
        self._users = {}
        self._has_dirty_data = False

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self._data))
        self._data.clear()
        self.endRemoveRows()

    def initModel(self):
        print("init suggestion model")
        self._users = self._dbman.getUserDict()

        tmplst = self._dbman.getSuggestionList()
        self.beginInsertRows(QModelIndex(), 0, len(tmplst)-1)
        self._data = tmplst
        self.endInsertRows()

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self._headers):
            return QVariant(self._headers[section])
        return QVariant()

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.isValid():
            return 0
        return len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        return self.ColumnCount

    def parent(self):
        return QModelIndex()

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()

        col = index.column()
        row = index.row()

        # print(self._data[row])
        # return

        if role == Qt.DisplayRole:
            if col == self.ColumnId:
                return QVariant(self._data[row].item_id)
            elif col == self.ColumnDate:
                return QVariant(self._data[row].item_date.toString("dd.MM.yyyy"))
            elif col == self.ColumnText:
                return QVariant(self._data[row].item_text)
            elif col == self.ColumnAuthor:
                return QVariant(self._users[self._data[row].item_author])
            elif col == self.ColumnStatus:
                if self._data[row].item_status == typedefs.StatusPending:
                    return QVariant("На рассмотрении")
                elif self._data[row].item_status == typedefs.StatusApproved:
                    assert (self._data[row].item_approver > 0), "No approver specified for an approved suggestion."
                    return QVariant("Одобрено: " + self._users[self._data[row].item_approver])
                elif self._data[row].item_status == typedefs.StatusRejected:
                    assert (self._data[row].item_approver > 0), "No approver specified for a rejected suggestion."
                    return QVariant("Отклонено: " + self._users[self._data[row].item_approver])
                else:
                    raise ValueError("Wrong suggestion status:", self._data[row].item_status)
            elif col == self.ColumnActive:
                if self._data[row].item_is_active == 1:
                    return QVariant("Да")
                elif self._data[row].item_is_active == 2:
                    return QVariant("Нет")
                else:
                    return QVariant("INVALID ACTIVITY STATE")
        elif role == Qt.EditRole:
            if col == self.ColumnId:
                return QVariant(self._data[row].item_id)
            elif col == self.ColumnDate:
                return QVariant(self._data[row].item_date)
            elif col == self.ColumnText:
                return QVariant(self._data[row].item_text)
            elif col == self.ColumnAuthor:
                return QVariant(self._users[self._data[row].item_author])
            elif col == self.ColumnStatus:
                if self._data[row].item_status == typedefs.StatusPending:
                    return QVariant("На рассмотрении")
                elif self._data[row].item_status == typedefs.StatusApproved:
                    assert (self._data[row].item_approver > 0), "No approver specified for an approved suggestion."
                    return QVariant("Одобрено: " + self._users[self._data[row].item_approver])
                elif self._data[row].item_status == typedefs.StatusRejected:
                    assert (self._data[row].item_approver > 0), "No approver specified for a rejected suggestion."
                    return QVariant("Отклонено: " + self._users[self._data[row].item_approver])
                else:
                    raise ValueError("Wrong suggestion status:", self._data[row].item_status)
            elif col == self.ColumnActive:
                if self._data[row].item_is_active == 1:
                    return True
                elif self._data[row].item_is_active == 2:
                    return False

        elif role == Qt.BackgroundRole:
            if col == self.ColumnStatus:
                if self._data[row].item_status == typedefs.StatusPending:
                    return QVariant(QBrush(QColor(typedefs.ColorPending)))
                elif self._data[row].item_status == typedefs.StatusApproved:
                    return QVariant(QBrush(QColor(typedefs.ColorApproved)))
                elif self._data[row].item_status == typedefs.StatusRejected:
                    return QVariant(QBrush(QColor(typedefs.ColorRejected)))
                else:
                    raise ValueError("Wrong suggestion status:", self._data[row].item_status)
            else:
                if self._data[row].item_is_dirty:
                    return QVariant(QBrush(QColor(typedefs.ColorDirty)))
        elif role == typedefs.RoleNodeId:
            return QVariant(self._data[row].item_id)
        elif role == typedefs.RoleStatus:
            return QVariant(self._data[row].item_status)
        elif role == typedefs.RoleAuthor:
            return QVariant(self._data[row].item_author)
        elif role == typedefs.RoleActive:
            return QVariant(self._data[row].item_is_active)
        return QVariant()

    def setData(self, index, data, role=None):
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == self.ColumnText:
                self._data[row].item_text = data
                self._data[row].item_is_dirty = True
                self.has_dirty_data = True
                return True
            if col == self.ColumnActive:
                if data:
                    self._data[row].item_is_active = 1
                else:
                    self._data[row].item_is_active = 2
                self._data[row].item_is_dirty = True
                self.has_dirty_data = True
                return True
        return False

    def addSuggestionRecord(self, user):
        # TODO refactor hardcoded constants
        tmpitem = suggestionitem.SuggestionItem(id_=0
                                                , date=QDate.currentDate()
                                                , text=""
                                                , author=user
                                                , approver=0
                                                , is_active=1
                                                , status=typedefs.StatusPending
                                                , is_dirty=True)

        self.beginInsertRows(QModelIndex(), 0, 0)
        self._data.insert(0, tmpitem)
        self.endInsertRows()
        self.has_dirty_data = True
        return self.index(0, 0, QModelIndex())

    def insertSuggestionRecord(self, record):
        record.item_id = self._dbman.insertRec(record)
        record.item_is_dirty = False

    def updateSuggestionRecord(self, record):
        self._dbman.updateRec(record)
        record.item_is_dirty = False

    def deleteSuggestionRecord(self, record):
        self._dbman.deleteRec(record)

    def deleteSuggestionRecordAtIndex(self, index):
        row = index.row()
        self.deleteSuggestionRecord(self._data[row])
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._data[row]
        self.endRemoveRows()

    def saveDirtyData(self):
        for rec in self._data:
            if rec.item_is_dirty:
                if rec.item_id > 0:
                    self.updateSuggestionRecord(rec)
                elif rec.item_id == 0:
                    newid = self.insertSuggestionRecord(rec)
                else:
                    raise ValueError("Wrong record id:", rec.item_id)

        self.has_dirty_data = False

    def approveSuggestion(self, index, user):
        # TODO use functors
        row = index.row()
        # TODO modify record in a separate method
        self._data[row].item_status = typedefs.StatusApproved
        self._data[row].item_approver = user
        self._data[row].item_is_active = 1
        self._data[row].item_is_dirty = True
        self.has_dirty_data = True

    def rejectSuggestion(self, index, user):
        # TODO use functors
        row = index.row()
        # TODO modify record in a separate method
        self._data[row].item_status = typedefs.StatusRejected
        self._data[row].item_approver = user
        self._data[row].item_is_active = 2
        self._data[row].item_is_dirty = True
        self.has_dirty_data = True

    def submit(self):
        # print("model submit call")
        return True

    @property
    def has_dirty_data(self):
        return self._has_dirty_data

    @has_dirty_data.setter
    def has_dirty_data(self, has):
        if type(has) == bool:
            self._has_dirty_data = has
        else:
            raise TypeError("Wrong property type. Need bool, got", type(has))

