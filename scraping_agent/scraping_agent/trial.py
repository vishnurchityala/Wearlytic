import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("wearl-2649a-firebase-adminsdk-fbsvc-6cbf6cbf33.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Reference to the collection
collection_ref = db.collection("products")

# Query using the 'where' method
query = collection_ref.where("source", "==", "flipkart.com").stream()

# Delete matching documents
deleted_count = 0
for doc in query:
    doc.reference.delete()
    deleted_count += 1

print(f"Deleted {deleted_count} documents from 'products' collection.")
