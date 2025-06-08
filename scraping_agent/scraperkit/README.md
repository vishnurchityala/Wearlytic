# ScraperKit

ScraperKit is a sophisticated web scraping framework built with a focus on reliability, maintainability, and anti-detection capabilities. It provides a structured approach to web scraping through a modular architecture that separates concerns and promotes code reuse.

## Package Structure

### 1. Base Package (`base/`)
The foundation of the framework containing abstract base classes and interfaces:
- `base_content_loader.py`: Abstract base class defining the interface for content loading
- `base_scraper.py`: Abstract base class for implementing specific scrapers
- Provides the contract that all concrete implementations must follow

### 2. Loaders Package (`loaders/`)
Implements different strategies for loading web content:
- `selenium_content_loader.py`: Selenium-based implementation for JavaScript-heavy websites
- Handles browser automation, anti-detection measures, and content extraction
- Manages browser instances and resources

### 3. Exceptions Package (`exceptions/`)
Custom exception hierarchy for robust error handling:
- `bad_url_exception.py`: Invalid URL or 404 errors
- `content_not_loaded_exception.py`: Content loading failures
- `data_component_not_found_exception.py`: Missing expected data elements
- `data_parsing_exception.py`: Data parsing errors
- `rate_limit_exception.py`: Rate limiting detection
- `timeout_exception.py`: Request timeout handling

### 4. Models Package (`models/`)
Data structures and schemas for scraped content:
- `product.py`: Product data model with validation
- Defines the structure of scraped data
- Ensures data consistency and type safety

### 5. Scrapers Package (`scrapers/`)
Domain-specific scraping implementations:
- `amazon_scraper.py`: Amazon-specific scraping logic
- `myntra_scraper.py`: Myntra-specific scraping logic
- Each scraper implements the base scraper interface
- Contains site-specific parsing and extraction logic

## Core Concepts

### 1. Content Loading Strategy
The framework implements a strategy pattern for content loading, allowing different approaches to fetch web content:
- **Base Content Loader**: An abstract base class that defines the interface for all content loaders
- **Selenium Loader**: A concrete implementation using Selenium WebDriver for JavaScript-heavy websites
- **Extensible Design**: Easy to add new content loading strategies (e.g., requests-based, playwright-based)

### 2. Anti-Bot Detection
The framework incorporates multiple layers of anti-bot detection measures:
- Browser fingerprint randomization
- Dynamic header management
- JavaScript execution masking
- Automation detection prevention
- Browser behavior simulation

### 3. Error Handling Architecture
A robust error handling system that categorizes and manages different types of scraping failures:
- Network-related errors
- Content validation errors
- Bot detection responses
- Timeout scenarios
- Invalid URL handling

### 4. Modular Design
The framework is organized into distinct modules:
```
scraperkit/
├── base/          # Core abstractions and interfaces
├── loaders/       # Content loading implementations
├── exceptions/    # Custom exception hierarchy
├── models/        # Data structures and schemas
└── scrapers/      # Domain-specific scraping logic
```

### 5. Key Features
- **Separation of Concerns**: Clear separation between content loading, parsing, and processing
- **Configurable Behavior**: Flexible configuration for timeouts, headers, and browser settings
- **Resource Management**: Proper handling of browser instances and system resources
- **Extensibility**: Easy to extend with new loaders, scrapers, or processing logic

## Architecture Overview

### Content Loading Flow
1. URL validation and preprocessing
2. Browser instance management
3. Content fetching with retry logic
4. Response validation and error handling
5. Resource cleanup

### Anti-Detection Measures
1. Browser fingerprint randomization
2. Header rotation and management
3. JavaScript execution masking
4. Automation detection prevention
5. Natural browsing behavior simulation

### Error Handling Strategy
1. Hierarchical exception system
2. Graceful degradation
3. Automatic retry mechanisms
4. Detailed error reporting
5. Resource cleanup on failure

## Best Practices

1. **Resource Management**
   - Always use context managers or explicit cleanup
   - Handle browser instances properly
   - Implement proper timeout handling

2. **Anti-Detection**
   - Rotate user agents and headers
   - Implement random delays
   - Mask automation signatures
   - Simulate human-like behavior

3. **Error Handling**
   - Use specific exception types
   - Implement proper logging
   - Handle cleanup in finally blocks
   - Implement retry mechanisms

4. **Extensibility**
   - Follow the base class contracts
   - Implement proper interfaces
   - Use dependency injection
   - Keep modules loosely coupled

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage with Selenium Content Loader

```python
from scraperkit.loaders.selenium_content_loader import SeleniumContentLoader

# Initialize the content loader
content_loader = SeleniumContentLoader(
    timeout=30,  # Optional: Set timeout in seconds
    headless=True  # Optional: Run browser in headless mode
)

try:
    # Load content from a URL
    page_content = content_loader.load_content("https://example.com")
    
    # Process the content as needed
    print(page_content)
    
finally:
    # Always close the loader to free resources
    content_loader.close()
```

### Custom Headers

```python
custom_headers = {
    "User-Agent": "Custom User Agent",
    "Accept-Language": "en-US,en;q=0.9",
    # Add more headers as needed
}

content_loader = SeleniumContentLoader(headers=custom_headers)
```

## Project Structure

```
scraperkit/
├── base/
│   └── base_content_loader.py    # Abstract base class for content loaders
├── loaders/
│   └── selenium_content_loader.py # Selenium-based content loader implementation
├── exceptions/                   # Custom exceptions
├── models/                      # Data models
└── scrapers/                    # Specific scraper implementations
```

## Error Handling

The toolkit includes custom exceptions for common scenarios:

- `BadURLException`: Raised when the URL is invalid or returns a 404
- `TimeoutException`: Raised when the request times out