from datetime import datetime

import pytz

class Person:

    firstname: str
    lastname: str
    created: datetime
    email: str
    zip: str

    def __init__(self, firstname, lastname, created, email, zip):

        self.firstname = firstname
        self.lastname = lastname
        self.created = created
        self.email = email
        self.zip = zip

    def generate_id(self):

        return self.email

    def to_dict(self):

        return {"firstname": self.firstname, "lastname":self.lastname, "created": self.created, "email": self.email, "zip": self.zip}

    @staticmethod
    def from_dict(data):

        tz = pytz.timezone('America/New_York')
        
        return Person(data.get("firstname", ""), data.get("lastname", ""), data.get("created", datetime.now().astimezone(tz)), data["email"], data["zip"])