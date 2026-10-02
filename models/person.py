from datetime import datetime

class Person:

    firstname: str
    lastname: str
    created: datetime
    email: str

    def __init__(self, firstname, lastname, created, email):

        self.firstname = firstname
        self.lastname = lastname
        self.created = created
        self.email = email

    def generate_id(self):

        return self.email

    def to_dict(self):

        return {"firstname": self.firstname, "lastname":self.lastname, "created": self.created, "email": self.email}

    @staticmethod
    def from_dict(data):
        return Person(data.firstname, data.lastname, data.created, data.email)