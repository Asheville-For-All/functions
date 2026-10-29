from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, storage, firestore
from pprint import pp
import pytz
from cal_links import get_calendar_links
from models.event import Event
from models.rsvp import Rsvp
import emailer
import time

##TODO : determine if this is running on google firebase or not. Update secrets / evironment vars as needed.

def initialize_firebase_service_account() -> firestore.client:

    key_dict = json.loads(os.environ.get("FB_DICT"))

    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.environ.get("FB_STORAGE_BUCKET")
    })

    db = firestore.client(database_id="default")

    return db

def send_reminders_for_upcoming_events(db):

    from google.cloud.firestore_v1.base_query import FieldFilter

    in_one_day = datetime.now(pytz.UTC) + timedelta(days=1)
    in_four_days = datetime.now(pytz.UTC) + timedelta(days=4)

    query = db.collection("events").where(filter=FieldFilter("start", ">", in_one_day)).where(filter=FieldFilter("start", "<", in_four_days))

    docs = query.stream()

    for d in docs:

        eventcode = d.id

        event = Event.from_dict(d.to_dict())

        emailedlist = d.to_dict().get("emailedlist", [])

        query = db.collection_group("rsvps").where(filter=FieldFilter("eventcode", "==", eventcode))

        rsvps = query.stream()

        email_list = []
        too_soon = []

        for r in rsvps:

            rsvp = Rsvp.from_dict(r.to_dict())

            if rsvp.created > (datetime.now(pytz.UTC) - timedelta(days=2)):

                too_soon.append(rsvp.to_dict()["email"])

            else:

                email_list.append(r.to_dict()["email"])

        for e in email_list:

            if e not in emailedlist and e not in too_soon:

                #TODO need to get secrets and/or env secrets? here to send email

                emailer.send_event_reminder_email(TODO) #TODO determine secrets/etc depending on what environemnt this will run in

                emailedlist.append(e)

                time.sleep(0.1)

        event.emailedlist = emailedlist
        db.collection("events").document(eventcode).update({"emailedlist": emailedlist})

if __name__ == "__main__":

    load_dotenv()

    ...