# Wearlytic - AI-Powered Clothing Brand Analytics

**Wearlytic** is an AI-driven web intelligence platform designed to collect, analyze, and visualize clothing brand data from various e-commerce platforms. It helps businesses track competitor strategies, identify market trends, and optimize product positioning through advanced data analytics.

## Project Structure

The project is organized into several key components:

### 1. Backend Service (`/backend`)
- Flask-based REST API service
- MongoDB database integration for product data storage
- Provides paginated product search and filtering capabilities
- Deployed on Vercel for scalability
- Features:
  - Advanced search filtering by description, brand, category
  - Price range filtering
  - Pagination support
  - MongoDB Atlas integration

### 2. Scraping Agent (`/scraping_agent`)
- Data ingestion component
- Concurrent web scraping capabilities
- Extracts product information from e-commerce platforms
- Features:
  - Automated data extraction
  - Product detail collection (pricing, availability, reviews)
  - Design attribute analysis
  - Concurrent request handling

### 3. Frontend Application (`/frontend`)
- Interactive dashboards and visualizations
- User-friendly interface for data exploration
- Features:
  - Real-time data visualization
  - Interactive product filtering
  - Trend analysis displays
  - Competitive analysis tools

### 4. Data Transformer (`/data-transformer`)
- Data processing and transformation pipeline
- Prepares raw scraped data for analysis
- Features:
  - Data cleaning and normalization
  - Feature extraction
  - Data enrichment
  - Format standardization

## Key Features
- **Automated Data Collection** – Intelligent scraping of product details including pricing, availability, reviews, and design attributes
- **AI-Powered Analytics** – Advanced analysis of clothing categories, pricing trends, and customer preferences
- **Competitive Intelligence** – Comprehensive brand comparison based on pricing strategies, product demand, and customer sentiment
- **Trend Prediction** – Machine learning models to identify emerging fashion trends and forecast product viability
- **Interactive Visualization** – Dynamic dashboards for data-driven decision making

## Use Cases
- Market research for fashion brands and retailers
- Competitive analysis and pricing strategy optimization
- Product development and customer preference analysis
- Trend identification and forecasting
- Inventory and pricing optimization

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Node.js and npm
- MongoDB Atlas account
- Vercel account (for backend deployment)

### Installation
1. Clone the repository
2. Set up each component following their respective README files
3. Configure environment variables
4. Start the services:
   - Backend: `cd backend && python app.py`
   - Frontend: `cd frontend && npm start`

## Development Status
> [!Warning]
> This project is actively under development. New features and improvements are being added regularly.
> The scraping agent is currently being enhanced for better concurrent request handling and data extraction capabilities.

## Contributing
Contributions are welcome! Please read our contributing guidelines and submit pull requests to the appropriate branches.

## License
This project is licensed under the terms specified in the LICENSE file.
