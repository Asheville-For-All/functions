## this is how to generate a link, with a non-expiring token. (Apparently this is unusual! Firebase has a way to make files "public", and then there's a way to do expiring tokens, but the way to do non-expiring tokens is more complicated.)

##NB: might need to install cloud admin:
##
## pip install firebase-admin google-cloud-storage


import urllib.parse
from uuid import uuid4
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase Admin SDK (Skip if already initialized)
# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'your-project-id.firebasestorage.app'
# })

def get_firebase_token_url(blob_path):
    bucket = storage.bucket()
    blob = bucket.blob(blob_path)
    
    # 1. Generate a unique token
    token = str(uuid4())
    
    # 2. Assign the token to the required custom metadata key
    # If you are uploading a new file, you can set metadata during upload instead
    blob.metadata = {"firebaseStorageDownloadTokens": token}
    blob.patch()  # Sends the metadata update to Google Cloud Storage
    
    # 3. URL-encode the file path (crucial for nested paths like 'folders/image.png')
    encoded_path = urllib.parse.quote(blob_path, safe="")
    
    # 4. Construct the persistent public URL
    download_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{encoded_path}?alt=media&token={token}"
    
    return download_url

# Usage Example:
# url = get_firebase_token_url("user_uploads/profile.png")
# print("Download URL:", url)
