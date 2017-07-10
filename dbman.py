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

        try:
            f = open("settings.ini")
        except IOError:
            return False, str("Settings.ini not found.")

        lines = f.readlines()
        f.close()

        settings = dict()
        for s in lines:
            # print(s)
            if s.strip() and s[0] != "#":
                sett = s.strip().split("=")
                settings[sett[0]] = sett[1]
            else:
                continue

        db.setHostName(settings["host"])
        db.setPort(int(settings["port"]))
        db.setUserName(settings["username"])
        db.setPassword(settings["password"])
        db.setDatabaseName(settings["database"])

        # db.setConnectOptions("charset=utf8")

        if not db.open():
            print("db not open")
            return False, db.lastError().text()

        # print(db.connectOptions())

        return True, "ok"

    def execSimpleQuery(self, string):
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        # query = QtSql.QSqlQuery()
        query.exec(string)
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
            # cp1251 = "Р°Р±РІРіРґРµС‘Р¶Р·РёР№РєР»РјРЅРѕРїСЂСЃС‚СѓС„С…СЃС‡С€С‰СЊС‹СЉСЌСЋСЏ"
            # print(cp1251)
            # cp1251bytes = cp1251.encode("cp1251")
            # print(cp1251bytes)
            # utf8 = cp1251bytes.decode(encoding="utf-8")
            # print(utf8)
            #
            # # Р
            # # РЄ
            # cp1251 = "РђР‘Р’Р“Р”Р•РЃР–Р—РР™РљР›РњРќРћРџР РЎРўРЈР¤РҐР¦Р§РЁР©РЄР«Р¬Р­Р®РЇ"
            # print(cp1251)
            # cp1251bytes = cp1251.replace("Р", "РЄ").encode("cp1251")
            # print(cp1251bytes)
            # utf8 = cp1251bytes.decode(encoding="utf-8")
            # print(utf8)

            # raise ValueError("break")
            # print("-------------")
            # print(query.value(1))
            # print(query.value(1).encode("cp1251"))
            # print(codecs.decode(query.value(1).replace("Р", "РЄ").encode("cp1251"), encoding="utf-8").replace("Ъ", "И"))
            tmpdict[query.value(0)] = codecs.decode(query.value(1).replace("Р", "РЄ").encode("cp1251"),
                                                    encoding="utf-8").replace("Ъ", "И")
        return tmpdict

    def insertRec(self, record):
        # TODO make encoder helper functions
        query = self.execSimpleQuery("CALL insertSuggestion('" +
                                     codecs.decode(record.item_text.replace("И", "Ъ").encode("utf-8"),
                                                   encoding="cp1251").replace("РЄ", "Р") + "', " +
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
                                     codecs.decode(record.item_text.replace("И", "Ъ").encode("utf-8"),
                                                   encoding="cp1251").replace("РЄ", "Р") + "', " +
                                     # codecs.decode(record.item_text.encode("utf-8"), encoding="cp1251") + "', " +
                                     str(record.item_approver) + ", " +
                                     str(record.item_is_active) + ", " +
                                     str(record.item_status) + ")")
        return query.isValid()  # TODO error handling

    def deleteRec(self, record):
        # TODO change deletion to bool marking
        if record.item_id == 0:
            return
            # raise ValueError("Wrong record id to delete:", record.item_id)

        query = self.execSimpleQuery("CALL deleteSuggestion(" + str(record.item_id) + ")")
        return True
