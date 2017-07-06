import codecs
import typedefs


class SuggestionItem:
    # TODO make properties
    # TODO change to a property sets item_is_dirty = True
    def __init__(self, id_=None, date=None, text="", author=0, approver=0, is_active=1,
                 status=typedefs.StatusPending, is_dirty=False):
        self.item_id = id_
        self.item_date = date
        self.item_text = text
        self.item_author = author
        self.item_approver = approver
        self.item_is_active = is_active
        self.item_status = status
        self.item_is_dirty = is_dirty

    def __str__(self):
        return "SugItem(" + "id:" + str(self.item_id) + " " \
               + "date:" + str(self.item_date) + " " \
               + "txt:" + self.item_text + " " \
               + "auth:" + str(self.item_author) + " " \
               + "apvr:" + str(self.item_approver) + " " \
               + "act:" + str(self.item_is_active) + " " \
               + "status:" + str(self.item_status) + " "\
               + "dirty:" + str(self.item_is_dirty) + ")"

    @classmethod
    def fromSqlRecord(cls, record):
        if not record:
            raise ValueError("Wrong SQL record.")
        return cls(id_=record.value(0)
                   , date=record.value(1)
                   , text=codecs.decode(record.value(2).replace("Р", "РЄ").encode("cp1251")).replace("Ъ", "И")
                   , author=record.value(3)
                   , approver=record.value(4)
                   , is_active=record.value(5)
                   , status=record.value(6)
                   , is_dirty=False)
