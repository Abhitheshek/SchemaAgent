from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from src.scraper import MySchemeScraper
from src.models import SchemeDetails, ScrapedData
import asyncio

class AgentState(TypedDict):
    query: Annotated[str, "Search query or empty"]
    filter_state: Annotated[str, "State filter"]
    filter_category: Annotated[str, "Category filter"]
    filter_age: Annotated[int, "Age filter"]
    scheme_urls: List[str]
    scraped_data: List[SchemeDetails]

async def search_node(state: AgentState):
    scraper = MySchemeScraper()
    await scraper.start()
    try:
        if state.get("filter_state"):
            print("Running FILTER search...")
            urls = await scraper.search_with_filters(
                state=state["filter_state"],
                category=state["filter_category"],
                age=state["filter_age"]
            )
        else:
            print("Running KEYWORD search...")
            query = state.get("query", "")
            urls = await scraper.search_schemes(query)
            
        return {"scheme_urls": urls}
    finally:
        await scraper.close()

async def scrape_node(state: AgentState):
    urls = state["scheme_urls"]
    scraper = MySchemeScraper()
    await scraper.start()
    data = []
    try:
        for url in urls:
            details = await scraper.scrape_scheme_details(url)
            data.append(details)
    finally:
        await scraper.close()
    return {"scraped_data": data}

def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("search", search_node)
    workflow.add_node("scrape", scrape_node)
    
    workflow.set_entry_point("search")
    workflow.add_edge("search", "scrape")
    workflow.add_edge("scrape", END)
    
    return workflow.compile()
