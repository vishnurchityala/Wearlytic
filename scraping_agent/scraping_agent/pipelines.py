# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import firebase_admin
from firebase_admin import credentials, firestore


class FirebasePipeline:
    def __init__(self):
        cred = credentials.Certificate("wearl-2649a-firebase-adminsdk-fbsvc-6cbf6cbf33.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def process_item(self, item, spider):
        # Define Firestore collection name
        collection_name = "products_trial"

        # Remove keys with None, empty strings, and empty dictionaries
        filtered_data = {k: v for k, v in dict(item).items() if v not in [None, ""] and not (isinstance(v, dict) and not v)}

        # Only add to Firestore if there's valid data
        if filtered_data:
            self.db.collection(collection_name).add(filtered_data)

        return item