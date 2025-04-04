import json
from pymongo import MongoClient

# Correct MongoDB URI (Replace <password> with your actual password)
MONGO_URI = "mongodb+srv://vishnurchityala:IvMvsKYJrR7Eo0Cd@wearlytic.qhchiev.mongodb.net/?retryWrites=true&w=majority"

# Define database and collection names
DATABASE_NAME = "wearlytic"
COLLECTION_NAME = "products"
JSON_FILE = "output.json"  # JSON file to upload

def connect_mongodb():
    """Connect to MongoDB Atlas."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        print("✅ Connected to MongoDB Atlas successfully!")
        return db[COLLECTION_NAME]
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")
        exit()

def load_json(filename):
    """Load data from JSON file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Remove 'id' field from each document
        for doc in data:
            if "id" in doc:
                del doc["id"]  # Remove Firestore ID

        print(f"📂 Loaded {len(data)} documents from {filename}")
        return data
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        exit()

def insert_data(collection, data):
    """Insert data into MongoDB collection."""
    try:
        if isinstance(data, list):  # Insert multiple documents
            collection.insert_many(data)
        else:  # Insert a single document
            collection.insert_one(data)
        print("✅ Data successfully inserted into MongoDB Atlas!")
    except Exception as e:
        print(f"❌ Data Insertion Error: {e}")

if __name__ == "__main__":
    collection = connect_mongodb()
    data = load_json(JSON_FILE)

    if data:
        insert_data(collection, data)
    else:
        print("⚠️ No data found in the JSON file.")
