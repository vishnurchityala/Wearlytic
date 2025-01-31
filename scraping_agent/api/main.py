"""
This REST API will be used to initiate an asynchronous scraping task by providing a job_id and relevant details for
scraping. It will handle saving the results to a database and provide real-time updates on the status of the
scraping task.

SAMPLE CALLING METHOD:

curl -X POST "http://localhost:8000/scrape" \
-H "Content-Type: application/json" \
-d '{
  "urls": ["https://www.amazon.in/s?k=shoes"],
  "selectors": {
    "product": {
      "product_container": {
        "type": "element",
        "selector": "//div[contains(@class, \"s-main-slot s-result-list\")]//div[contains(@class, \"puis-card-container \")]"
      },
      "info": {
        "title": {
          "type": "text",
          "selector": ".//div[contains(@data-cy, \"title-recipe\")]/a/h2/span/text()"
        },
        "price": {
          "type": "text",
          "selector": ".//span[contains(@class, \"price-whole\")]/text()"
        }
      }
    }
  },
  "job_id": "job_amazon_scrape"
}'

SAMPLE RESPONSE :

{
    "status": "success",
    "data": [
        {
            "url": "https://www.amazon.in/s?k=shoes",
            "timestamp": "2025-01-31T22:36:35.803245",
            "data": [
                {
                    "title": [
                        "Men's Wonder-13 Sports Running Shoes…"
                    ],
                    "price": [
                        "599"
                    ],
                    "page_rank": 1
                },
                {
                    "title": [
                        "Exclusive Trendy Sports Running Shoes | Casual Shoe | Sneakers for Men's & Boy's"
                    ],
                    "price": [
                        "265"
                    ],
                    "page_rank": 2
                },
                {
                    "title": [
                        "Mens Indus-251 Running Shoe"
                    ],
                    "price": [
                        "554"
                    ],
                    "page_rank": 3
                }
            ]
        }
    ]
}
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
from typing import List, Dict, Any

app = FastAPI()

SCRAPY_PROJECT_PATH = "../scraping_agent"


class ScrapeRequest(BaseModel):
    urls: List[str]
    selectors: Dict[str, Any]
    job_id: str


@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    command = [
        "scrapy",
        "crawl",
        "dynamic_spider",
        "-a", f"urls={json.dumps(request.urls)}",
        "-a", f"selectors={json.dumps(request.selectors)}",
        "-a", f"job_id={request.job_id}",
        "-s", "LOG_ENABLED=False"
    ]

    try:
        result = subprocess.run(
            command,
            cwd=SCRAPY_PROJECT_PATH,
            capture_output=True,
            text=True,
            check=True
        )

        try:
            output = json.loads(result.stdout)
            return {"status": "success", "data": output}
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse spider output"
            )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scrapy error: {e.stderr}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
