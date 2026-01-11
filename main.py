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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    query: Optional[str] = None
    filter_state: Optional[str] = None
    filter_category: Optional[str] = None
    filter_age: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "Government Scheme Scraper API is running"}

@app.get("/test")
async def test():
    return {"status": "API is working", "cors": "enabled"}

@app.post("/scrape", response_model=ScrapedData)
async def scrape_schemes(request: ScrapeRequest):
    initial_state = {
        "query": request.query,
        "filter_state": request.filter_state,
        "filter_category": request.filter_category,
        "filter_age": request.filter_age or 18,
        "scheme_urls": [],
        "scraped_data": []
    }
    
    try:
        graph = create_graph()
        result = await graph.ainvoke(initial_state)
        
        return ScrapedData(
            query=request.query,
            filter_state=request.filter_state,
            filter_category=request.filter_category,
            filter_age=request.filter_age,
            schemes=result.get("scraped_data", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
