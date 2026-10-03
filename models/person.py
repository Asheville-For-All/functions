from datetime import datetime

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
        return Person(data.firstname, data.lastname, data.created, data.email, data.zip)