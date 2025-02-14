import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("wearl-2649a-firebase-adminsdk-fbsvc-6cbf6cbf33.json")  # Replace with your service account key file
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# Load JSON file
with open("myntra_products.json", "r") as file:  # Replace with your JSON file
    data = json.load(file)

# Ensure data is a list of objects
if isinstance(data, list):
    collection_name = "products"  # Replace with your Firestore collection name
    for item in data:
        db.collection(collection_name).add(item)
        print(item)
    print(f"Successfully added {len(data)} documents to '{collection_name}' collection.")
else:
    print("Error: JSON data is not an array of objects.")
