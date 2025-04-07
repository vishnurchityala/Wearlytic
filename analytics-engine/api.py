import os
import pymongo
from dotenv import load_dotenv
from collections import Counter
from typing import List, Dict, Any, Tuple
import pandas as pd
import re
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app) 

def get_mongodb_connection():
    try:
        client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

def get_products_collection():
    client = get_mongodb_connection()
    if client is None:
        return None
    db = client.get_database()
    return db.products

def get_top_colors_and_products(limit: int = 5, products_per_color: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    products_collection = get_products_collection()
    if products_collection is None:
        return {}
    
    products_with_colors = list(products_collection.find(
        {"dominant_color.name": {"$exists": True}},
        {"_id": 1, "product_name": 1, "price": 1, "dominant_color": 1, "product_url": 1}
    ))
    
    if not products_with_colors:
        return {}
    
    color_counts = Counter()
    for product in products_with_colors:
        dominant_color = product.get("dominant_color", {})
        if dominant_color is not None and "name" in dominant_color:
            color_counts[dominant_color["name"]] += 1
    
    top_colors = color_counts.most_common(limit)
    
    result = {}
    for color, count in top_colors:
        color_products = [
            {
                "title": p.get("product_name", "Unknown"),
                "price": p.get("price", "N/A"),
                "url": p.get("product_url", "N/A")
            }
            for p in products_with_colors 
            if p.get("dominant_color", {}).get("name") == color
        ][:products_per_color]
        
        result[color] = {
            "count": count,
            "products": color_products
        }
    
    return result

def get_top_designs_and_products(limit: int = 5, products_per_design: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    products_collection = get_products_collection()
    if products_collection is None:
        return {}
    
    products_with_tags = list(products_collection.find(
        {"tags": {"$exists": True}},
        {"_id": 1, "product_name": 1, "price": 1, "tags": 1, "product_url": 1}
    ))
    
    if not products_with_tags:
        return {}
    
    all_tags = []
    for product in products_with_tags:
        tags = product.get("tags", [])
        if tags is None:
            tags = []
            
        clean_tags = [tag for tag in tags 
                     if tag is not None and not (isinstance(tag, str) and (
                         tag.startswith("Here are the") or 
                         "box_2d" in tag or 
                         "json" in tag or
                         re.match(r'^\[|\]$', tag)
                     ))]
        all_tags.extend(clean_tags)
    
    tag_counts = Counter(all_tags)
    top_tags = tag_counts.most_common(limit)
    
    result = {}
    for tag, count in top_tags:
        tag_products = [
            {
                "title": p.get("product_name", "Unknown"),
                "price": p.get("price", "N/A"),
                "url": p.get("product_url", "N/A")
            }
            for p in products_with_tags 
            if tag in [t for t in p.get("tags", []) 
                      if t is not None and not (isinstance(t, str) and (
                          t.startswith("Here are the") or 
                          "box_2d" in t or 
                          "json" in t or
                          re.match(r'^\[|\]$', t)
                      ))]
        ][:products_per_design]
        
        result[tag] = {
            "count": count,
            "products": tag_products
        }
    
    return result

def get_average_price_by_category() -> Dict[str, float]:
    products_collection = get_products_collection()
    if products_collection is None:
        return {}
    
    products = list(products_collection.find(
        {"category": {"$exists": True}, "price": {"$exists": True}},
        {"category": 1, "price": 1}
    ))
    
    if not products:
        return {}
    
    for product in products:
        if product.get("price") is None:
            product["price"] = 0.0
        elif isinstance(product["price"], str):
            price_str = product["price"].replace("₹", "").replace(",", "").strip()
            try:
                product["price"] = float(price_str)
            except ValueError:
                product["price"] = 0.0
    
    df = pd.DataFrame(products)
    if not df.empty:
        avg_prices = df.groupby("category")["price"].mean().to_dict()
        return avg_prices
    else:
        return {}

def get_brand_analysis() -> Dict[str, Any]:
    products_collection = get_products_collection()
    if products_collection is None:
        return {}
    
    products = list(products_collection.find(
        {"brand": {"$exists": True}},
        {"brand": 1, "price": 1, "category": 1}
    ))
    
    if not products:
        return {}
    
    for product in products:
        if product.get("price") is None:
            product["price"] = 0.0
        elif isinstance(product.get("price"), str):
            price_str = product["price"].replace("₹", "").replace(",", "").strip()
            try:
                product["price"] = float(price_str)
            except ValueError:
                product["price"] = 0.0
    
    df = pd.DataFrame(products)
    
    brand_counts = df["brand"].value_counts().to_dict()
    
    avg_price_by_brand = df.groupby("brand")["price"].mean().to_dict()
    
    brand_categories = {}
    for brand in df["brand"].unique():
        brand_df = df[df["brand"] == brand]
        categories = brand_df["category"].value_counts().head(3).to_dict()
        brand_categories[brand] = categories
    
    return {
        "brand_counts": brand_counts,
        "avg_price_by_brand": avg_price_by_brand,
        "top_categories_by_brand": brand_categories
    }

def get_price_range_analysis() -> Dict[str, Any]:
    products_collection = get_products_collection()
    if products_collection is None:
        return {}
    
    products = list(products_collection.find(
        {"price": {"$exists": True}},
        {"price": 1, "category": 1, "brand": 1}
    ))
    
    if not products:
        return {}
    
    for product in products:
        if product.get("price") is None:
            product["price"] = 0.0
        elif isinstance(product.get("price"), str):
            price_str = product["price"].replace("₹", "").replace(",", "").strip()
            try:
                product["price"] = float(price_str)
            except ValueError:
                product["price"] = 0.0
    
    df = pd.DataFrame(products)
    
    price_ranges = {
        "Budget (₹0-500)": (0, 500),
        "Mid-Range (₹501-1000)": (501, 1000),
        "Premium (₹1001-2000)": (1001, 2000),
        "Luxury (₹2001+)": (2001, float('inf'))
    }
    
    price_range_counts = {}
    for range_name, (min_price, max_price) in price_ranges.items():
        count = len(df[(df["price"] >= min_price) & (df["price"] <= max_price)])
        price_range_counts[range_name] = count
    
    price_range_categories = {}
    for range_name, (min_price, max_price) in price_ranges.items():
        range_df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]
        if not range_df.empty:
            categories = range_df["category"].value_counts().head(3).to_dict()
            price_range_categories[range_name] = categories
    
    price_range_brands = {}
    for range_name, (min_price, max_price) in price_ranges.items():
        range_df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]
        if not range_df.empty:
            brands = range_df["brand"].value_counts().head(3).to_dict()
            price_range_brands[range_name] = brands
    
    return {
        "price_range_counts": price_range_counts,
        "top_categories_by_price_range": price_range_categories,
        "top_brands_by_price_range": price_range_brands
    }

