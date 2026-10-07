from dotenv import load_dotenv
import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage, firestore_async
from pprint import pp
import pytz
from cal_links import get_calendar_links

def initialize_firebase_service_account() -> firestore.client:

    key_dict = json.loads(os.environ.get("FB_DICT"))

    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.environ.get("FB_STORAGE_BUCKET")
    })

    db = firestore.client(database_id="default")

    return db

async def create_event_in_firestore(db):

    tz = pytz.timezone('America/New_York')

    event_data = {
        "event_code": "2026102200",
        "title": "Asheville For All - October Meetup",
        "start": datetime.fromisoformat("2026-10-22T18:00:00").astimezone(tz),
        "end": datetime.fromisoformat("2026-10-22T20:00:00").astimezone(tz),
        "location": "Hi-Wire Brewing - River Arts District, 284 Lyman St., Asheville NC 28801"
    }

    await db.collection("events").document(event_data["event_code"]).set(event_data)

async def read_event_from_firestore(db, event_code):

    event_ref = db.collection("events").document(event_code)
    event_doc = await event_ref.get()
    if event_doc.exists:
        pp(event_doc.to_dict())
    else:
        return None

async def read_RSVPs_from_event(db, event_code, csvStyle=False) -> str:

    from google.cloud.firestore_v1.base_query import FieldFilter

    query = db.collection_group("rsvps").where(filter=FieldFilter("eventcode", "==", event_code))

    docs = query.stream()

    rsvp_list = []
    email_list = []

    async for d in docs:

        if d.reference.parent.parent.id not in email_list:

            s = d.reference.parent.parent.id
            email_list.append(s)

            rsvp = {"email": s}

            person_ref = d.reference.parent.parent
            doc = await person_ref.get()
            if doc.exists:

                rsvp["firstname"] = doc.to_dict().get("firstname", "")
                rsvp["lastname"] = doc.to_dict().get("lastname", "")

            rsvp_list.append(rsvp)

    if csvStyle:
        csv = "email, firstname, lastname\n"
        for line in rsvp_list:
            csv += line["email"] + "," + line["firstname"] + "," + line["lastname"] + "\n"

        print(csv)
        return csv

    print(json.dumps(rsvp_list))
    return json.dumps(rsvp_list)

def write_ics_to_file(event_code, ics_text:str) -> str:

    bucket = storage.bucket()
    blob = bucket.blob(f'ics/{event_code}/calendar.ics')
    blob.upload_from_string(ics_text)
    blob.make_public()
    return blob.public_url

def get_public_url_for_existing_ics_file(event_code) -> str:

    bucket = storage.bucket()
    blob = bucket.blob(f'ics/{event_code}/invite.ics')
    ## blob.make_public() <-- should be public by default because of the function above.
    return blob.public_url

async def generate_and_store_ics(db, eventcode) -> str:

    event_doc = await db.collection("events").document(eventcode).get()

    event_info = event_doc.to_dict()

    cal_links = get_calendar_links({
        "title": event_info.get("title"),
        "start_time": event_info.get("start"),
        "end_time": event_info.get("end"),
        "location": event_info.get("location"),
        "timezone": "America/New_York"    
    })

    ics_text = cal_links.get("ics")
    return write_ics_to_file(eventcode, ics_text)

if __name__ == "__main__":

    load_dotenv()

    db = initialize_firebase_service_account()

    read_RSVPs_from_event(db, "2026102200", csvStyle=True)