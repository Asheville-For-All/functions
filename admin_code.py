from dotenv import load_dotenv
import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from pprint import pp
import pytz

def initialize_firebase_service_account() -> firestore.client:

    key_dict = json.loads(os.environ.get("FB_DICT"))

    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

    db = firestore.client(database_id="default")

    return db

def create_event_in_firestore(db):

    tz = pytz.timezone('America/New_York')

    event_data = {
        "event_code": "2026102200",
        "title": "Asheville For All - October Meetup",
        "start": datetime.fromisoformat("2026-10-22T18:00:00").astimezone(tz),
        "end": datetime.fromisoformat("2026-10-22T20:00:00").astimezone(tz),
        "location": "Hi-Wire Brewing - River Arts District, 284 Lyman St., Asheville NC 28801"
    }

    db.collection("events").document(event_data["event_code"]).set(event_data)

def read_event_from_firestore(db, event_code):

    event_ref = db.collection("events").document(event_code)
    event_doc = event_ref.get()
    if event_doc.exists:
        pp(event_doc.to_dict())
    else:
        return None

def read_RSVPs_from_event(db, event_code) -> list:

    from google.cloud.firestore_v1.base_query import FieldFilter

    query = db.collection_group("rsvps").where(filter=FieldFilter("eventcode", "==", event_code))

    docs = query.stream()

    rsvp_list = []
    email_list = []

    for d in docs:

        if d.reference.parent.parent.id not in email_list:

            s = d.reference.parent.parent.id
            email_list.append(s)

            person_ref = d.reference.parent.parent
            doc = person_ref.get()
            if doc.exists:
                s += ", " + doc.to_dict().get("firstname", "")
                s += ", " + doc.to_dict().get("lastname", "")

            rsvp_list.append(s)

    pp(rsvp_list)
    
    return rsvp_list

if __name__ == "__main__":

    load_dotenv()

    db = initialize_firebase_service_account()

    read_RSVPs_from_event(db, "2026102200")
    