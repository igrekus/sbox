import codecs
import datetime
from PyQt5.QtCore import Qt


class SuggestionItem:
    def __init__(self, id_=0, date=None, text="", author=0, approver=0, active=False):
        self.item_id = id_
        self.item_date = date
        self.item_text = text
        self.item_author = author
        self.item_approver = approver
        self.item_active = active

    def __str__(self):
        return "SugItem(" + "id:" + str(self.item_id) + " "\
                          + "date:" + str(self.item_date) + " "\
                          + "txt:" + self.item_text + " "\
                          + "auth:" + str(self.item_author) + " "\
                          + "app:" + str(self.item_approver) + " "\
                          + "act:" + str(self.item_active) + ")"

    @classmethod
    def fromSqlRecord(cls, record):
        if not record:
            raise ValueError("Wrong SQL record.")
        return cls(id_=record.value(0)
                   , date=record.value(1)
                   , text=codecs.decode(record.value(2).encode("cp1251"))
                   , author=record.value(3)
                   , approver=record.value(4)
                   , active=bool(record.value(5)))
