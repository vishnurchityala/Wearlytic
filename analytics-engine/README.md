# Analytics Engine API

This API provides analytics data for product information stored in MongoDB.

## API Endpoints

### Colors Analysis
- **Endpoint**: `/api/colors`
- **Method**: GET
- **Parameters**:
  - `limit` (optional): Number of top colors to return (default: 5)
  - `products_per_color` (optional): Number of sample products per color (default: 5)

### Designs Analysis
- **Endpoint**: `/api/designs`
- **Method**: GET
- **Parameters**:
  - `limit` (optional): Number of top designs to return (default: 5)
  - `products_per_design` (optional): Number of sample products per design (default: 5)

### Categories Analysis
- **Endpoint**: `/api/categories`
- **Method**: GET
- **Description**: Returns average price by category

### Brands Analysis
- **Endpoint**: `/api/brands`
- **Method**: GET
- **Description**: Returns brand counts, average price by brand, and top categories by brand

### Price Ranges Analysis
- **Endpoint**: `/api/price-ranges`
- **Method**: GET
- **Description**: Returns product counts by price range, top categories by price range, and top brands by price range

### Seasonal Analysis
- **Endpoint**: `/api/seasons`
- **Method**: GET
- **Description**: Returns product counts by season and categories by season

### All Analytics
- **Endpoint**: `/api/all`
- **Method**: GET
- **Description**: Returns all analytics data in a single response

## Environment Variables

The following environment variables need to be set:

- `MONGODB_URI`: MongoDB connection string

## Deployment to Render

### Prerequisites
- A Render account (sign up at [render.com](https://render.com))
- Your MongoDB connection string

### Deployment Steps

1. **Create a new Web Service on Render**
   - Log in to your Render dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub repository

2. **Configure the Web Service**
   - Name: `wearlytic-analytics` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn api:app`
   - Select the branch to deploy (usually `main`)

3. **Set Environment Variables**
   - Add the following environment variable:
     - Key: `MONGODB_URI`
     - Value: Your MongoDB connection string

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your application

5. **Access Your API**
   - Once deployed, Render will provide a URL for your API
   - Example: `https://wearlytic-analytics.onrender.com`

## Local Development

To run the API locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python api.py
```

The API will be available at `http://localhost:5000`. 