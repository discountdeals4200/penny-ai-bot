"""FastAPI server for bot control and data retrieval."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger
from bot.database import Database
from bot.scraper import RetailScraper
from bot.ai_engine import PennyAIEngine
import asyncio
from config import OPENAI_API_KEY, OPENAI_MODEL

app = FastAPI(
    title="Penny AI Bot API",
    description="API for penny item and lowest-price item search",
    version="1.0.0"
)

database = Database()
ai_engine = PennyAIEngine(OPENAI_API_KEY, OPENAI_MODEL)


class SearchRequest(BaseModel):
    query: str
    max_price: float = 1.00
    site: Optional[str] = None  # amazon, walmart, ebay


class ItemResponse(BaseModel):
    title: str
    price: float
    url: str
    source: str
    deal_score: Optional[float] = None


@app.get("/")
async def root():
    """Health check."""
    return {"status": "Penny AI Bot running", "version": "1.0.0"}


@app.get("/api/penny-items", response_model=List[ItemResponse])
async def get_penny_items():
    """Get all penny items found."""
    try:
        items = database.get_penny_items()
        return items
    except Exception as e:
        logger.error(f"Error retrieving penny items: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving items")


@app.get("/api/lowest-items", response_model=List[ItemResponse])
async def get_lowest_items(limit: int = 10):
    """Get lowest-priced items."""
    try:
        items = database.get_lowest_items(limit)
        return items
    except Exception as e:
        logger.error(f"Error retrieving lowest items: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving items")


@app.post("/api/search", response_model=List[ItemResponse])
async def search(request: SearchRequest):
    """Manually trigger a search."""
    logger.info(f"Manual search initiated: {request.query}")
    try:
        async with RetailScraper() as scraper:
            items = []
            if request.site in [None, "amazon"]:
                items.extend(await scraper.scrape_amazon(request.query, request.max_price))
            if request.site in [None, "walmart"]:
                items.extend(await scraper.scrape_walmart(request.query, request.max_price))
            if request.site in [None, "ebay"]:
                items.extend(await scraper.scrape_ebay(request.query, request.max_price))
        
        analyzed_items = ai_engine.analyze_items(items, request.max_price)
        database.add_items(analyzed_items)
        return analyzed_items
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail="Error performing search")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
