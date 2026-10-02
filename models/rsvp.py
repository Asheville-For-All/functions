from datetime import datetime

class Rsvp:

    eventcode: str
    created: datetime

    def __init__(self, created, eventcode):

        self.eventcode = eventcode
        self.created = created

    def generate_id(self):

        return self.eventcode + "_" + self.created.isoformat()

    def to_dict(self):

        return {"eventcode": self.eventcode, "created":self.created}

    @staticmethod
    def from_dict(data):

        return Rsvp(data.created, data.eventcode)