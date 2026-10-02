from firebase_functions import https_fn
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app, firestore

from datetime import datetime
import os

import dateutil

from models.person import Person
from models.rsvp import Rsvp

set_global_options(max_instances=10)

initialize_app()

@https_fn.on_request(cors=False)
def rsvp(req: https_fn.Request) -> https_fn.Response:

    try:

        now = datetime.now().astimezone(dateutil.tz.gettz(os.environ.get("America/New_York")))
        
        p = Person(req.json["firstname"], req.json["lastname"], now, req.json["email"])
        r = Rsvp(now, req.json["eventcode"])

        db = firestore.client()

        db.collection("people").document(p.generate_id()).set(p.to_dict(), merge=True)
        db.collection("people").document(p.generate_id()).collection("rsvps").document(r.generate_id()).set(r.to_dict())

    except Exception as e:
        return https_fn.Response(f"An error occurred: {str(e)}", status=500)

    return https_fn.Response("RSVP successfully recorded.", status=200)