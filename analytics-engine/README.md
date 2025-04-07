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

## Deployment

This API is configured for deployment on Vercel using the `vercel.json` configuration file. 