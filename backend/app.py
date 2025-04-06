from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
import math
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:5000", "http://localhost:5000", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
api = Api(app)

mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)
db = client['wearlytic']
products_collection = db['products']

class Products(Resource):
    def get(self):
        try:
            search = request.args.get('search', '').lower()
            category = request.args.get('category', '')
            brand = request.args.get('brand', '')
            min_price = request.args.get('min_price', '')
            max_price = request.args.get('max_price', '')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 5))
            
            query = {}
            
            if search:
                query['$or'] = [
                    {'description': {'$regex': search, '$options': 'i'}},
                    {'brand': {'$regex': search, '$options': 'i'}}
                ]
            
            if category:
                query['category'] = {'$regex': category, '$options': 'i'}
            
            if brand:
                query['brand'] = {'$regex': brand, '$options': 'i'}
            
            if min_price or max_price:
                price_query = {}
                if min_price:
                    min_price_float = float(min_price.replace('₹', '').strip())
                    price_query['$gte'] = min_price_float
                if max_price:
                    max_price_float = float(max_price.replace('₹', '').strip())
                    price_query['$lte'] = max_price_float
                if price_query:
                    query['price'] = price_query
            
            total_products = products_collection.count_documents(query)
            total_pages = math.ceil(total_products / per_page)
            
            skip = (page - 1) * per_page
            products = list(products_collection.find(
                query,
                {'_id': 0} 
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
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(Products, '/api/products')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000) 