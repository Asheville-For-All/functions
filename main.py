from firebase_functions import https_fn, options
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app, firestore
from firebase_functions import logger
from firebase_functions.params import SecretParam

from firebase_functions.firestore_fn import (
  on_document_created,
  Event,
  DocumentSnapshot
)

from datetime import datetime
import os
import re
import dateutil
import pytz

from emailer import send_email
from cal_links import get_calendar_links

from models.person import Person
from models.rsvp import Rsvp

set_global_options(max_instances=10)

initialize_app()

EMAIL_USER = SecretParam("EMAIL_ACCT_USER")
EMAIL_PW = SecretParam("EMAIL_ACCT_PW")
EMAIL_SENDER = SecretParam("EMAIL_SENDER")
EMAIL_SMTP = SecretParam("EMAIL_SMTP")

@https_fn.on_request(cors=options.CorsOptions(
    cors_origins=["http://localhost:5500", r"https://.*\.web\.app", r"https://.*\.firebaseapp\.com", r"ashevilleforall"],
    cors_methods=["get", "post"],
))
def rsvpv2(req: https_fn.Request) -> https_fn.Response:

    if "email" not in req.form or "eventcode" not in req.form or "zip" not in req.form:
        return https_fn.Response("Missing required fields.", status=400)

    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, req.form.get("email")) == False:
        return https_fn.Response("Invalid email address.", status=400)

    try:

        now = datetime.now().astimezone(dateutil.tz.gettz(os.environ.get("America/New_York")))
        
        p = Person(req.form.get("firstname", ""), req.form.get("lastname", ""), now, req.form.get("email"), req.form.get("zip"))
        r = Rsvp(now, req.form.get("eventcode"))

        db = firestore.client(database_id="default")

        mergearray = ["zip"]
        if req.form.get("firstname", "") != "":
            mergearray.append("firstname")
        if req.form.get("lastname", "") != "":
            mergearray.append("lastname")

        db.collection("people").document(p.generate_id()).set(p.to_dict(), merge=mergearray)
        db.collection("people").document(p.generate_id()).collection("rsvps").document(r.generate_id()).set(r.to_dict())

    except Exception as e:
        return https_fn.Response(f"An error occurred: {str(e)}", status=500)

    return https_fn.Response("RSVP successfully recorded.", status=200)

# Triggered when a new document is created in the "rsvps" subcollection
@on_document_created(document="people/{personId}/rsvps/{rsvpId}", database="default", secrets=[EMAIL_USER, EMAIL_PW, EMAIL_SENDER, EMAIL_SMTP])
def handle_new_rsvp(event: Event[DocumentSnapshot]) -> None:
    # 1. Retrieve the parent document ID (personId) from event.params
    parent_id = event.params["personId"]
    
    # 2. Retrieve the newly created RSVP document ID
    rsvp_id = event.params["rsvpId"]
    
    # 3. Retrieve the actual document data
    event_code = event.data.to_dict().get("eventcode") if event.data else None

    ##TODO send email to person_id. Get the event info from firebase using the eventcode.

    content = "<p>Thank for your RSVP! We look forward to seeing you.</p><p>Here is the event information:</p>"

    db = firestore.client(database_id="default")

    event_doc = db.collection("events").document(event_code).get()
    if event_doc.exists == False:
        return https_fn.Response("Event not found.", status=404)

    event_info = event_doc.to_dict()

    tz = pytz.timezone('America/New_York')

    adjusted_start = event_info.get("start").astimezone(tz)
    adjusted_end = event_info.get("end").astimezone(tz)

    content += f"<p><em>{event_info.get("title")}<br/>{event_info.get("location")}<br/>{adjusted_start.strftime("%a, %b %-d, %Y")}<br/>{adjusted_start.strftime("%I:%M %p")}-{adjusted_end.strftime("%I:%M %p")}</em></p>"

    cal_links = get_calendar_links({
        "title": event_info.get("title"),
        "start_time": event_info.get("start"),
        "end_time": event_info.get("end"),
        "location": event_info.get("location"),
        "timezone": "America/New_York"    
    })

    content += "<h2>Add to Calendar:</h2><p>"

    for key, val in cal_links.items():
        if key != "ics" and key != "apple":
            content += f"<span style='background-color:gray;color:white;border-radius:4px;padding:4px;'><a href='{val}' style='color:white;'>{key.upper()}</a></span> "

    content += "</p>"

    user = EMAIL_USER.value
    email_pw = EMAIL_PW.value
    email_sender = EMAIL_SENDER.value
    email_smtp = EMAIL_SMTP.value

    send_email(user, email_pw, email_sender, parent_id, "Thank you for your RSVP", content, email_smtp)