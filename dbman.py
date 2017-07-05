import codecs
from suggestionitem import SuggestionItem
from PyQt5.QtCore import Qt, QObject
from PyQt5 import QtSql

# TODO db error handling
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
        db.setDatabaseName("sb")

        # db.setHostName("10.10.15.9")
        # db.setPort(3306)
        # db.setUserName("root")
        # db.setPassword("123456")
        # db.setDatabaseName("sbox")

        if not db.open():
            print("db not open")
            return False, db.lastError().text()

        return True, "ok"

    def execSimpleQuery(self, str):
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        # query = QtSql.QSqlQuery()
        query.exec(str)
        print(query.lastQuery(), "rows:", query.numRowsAffected())
        print(query.lastError().text())
        return query

    def checkLogin(self, uid, passw):
        """        
        Checks user against the database
        :param uid: int - user id
        :param passw: str - user password
        :return: tuple(bool, int) - check result, user level
        """

        # TODO hash passwords
        # query = self.execSimpleQuery("SELECT * FROM `user` WHERE user_id = "
        #                              + str(uid) + " AND user_pass = '"
        #                              + str(passw) + "'")
        query = self.execSimpleQuery("CALL checkUser("
                                     + str(uid) + ", '"
                                     + str(passw) + "')")
        query.next()
        return bool(query.numRowsAffected()), query.value(0)

    def getSuggestionList(self):
        query = self.execSimpleQuery("CALL getSuggestionsAll();")
        tmplist = list()
        while query.next():
            tmplist.append(SuggestionItem.fromSqlRecord(query.record()))
        return tmplist

    def getUserDict(self):
        query = self.execSimpleQuery("CALL getUsersAll();")
        tmpdict = dict()
        while query.next():
            print(query.value(1))
            print(query.value(1).encode("utf-8"))
            print(codecs.decode(query.value(1).encode("utf-8").replace("\x98", "\xc8"), encoding="cp1251"))
            tmpdict[query.value(0)] = codecs.decode(query.value(1).encode("cp1251"), encoding="utf-8")
        return tmpdict

    def insertRec(self, record):
        # TODO make encoder helper functions
        query = self.execSimpleQuery("CALL insertSuggestion('" +
                                     codecs.decode(record.item_text.encode("utf-8"), encoding="cp1251") + "', " +
                                     str(record.item_author) + ", " +
                                     str(record.item_approver) + ", " +
                                     str(record.item_is_active) + ", " +
                                     str(record.item_status) + ")")
        query.next()
        return query.value(0)

    def updateRec(self, record):
        # TODO make encoder helper functions
        query = self.execSimpleQuery("CALL updateSuggestion(" +
                                     str(record.item_id) + ", '" +
                                     codecs.decode(record.item_text.encode("utf-8"), encoding="cp1251") + "', " +
                                     str(record.item_approver) + ", " +
                                     str(record.item_is_active) + ", " +
                                     str(record.item_status) + ")")
        return query.isValid()  # TODO error handling

    def deleteRec(self, record):
        # TODO change deletion to bool marking
        if record.item_id == 0:
            raise ValueError("Wrong record id to delete:", record.item_id)

        query = self.execSimpleQuery("CALL deleteSuggestion(" + str(record.item_id) + ")")
        return True