def get_seasonal_analysis() -> Dict[str, Any]:
    products_collection = get_products_collection()
    if products_collection is None:
        return {}
    
    products = list(products_collection.find(
        {"tags": {"$exists": True}},
        {"tags": 1, "price": 1, "category": 1}
    ))
    
    if not products:
        return {}
    
    seasons = {
        "Spring": ["spring", "floral", "light", "pastel"],
        "Summer": ["summer", "beach", "swim", "lightweight", "breathable"],
        "Fall": ["fall", "autumn", "layered", "warm"],
        "Winter": ["winter", "cold", "warm", "cozy", "knit", "wool"]
    }
    
    season_counts = {season: 0 for season in seasons}
    season_categories = {season: {} for season in seasons}
    
    for product in products:
        tags = product.get("tags", [])
        if tags is None:
            tags = []
            
        clean_tags = [tag.lower() for tag in tags 
                     if tag is not None and not (isinstance(tag, str) and (
                         tag.startswith("Here are the") or 
                         "box_2d" in tag or 
                         "json" in tag or
                         re.match(r'^\[|\]$', tag)
                     ))]
        
        for season, season_tags in seasons.items():
            if any(tag in clean_tags for tag in season_tags):
                season_counts[season] += 1
                
                category = product.get("category", "Unknown")
                if category in season_categories[season]:
                    season_categories[season][category] += 1
                else:
                    season_categories[season][category] = 1
    
    return {
        "season_counts": season_counts,
        "categories_by_season": season_categories
    }

@app.route('/api/colors', methods=['GET'])
def api_colors():
    try:
        limit = request.args.get('limit', default=5, type=int)
        products_per_color = request.args.get('products_per_color', default=5, type=int)
        return jsonify(get_top_colors_and_products(limit, products_per_color))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/designs', methods=['GET'])
def api_designs():
    try:
        limit = request.args.get('limit', default=5, type=int)
        products_per_design = request.args.get('products_per_design', default=5, type=int)
        return jsonify(get_top_designs_and_products(limit, products_per_design))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def api_categories():
    try:
        return jsonify(get_average_price_by_category())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/brands', methods=['GET'])
def api_brands():
    try:
        return jsonify(get_brand_analysis())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/price-ranges', methods=['GET'])
def api_price_ranges():
    try:
        return jsonify(get_price_range_analysis())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/seasons', methods=['GET'])
def api_seasons():
    try:
        return jsonify(get_seasonal_analysis())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/all', methods=['GET'])
def api_all():
    try:
        return jsonify({
            "colors": get_top_colors_and_products(),
            "designs": get_top_designs_and_products(),
            "categories": get_average_price_by_category(),
            "brands": get_brand_analysis(),
            "price_ranges": get_price_range_analysis(),
            "seasons": get_seasonal_analysis()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5050) 