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
        # Initialize Firebase only once
        cred = credentials.Certificate("wearl-2649a-firebase-adminsdk-fbsvc-6cbf6cbf33.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def process_item(self, item, spider):
        # Define Firestore collection name
        collection_name = "products"

        data = dict(item)

        self.db.collection(collection_name).add(data)

        return item

