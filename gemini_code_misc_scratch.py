from firebase_functions import https_fn
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

##trigger on create rsvp in firestore: https://firebase.google.com/docs/functions/firestore-events
@on_document_created(document="people/{person}/rsvps/{rsvp}")
def myfunction(event: Event[DocumentSnapshot]) -> None:

## FOLLOWING CODE WON"T WORK -- SEE GEMINI CODE BELOW

    try:
        new_value = event.data.to_dict()
        rsvp_id = event.data.id
        parent_email = event.data.reference.getParent().getParent().id
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    else:
        logger.debug(f"Data retrieved from event: rsvp_id={rsvp_id}, parent_email={parent_email}, new_value={new_value}, event_code={new_value.get('eventcode')}")

    ...#TODO send email. I guess we need event data, like start time and end time...

## This is how Gemini says to do it:

# Triggered when a new document is created in the "rsvps" subcollection
@on_document_created(document="people/{personId}/rsvps/{rsvpId}")
def handle_new_rsvp(event: Event[DocumentSnapshot]) -> None:
    # 1. Retrieve the parent document ID (personId) from event.params
    parent_id = event.params["personId"]
    
    # 2. Retrieve the newly created RSVP document ID
    rsvp_id = event.params["rsvpId"]
    
    # 3. Retrieve the actual document data
    rsvp_data = event.data.to_dict() if event.data else None

    # Your custom logic here
    print(f"RSVP {rsvp_id} created for parent person ID: {parent_id}")

## And this is how Gemini says to do if you wanted to do the "parents way":

@on_document_created(document="people/{personId}/rsvps/{rsvpId}")
def handle_new_rsvp(event: Event[DocumentSnapshot]) -> None:
    # Safely ensure event.data contains the document snapshot
    if event.data is not None:
        # 1. Get the DocumentReference for the new RSVP document
        rsvp_ref = event.data.reference  # e.g., people/123/rsvps/abc
        
        # 2. Get the CollectionReference ("rsvps")
        rsvps_collection_ref = rsvp_ref.parent  # e.g., people/123/rsvps
        
        # 3. Get the DocumentReference of the parent ("people/123")
        parent_doc_ref = rsvps_collection_ref.parent  # e.g., people/123
        
        # 4. Extract the parent's string ID
        if parent_doc_ref is not None:
            parent_id = parent_doc_ref.id
            print(f"Traversed parent ID: {parent_id}")