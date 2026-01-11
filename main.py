from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import asyncio
from src.graph import create_graph
from src.models import ScrapedData, SchemeDetails
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MyScheme Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    query: Optional[str] = None
    filter_state: Optional[str] = None
    filter_category: Optional[str] = None
    filter_age: Optional[int] = None

@app.post("/scrape", response_model=ScrapedData)
async def scrape_schemes(request: ScrapeRequest):
    print(f"Received scrape request: {request}")
    
    # Construct initial state matching main.py structure
    initial_state = {
        "query": request.query,
        "filter_state": request.filter_state,
        "filter_category": request.filter_category,
        "filter_age": request.filter_age,
        "scheme_urls": [],
        "scraped_data": []
    }
    
    # Default age if using filters and not provided
    if (initial_state["filter_state"] or initial_state["filter_category"]) and not initial_state["filter_age"]:
         initial_state["filter_age"] = 18

    try:
        graph = create_graph()
        result = await graph.ainvoke(initial_state)
        
        scraped_data = result.get("scraped_data", [])
        
        return ScrapedData(
            query=request.query,
            filter_state=request.filter_state,
            filter_category=request.filter_category,
            filter_age=request.filter_age,
            schemes=scraped_data
        )
    except Exception as e:
        print(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
