import json
import pandas as pd
from google.cloud import firestore

# Set up Firestore client (Replace 'your-service-account.json' with your file)
FIREBASE_CREDENTIALS = "firebase-key.json"
db = firestore.Client.from_service_account_json(FIREBASE_CREDENTIALS)

def fetch_collection(collection_name):
    """Fetch all documents from a Firestore collection."""
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()

    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['id'] = doc.id  # Include document ID
        data.append(doc_dict)

    return data

def save_to_json(data, filename="output.json"):
    """Save data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

def save_to_csv(data, filename="output.csv"):
    """Save data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    collection_name = input("Enter Firestore collection name: ")
    data = fetch_collection(collection_name)

    if data:
        save_to_json(data, "output.json")
        save_to_csv(data, "output.csv")
    else:
        print("No data found in the collection.")
