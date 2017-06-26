import codecs


class SuggestionItem:
    def __init__(self, id_=0, text="", author=0, approver=0, active=False):
        self.item_id = id_
        self.item_text = text
        self.item_author = author
        self.item_approver = approver
        self.item_active = active

    def __str__(self):
        return "SugItem(" + "id:" + str(self.item_id) + " "\
                          + "txt:" + self.item_text + " "\
                          + "auth:" + str(self.item_author) + " "\
                          + "app:" + str(self.item_approver) + " "\
                          + "act:" + str(self.item_active) + ")"

    @classmethod
    def fromSqlRecord(cls, record):
        if not record:
            raise ValueError("Wrong SQL record.")

        return cls(id_=record.value(0)
                   , text=codecs.decode(record.value(1).encode("cp1251"))
                   , author=record.value(2)
                   , approver=record.value(3)
                   , active=bool(record.value(4)))
