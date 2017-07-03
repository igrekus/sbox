import typedefs
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant


class MapModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(MapModel, self).__init__(parent)
        self.mapData = dict()
        self.strList = list()

    def initModel(self, data: dict):
        count = len(data.values()) - 1
        if count < 0:
            count = 0
        self.beginInsertRows(QModelIndex(), 0, count)
        self.mapData = data
        self.strList = list(self.mapData.values())
        self.strList.sort()
        self.mapData[0] = "Все"
        self.strList.insert(0, "Все")
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.mapData) - 1)
        self.mapData.clear()
        self.strList.clear()
        self.endRemoveRows()

    def isEmpty(self):
        return not bool(self.strList)

    def headerData(self, section, orientation, role=None):
        headers = ["Имя"]
        if orientation == Qt.Horizontal and section < len(headers):
            return QVariant(headers[section])

        return QVariant()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.strList)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant

        row = index.row()
        if role == Qt.DisplayRole:
            return self.strList[row]
        elif role == typedefs.RoleNodeId:
            return self.getId(self, self.strList[row])

    def getId(self, search_str=""):
        for i, string in self.mapData.items():
            if string == search_str:
                return i

#     void
#     MapModel::addItem(const
#     qint32
#     id, const
#     QString & str)
#     {
#     auto
#     rowIter = std::find_if(m_strList.begin(), m_strList.end(), [ & str](const
#     QString & it){
#     return it > str;
#     });
#     qint32
#     row = std::distance(m_strList.begin(), rowIter);
#     m_mapData.id.insert(id, str);
#     m_mapData.di.insert(str, id);
#
#     beginInsertRows(QModelIndex(), row, row);
#     m_strList.insert(row, str);
#     endInsertRows();
#     }
#
#     void
#     MapModel::addItemAtPosition(const
#     qint32
#     pos, const
#     qint32
#     id, const
#     QString & str)
#     {
#         beginInsertRows(QModelIndex(), pos, pos);
#     m_strList.insert(pos, str);
#     m_mapData.id.insert(id, str);
#     m_mapData.di.insert(str, id);
#     endInsertRows();
#     }
#
#     void
#     MapModel::editItem(const
#     qint32
#     id, const
#     QString & name)
#     {
#         qint32
#     row = m_strList.indexOf(m_mapData.id.value(id));
#
#     m_mapData.di.remove(m_mapData.id.value(id));
#     m_mapData.id.replace(id, name);
#     m_mapData.di.insert(name, id);
#
#     m_strList.replace(row, name);
#     dataChanged(index(row, 0, QModelIndex()), index(row, 0, QModelIndex()));
#     }
#
#     void
#     MapModel::removeItem(const
#     qint32
#     id)
#     {
#         qint32
#     row = m_strList.indexOf(m_mapData.id.value(id));
#
#     m_mapData.di.remove(m_mapData.id.value(id));
#     m_mapData.id.remove(id);
#
#     beginRemoveRows(QModelIndex(), row, row);
#     m_strList.removeAt(row);
#     endRemoveRows();
#     }
#
#     QString
#     MapModel::getData(const
#     qint32
#     id)
#     {
#     return m_mapData.id.value(id);
#
# }
