## TODO write code for any admin tasks taht won't go through the deployment process

from dotenv import load_dotenv
import os
import json
from datetime import datetime, date, time
import dateutil
from dateutil.relativedelta import relativedelta
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

if __name__ == "__main__":

    load_dotenv()

    db = initialize_firebase_service_account()

    ##create_event_in_firestore(db)
    read_event_from_firestore(db, "2026102200")
    