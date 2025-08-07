# Flask Products API with MongoDB

A Flask REST API that provides paginated product search functionality using MongoDB as the database.

## Prerequisites

1. MongoDB Atlas account with a cluster
2. Python 3.7 or higher
3. Vercel account (for deployment)

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MongoDB:
   - Update the `MONGODB_URI` in `.env` file with your MongoDB Atlas connection string
   - Make sure your Atlas cluster's IP whitelist includes your application's IP address

4. Run the application locally:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Set up environment variables in Vercel:
```bash
vercel env add MONGODB_URI
```
Enter your MongoDB Atlas connection string when prompted.

4. Deploy to Vercel:
```bash
vercel
```

5. For subsequent deployments:
```bash
vercel --prod
```

The API will be available at your Vercel deployment URL.

## Database Schema

The API expects a MongoDB database named `products_db` with a collection named `products`. Each product document should have the following structure:

```json
{
    "description": "Product description",
    "product_url": "URL to product page",
    "source": "Source website",
    "product_name": "Product name",
    "image_url": "URL to product image",
    "category": "Product category",
    "price": "₹Price in INR",
    "colors": ["Color options"],
    "brand": "Brand name",
    "material": "Material type",
    "timestamp": 1234567890.12345
}
```

## API Endpoints

### GET /api/products

Returns a paginated list of products with advanced search filtering.

#### Query Parameters:
- `search` (optional): Search term to filter products by description or brand name
- `category` (optional): Filter by specific category
- `brand` (optional): Filter by specific brand
- `min_price` (optional): Minimum price filter (e.g., "₹500")
- `max_price` (optional): Maximum price filter (e.g., "₹2000")
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Number of items per page (default: 5)

#### Example Response:
```json
{
    "products": [
        {
            "description": "Product description",
            "product_url": "https://example.com/product",
            "source": "myntra.com",
            "product_name": "Product Name",
            "image_url": "https://example.com/image.jpg",
            "category": "Category",
            "price": "₹999",
            "colors": [],
            "brand": "Brand Name",
            "material": "Material Type",
            "timestamp": 1234567890.12345
        }
    ],
    "pagination": {
        "total": 100,
        "page": 1,
        "per_page": 5,
        "total_pages": 20
    }
}
```

#### Example Usage:
- Search in description and brand: `GET /api/products?search=cotton`
- Filter by category: `GET /api/products?category=tshirts`
- Filter by brand: `GET /api/products?brand=MANGO`
- Price range: `GET /api/products?min_price=₹500&max_price=₹2000`
- Combined filters: `GET /api/products?category=jeans&brand=jack&min_price=₹1000&max_price=₹3000`
- Pagination: `GET /api/products?page=2&per_page=10` 