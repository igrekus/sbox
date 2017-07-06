import typedefs
import re
from PyQt5.QtCore import QSortFilterProxyModel, Qt



class SuggestionSearchProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(SuggestionSearchProxyModel, self).__init__(parent)

        self.filterAuthor = 0
        self.filterActive = 0
        self.filterStatus = 0
        self._filterString = ""
        self._filterRegex = re.compile(self._filterString, flags=re.IGNORECASE)

    @property
    def filterString(self):
        return self._filterString

    @filterString.setter
    def filterString(self, string):
        if type(string) == str:
            self._filterString = string
            self._filterRegex = re.compile(string, flags=re.IGNORECASE)
        else:
            raise TypeError("Filter must be a str.")

    def filterAcceptsRow(self, source_row, source_parent_index):
        source_index = self.sourceModel().index(source_row, self.filterKeyColumn(), source_parent_index)
        if source_index.isValid():
            author = self.sourceModel().index(source_row, 0, source_parent_index).data(typedefs.RoleAuthor)
            active = self.sourceModel().index(source_row, 0, source_parent_index).data(typedefs.RoleActive)
            status = self.sourceModel().index(source_row, 0, source_parent_index).data(typedefs.RoleStatus)

            if self.filterAuthor == 0 or self.filterAuthor == author:
                if self.filterActive == 0 or self.filterActive == active:
                    if self.filterStatus == 0 or self.filterStatus == status:
                        for i in range(self.sourceModel().columnCount()):
                            if self._filterRegex.findall(str(self.sourceModel().index(source_row, i, source_parent_index).data(Qt.DisplayRole))):
                                return True

        return False
