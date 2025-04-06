from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import math
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
api = Api(app)

# MongoDB connection
mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)
db = client['wearlytic']
products_collection = db['products']

class Products(Resource):
    def get(self):
        # Get query parameters
        search = request.args.get('search', '').lower()
        category = request.args.get('category', '')
        brand = request.args.get('brand', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        
        # Build MongoDB query
        query = {}
        
        # Search only in description and brand
        if search:
            query['$or'] = [
                {'description': {'$regex': search, '$options': 'i'}},
                {'brand': {'$regex': search, '$options': 'i'}}
            ]
        
        # Add category filter
        if category:
            query['category'] = {'$regex': category, '$options': 'i'}
        
        # Add brand filter
        if brand:
            query['brand'] = {'$regex': brand, '$options': 'i'}
        
        # Add price range filter
        if min_price or max_price:
            price_query = {}
            if min_price:
                # Remove ₹ and convert to float
                min_price_float = float(min_price.replace('₹', '').strip())
                price_query['$gte'] = min_price_float
            if max_price:
                # Remove ₹ and convert to float
                max_price_float = float(max_price.replace('₹', '').strip())
                price_query['$lte'] = max_price_float
            if price_query:
                query['price'] = price_query
        
        # Get total count of matching documents
        total_products = products_collection.count_documents(query)
        total_pages = math.ceil(total_products / per_page)
        
        # Get paginated results
        skip = (page - 1) * per_page
        products = list(products_collection.find(
            query,
            {'_id': 0}  # Exclude MongoDB's _id field
        ).skip(skip).limit(per_page))
        
        return {
            'products': products,
            'pagination': {
                'total': total_products,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        }

api.add_resource(Products, '/api/products')

if __name__ == '__main__':
    app.run(debug=True) 