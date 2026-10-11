from datetime import datetime

import pytz

class Person:

    firstname: str
    lastname: str
    created: datetime
    email: str
    zip: str
    last_event_trigger: str ## rsvp | subscribe

    def __init__(self, firstname, lastname, created, email, zip, last_event_trigger):

        self.firstname = firstname
        self.lastname = lastname
        self.created = created
        self.email = email
        self.zip = zip
        self.last_event_trigger = last_event_trigger

    def generate_id(self):

        return self.email

    def to_dict(self):

        return {"firstname": self.firstname, "lastname":self.lastname, "created": self.created, "email": self.email, "zip": self.zip, "last_event_trigger": self.last_event_trigger}

    @staticmethod
    def from_dict(data):

        tz = pytz.timezone('America/New_York')
        
        return Person(data.get("firstname", ""), data.get("lastname", ""), data.get("created", datetime.now().astimezone(tz)), data["email"], data["zip"], data.get("last_event_trigger", ""))