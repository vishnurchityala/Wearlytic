from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
import math
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS with specific configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Allow all origins in production
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
api = Api(app)

# MongoDB connection with optimized settings
mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(
    mongo_uri,
    serverSelectionTimeoutMS=5000,  # 5 seconds timeout for server selection
    socketTimeoutMS=45000,          # 45 seconds timeout for operations
    connectTimeoutMS=10000,         # 10 seconds timeout for connection
    maxPoolSize=50,                 # Maximum number of connections in the pool
    minPoolSize=10                  # Minimum number of connections in the pool
)
db = client['wearlytic']
products_collection = db['products']

class Products(Resource):
    def get(self):
        try:
            start_time = time.time()
            
            # Get query parameters
            search = request.args.get('search', '').lower()
            category = request.args.get('category', '')
            brand = request.args.get('brand', '')
            min_price = request.args.get('min_price', '')
            max_price = request.args.get('max_price', '')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 5))
            
            # Validate page size
            if per_page > 50:
                per_page = 50
            
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
            
            # Get paginated results with projection
            skip = (page - 1) * per_page
            products = list(products_collection.find(
                query,
                {
                    '_id': 0,
                    'description': 1,
                    'product_url': 1,
                    'source': 1,
                    'product_name': 1,
                    'image_url': 1,
                    'category': 1,
                    'price': 1,
                    'colors': 1,
                    'brand': 1,
                    'material': 1,
                    'timestamp': 1
                }
            ).skip(skip).limit(per_page))
            
            execution_time = time.time() - start_time
            print(f"Query executed in {execution_time:.2f} seconds")
            
            return {
                'products': products,
                'pagination': {
                    'total': total_products,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages
                }
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return {'error': str(e)}, 500

api.add_resource(Products, '/api/products')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000) 