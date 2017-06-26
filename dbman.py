import codecs
from suggestionitem import SuggestionItem
from PyQt5.QtCore import Qt, QObject
from PyQt5 import QtSql


class DbManager(QObject):
    def __init__(self, parent=None):
        super(DbManager, self).__init__(parent)
        # self.setAttribute(Qt.WA_DeleteOnClose)

    def connectToDatabase(self):
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL")

        db.setHostName("localhost")
        db.setPort(3306)
        db.setUserName("root")
        db.setPassword("")
        db.setDatabaseName("sbox")

        if not db.open():
            print("db not open")
            return False

        return True

    def execSimpleQuery(self, str):
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        # query = QtSql.QSqlQuery()
        query.exec(str)
        print(query.lastQuery(), "rows:", query.numRowsAffected())
        print(query.lastError().text())
        return query

    def getSuggestionList(self):
        query = self.execSimpleQuery("SELECT * FROM sug WHERE sug_id <> 0")
        tmplist = list()
        while query.next():
            tmplist.append(SuggestionItem.fromSqlRecord(query.record()))
        return tmplist

    def getUserDict(self):
        # query = self.execSimpleQuery("SELECT user_id, CONVERT(user_name USING utf8) FROM user WHERE user_id <> 0")
        query = self.execSimpleQuery("SELECT user_id, user_name FROM user WHERE user_id <> 0")
        tmpdict = dict()
        while query.next():
            tmpdict[query.value(0)] = codecs.decode(query.value(1).encode("cp1251"))
        return tmpdict

