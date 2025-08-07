
# Scraping Agent API

FastAPI microservice for web scraping and product data ingestion. Integrates with Wearlytic analytics platform.

## How It Works

- Start scraping jobs for product listings or individual products
- Check job status
- Get scrape results
- Uses Celery for background tasks

## API Endpoints

### Listing Scrape

- **POST `/api/scrape/listing/`**
  - Start a new listing scrape job
  - Request:
    ```json
    { "webpage_url": "https://example.com/listings" }
    ```
  - Response:
    ```json
    { "task_id": "celery-task-id" }
    ```

- **GET `/api/scrape/listing/{task_id}/status/`**
  - Get status of a listing scrape job
  - Response:
    ```json
    { "message": "Status response" }
    ```

- **GET `/api/scrape/listing/{task_id}/result/`**
  - Get result of a completed listing scrape job
  - Response: Listing data (see JobResult model)

### Product Scrape

- **POST `/api/scrape/product/`**
  - Start a new product scrape job
  - Request:
    ```json
    { "webpage_url": "https://example.com/product/123" }
    ```
  - Response:
    ```json
    { "task_id": "celery-task-id" }
    ```

- **GET `/api/scrape/product/{task_id}/status/`**
  - Get status of a product scrape job
  - Response:
    ```json
    { "message": "Status response" }
    ```

- **GET `/api/scrape/product/{task_id}/result/`**
  - Get result of a completed product scrape job
  - Response: Product data (see JobResult model)

## Extending

- Add scrapers in `scraperkit/scrapers/`
- Add routes in `api/routes/`
- Update models in `api/models/`