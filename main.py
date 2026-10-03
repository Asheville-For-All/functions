from firebase_functions import https_fn, options
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app, firestore
from firebase_functions import logger

from firebase_functions.firestore_fn import (
  on_document_created,
  on_document_deleted,
  on_document_updated,
  on_document_written,
  Event,
  Change,
  DocumentSnapshot,
)

from datetime import datetime
import os
import re

import dateutil

from models.person import Person
from models.rsvp import Rsvp

set_global_options(max_instances=10)

initialize_app()

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

        db.collection("people").document(p.generate_id()).set(p.to_dict(), merge=["zip"])
        db.collection("people").document(p.generate_id()).collection("rsvps").document(r.generate_id()).set(r.to_dict())

    except Exception as e:
        return https_fn.Response(f"An error occurred: {str(e)}", status=500)

    return https_fn.Response("RSVP successfully recorded.", status=200)

# Triggered when a new document is created in the "rsvps" subcollection
@on_document_created(document="people/{personId}/rsvps/{rsvpId}", database="default")
def handle_new_rsvp(event: Event[DocumentSnapshot]) -> None:
    # 1. Retrieve the parent document ID (personId) from event.params
    parent_id = event.params["personId"]
    
    # 2. Retrieve the newly created RSVP document ID
    rsvp_id = event.params["rsvpId"]
    
    # 3. Retrieve the actual document data
    event_code = event.data.to_dict().get("eventcode") if event.data else None

    ##TODO send email to rsvp_id