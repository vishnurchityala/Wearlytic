from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
from functools import lru_cache
import logging
from concurrent.futures import ThreadPoolExecutor
import time
from typing import Optional, Tuple, List, Dict, Any
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
gen_model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB connection with retry logic
def get_mongodb_connection(max_retries: int = 3, retry_delay: int = 5) -> pymongo.MongoClient:
    for attempt in range(max_retries):
        try:
            client = pymongo.MongoClient(
                os.getenv('MONGODB_URI'),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=45000,
                maxPoolSize=50,
                minPoolSize=10
            )
            # Test the connection
            client.admin.command('ping')
            return client
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to MongoDB after {max_retries} attempts: {e}")
                raise
            logger.warning(f"MongoDB connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

# Initialize MongoDB connection
client = get_mongodb_connection()
db = client.get_database()
products_collection = db.products

# Cache for image analysis results
@lru_cache(maxsize=1000)
def get_cached_image_analysis(image_url: str, initial_tag: str) -> Dict[str, Any]:
    """Cache image analysis results to avoid redundant API calls"""
    color_result = get_dominant_color(image_url, initial_tag)
    tags = get_image_tags(image_url, initial_tag)
    return {
        'color': color_result,
        'tags': tags
    }

def get_color_code(rgb_tuple):
    """Convert RGB to closest standard color code"""
    standard_colors = {
        'red': ((255, 0, 0), '#FF0000'),
        'maroon': ((128, 0, 0), '#800000'),
        'orange': ((255, 165, 0), '#FFA500'),
        'yellow': ((255, 255, 0), '#FFFF00'),
        'olive': ((128, 128, 0), '#808000'),
        'lime': ((0, 255, 0), '#00FF00'),
        'green': ((0, 128, 0), '#008000'),
        'aqua': ((0, 255, 255), '#00FFFF'),
        'teal': ((0, 128, 128), '#008080'),
        'blue': ((0, 0, 255), '#0000FF'),
        'navy': ((0, 0, 128), '#000080'),
        'purple': ((128, 0, 128), '#800080'),
        'fuchsia': ((255, 0, 255), '#FF00FF'),
        'white': ((255, 255, 255), '#FFFFFF'),
        'silver': ((192, 192, 192), '#C0C0C0'),
        'gray': ((128, 128, 128), '#808080'),
        'black': ((0, 0, 0), '#000000'),
        'brown': ((165, 42, 42), '#A52A2A'),
        'beige': ((245, 245, 220), '#F5F5DC'),
        'pink': ((255, 192, 203), '#FFC0CB'),
        'gold': ((255, 215, 0), '#FFD700'),
        'khaki': ((240, 230, 140), '#F0E68C'),
        'lavender': ((230, 230, 250), '#E6E6FA'),
        'coral': ((255, 127, 80), '#FF7F50'),
        'turquoise': ((64, 224, 208), '#40E0D0')
    }

    def color_distance(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

    closest_color = min(standard_colors.items(), 
                       key=lambda x: color_distance(rgb_tuple, x[1][0]))
    return closest_color[0], closest_color[1][1]

def get_dominant_color(image_url: str, initial_tag: str = "") -> Optional[Tuple[tuple, str, str]]:
    """Get dominant color from image using Gemini AI"""
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        img_data = response.content

        prompt_text = (
            f"What is the dominant color of this {initial_tag}? "
            f"Focus on the main fabric color, ignoring any patterns or designs. "
            f"For clothing items, consider the primary color that covers most of the garment. "
            f"Provide the answer as an RGB tuple and a descriptive color name. "
            f"Give response in format: (255, 255, 255)white"
        )

        contents = [{
            "parts": [
                {"mime_type": "image/jpeg", "data": img_data},
                {"text": prompt_text},
            ]
        }]
        
        response = gen_model.generate_content(contents=contents)
        color_text = response.text.strip()

        start_paren = color_text.find("(")
        end_paren = color_text.find(")")
        if start_paren != -1 and end_paren != -1:
            color_tuple_str = color_text[start_paren:end_paren + 1]
            color_name = color_text[end_paren + 1:].split(',')[0].split()[-1].strip()
            color_tuple = eval(color_tuple_str)

            if (isinstance(color_tuple, tuple) and 
                len(color_tuple) == 3 and 
                all(0 <= x <= 255 for x in color_tuple)):
                # Get standardized color name and hex code
                std_color_name, hex_code = get_color_code(color_tuple)
                return color_tuple, std_color_name, hex_code

        return None
    except Exception as e:
        logger.error(f"Error in get_dominant_color: {str(e)}")
        return None

def get_image_tags(image_url: str, initial_tag: str = "") -> Optional[List[str]]:
    """Get image tags using Gemini AI"""
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        img_data = response.content

        prompt_text = (
            f"Analyze this {initial_tag} image and provide detailed descriptive tags. "
            f"Include tags for: style, fit, neckline, sleeve type, occasion, season, pattern, texture. "
            f"Also include general fashion and clothing-related descriptors. "
            f"Provide at least 15 specific, fashion-focused tags in a comma-separated format. "
            f"Focus on details that would be useful for fashion recommendations and style matching. "
            f"Do not include any text before or after the comma-separated list."
        )

        contents = [{
            "parts": [
                {"mime_type": "image/jpeg", "data": img_data},
                {"text": prompt_text},
            ]
        }]
        
        response = gen_model.generate_content(contents=contents)
        tags = response.text.strip()
        
        return [tag.strip() for tag in tags.split(',')] if tags else []
    except Exception as e:
        logger.error(f"Error in get_image_tags: {str(e)}")
        return []

def process_single_product(product: Dict[str, Any]) -> bool:
    """Process a single product for annotation"""
    try:
        image_url = product.get('image_url')
        initial_tag = product.get('category', '')

        if not image_url:
            return False

        # Get cached or new analysis results
        analysis_results = get_cached_image_analysis(image_url, initial_tag)
        
        update_data = {
            'dominant_color': {
                'rgb': analysis_results['color'][0] if analysis_results['color'] else None,
                'name': analysis_results['color'][1] if analysis_results['color'] else None,
                'hex': analysis_results['color'][2] if analysis_results['color'] else None
            },
            'tags': analysis_results['tags'],
            'colors': [analysis_results['color'][1]] if analysis_results['color'] else []  # Add color to colors array
        }

        result = products_collection.update_one(
            {'product_url': {'$regex': f'.*{product["_id"]}.*'}},  # Match product ID in URL
            {'$set': update_data}
        )

        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error processing product {product.get('_id')}: {str(e)}")
        return False

@app.route('/annotate', methods=['POST'])
def annotate_product():
    """Annotate a single product"""
    try:
        data = request.json
        product_id = str(data.get('product_id'))
        image_url = data.get('image_url')
        category = data.get('category', '')  # Use category as initial_tag

        if not product_id or not image_url:
            return jsonify({'error': 'Missing required fields'}), 400

        # Get cached or new analysis results
        analysis_results = get_cached_image_analysis(image_url, category)
        
        if analysis_results['color']:
            rgb_value, color_name, hex_code = analysis_results['color']
            color_info = {
                'rgb': rgb_value,
                'name': color_name,
                'hex': hex_code
            }
        else:
            color_info = {
                'rgb': None,
                'name': None,
                'hex': None
            }

        update_data = {
            'dominant_color': color_info,
            'tags': analysis_results['tags'],
            'colors': [color_info['name']] if color_info['name'] else []
        }

        # Update MongoDB document
        result = products_collection.update_one(
            {'product_url': {'$regex': f'.*{product_id}.*'}},
            {'$set': update_data}
        )

        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': 'Product annotated successfully',
                'data': update_data
            })
        else:
            return jsonify({
                'error': 'Product not found or no changes made'
            }), 404

    except Exception as e:
        logger.error(f"Error in annotate_product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/batch-annotate', methods=['POST'])
def batch_annotate():
    """Annotate multiple products in parallel"""
    try:
        data = request.json or {}
        batch_size = int(data.get('batch_size', 50))
        max_workers = int(data.get('max_workers', 5))

        # Find products that need annotation
        unannotated_products = list(products_collection.find({
            '$or': [
                {'dominant_color': {'$exists': False}},
                {'dominant_color': None},
                {'tags': {'$exists': False}},
                {'tags': None},
                {'colors': {'$exists': False}},
                {'colors': None}
            ]
        }).limit(batch_size))

        if not unannotated_products:
            return jsonify({
                'success': True,
                'message': 'No products need annotation'
            })

        def process_product(product):
            try:
                product_id = str(product.get('_id'))
                image_url = product.get('image_url')
                category = product.get('category', '')

                if not image_url:
                    return None

                # Get cached or new analysis results
                analysis_results = get_cached_image_analysis(image_url, category)
                
                if analysis_results['color']:
                    rgb_value, color_name, hex_code = analysis_results['color']
                    color_info = {
                        'rgb': rgb_value,
                        'name': color_name,
                        'hex': hex_code
                    }
                else:
                    color_info = {
                        'rgb': None,
                        'name': None,
                        'hex': None
                    }

                update_data = {
                    'dominant_color': color_info,
                    'tags': analysis_results['tags'],
                    'colors': [color_info['name']] if color_info['name'] else []
                }

                # Update MongoDB document
                result = products_collection.update_one(
                    {'_id': product['_id']},
                    {'$set': update_data}
                )

                return result.modified_count > 0
            except Exception as e:
                logger.error(f"Error processing product {product_id}: {str(e)}")
                return None

        # Process products in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_product, unannotated_products))

        successful_updates = sum(1 for r in results if r is True)
        
        return jsonify({
            'success': True,
            'message': f'Batch annotation completed. {successful_updates} products annotated.'
        })

    except Exception as e:
        logger.error(f"Error in batch_annotate: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/annotate-all', methods=['POST'])
def annotate_all():
    """Annotate all products in the database"""
    try:
        data = request.json or {}
        max_workers = int(data.get('max_workers', 5))
        batch_size = int(data.get('batch_size', 100))  # Process in batches to avoid memory issues

        # Get total count of products
        total_products = products_collection.count_documents({})
        processed_count = 0
        successful_updates = 0

        # Create a ThreadPoolExecutor outside the loop
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Process in batches
            while processed_count < total_products:
                try:
                    # Get next batch of products
                    products = list(products_collection.find().skip(processed_count).limit(batch_size))
                    
                    if not products:
                        break

                    def process_product(product):
                        try:
                            product_id = str(product.get('_id'))
                            image_url = product.get('image_url')
                            category = product.get('category', '')

                            if not image_url:
                                return None

                            # Get cached or new analysis results
                            analysis_results = get_cached_image_analysis(image_url, category)
                            
                            if analysis_results['color']:
                                rgb_value, color_name, hex_code = analysis_results['color']
                                color_info = {
                                    'rgb': rgb_value,
                                    'name': color_name,
                                    'hex': hex_code
                                }
                            else:
                                color_info = {
                                    'rgb': None,
                                    'name': None,
                                    'hex': None
                                }

                            update_data = {
                                'dominant_color': color_info,
                                'tags': analysis_results['tags'],
                                'colors': [color_info['name']] if color_info['name'] else []
                            }

                            # Update MongoDB document
                            result = products_collection.update_one(
                                {'_id': product['_id']},
                                {'$set': update_data}
                            )

                            return result.modified_count > 0
                        except Exception as e:
                            logger.error(f"Error processing product {product_id}: {str(e)}")
                            return None

                    # Process batch in parallel
                    futures = [executor.submit(process_product, product) for product in products]
                    results = [future.result() for future in futures]

                    successful_updates += sum(1 for r in results if r is True)
                    processed_count += len(products)

                    logger.info(f"Processed {processed_count}/{total_products} products. Successful updates: {successful_updates}")

                except Exception as e:
                    logger.error(f"Error processing batch: {str(e)}")
                    continue

        return jsonify({
            'success': True,
            'message': f'All products processed. {successful_updates} products annotated successfully.',
            'total_products': total_products,
            'successful_updates': successful_updates
        })

    except Exception as e:
        logger.error(f"Error in annotate_all: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get annotation statistics"""
    try:
        pipeline = [
            {
                '$facet': {
                    'total': [{'$count': 'count'}],
                    'annotated': [{
                        '$match': {
                            'dominant_color': {'$exists': True},
                            'tags': {'$exists': True}
                        }
                    }, {'$count': 'count'}],
                    'colors': [{
                        '$match': {'dominant_color.name': {'$exists': True}}
                    }, {
                        '$group': {
                            '_id': '$dominant_color.name',
                            'count': {'$sum': 1}
                        }
                    }],
                    'tags': [{
                        '$match': {'tags': {'$exists': True}}
                    }, {
                        '$unwind': '$tags'
                    }, {
                        '$group': {
                            '_id': '$tags',
                            'count': {'$sum': 1}
                        }
                    }, {
                        '$sort': {'count': -1}
                    }, {
                        '$limit': 10
                    }]
                }
            }
        ]

        stats = list(products_collection.aggregate(pipeline))[0]
        
        total = stats['total'][0]['count'] if stats['total'] else 0
        annotated = stats['annotated'][0]['count'] if stats['annotated'] else 0

        return jsonify({
            'total_products': total,
            'annotated_products': annotated,
            'remaining_products': total - annotated,
            'color_distribution': stats['colors'],
            'top_tags': stats['tags']
        })

    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api-usage', methods=['GET'])
def api_usage():
    """Provide usage instructions for the API"""
    usage_info = {
        "endpoints": {
            "/annotate": {
                "method": "POST",
                "description": "Annotate a single product.",
                "request_body": {
                    "product_id": "string, required",
                    "image_url": "string, required",
                    "category": "string, optional"
                },
                "response": {
                    "success": "boolean",
                    "message": "string",
                    "data": {
                        "dominant_color": {
                            "rgb": "tuple",
                            "name": "string",
                            "hex": "string"
                        },
                        "tags": "array of strings",
                        "colors": "array of strings"
                    }
                }
            },
            "/batch-annotate": {
                "method": "POST",
                "description": "Annotate multiple products in parallel.",
                "request_body": {
                    "batch_size": "integer, optional (default: 50)",
                    "max_workers": "integer, optional (default: 5)"
                },
                "response": {
                    "success": "boolean",
                    "message": "string"
                }
            },
            "/annotate-all": {
                "method": "POST",
                "description": "Annotate all products in the database.",
                "request_body": {
                    "batch_size": "integer, optional (default: 100)",
                    "max_workers": "integer, optional (default: 5)"
                },
                "response": {
                    "success": "boolean",
                    "message": "string",
                    "total_products": "integer",
                    "successful_updates": "integer"
                }
            },
            "/stats": {
                "method": "GET",
                "description": "Get annotation statistics.",
                "response": {
                    "total_products": "integer",
                    "annotated_products": "integer",
                    "remaining_products": "integer",
                    "color_distribution": "array of objects",
                    "top_tags": "array of objects"
                }
            }
        }
    }
    return jsonify(usage_info)

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    logger.error(f"Unhandled error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 