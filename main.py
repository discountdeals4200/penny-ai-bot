"""Main bot runner."""
import asyncio
from loguru import logger
from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MAX_PRICE_THRESHOLD,
    SEARCH_INTERVAL_MINUTES,
    DEBUG_MODE,
    LOG_LEVEL
)
from bot.scraper import RetailScraper
from bot.ai_engine import PennyAIEngine
from bot.database import Database
from bot.notifier import DealNotifier

# Configure logging
logger.add("logs/penny_bot.log", rotation="500 MB", level=LOG_LEVEL)


class PennyAIBot:
    """Main bot orchestrator."""

    def __init__(self):
        self.ai_engine = PennyAIEngine(OPENAI_API_KEY, OPENAI_MODEL)
        self.database = Database()
        self.notifier = DealNotifier("your_email@example.com", "smtp.gmail.com", 587)
        self.search_queries = [
            "penny item",
            "clearance sale under $1",
            "lowest price electronics"
        ]

    async def run(self):
        """Run the bot continuously."""
        logger.info("🤖 Penny AI Bot started")
        logger.info(f"Max price threshold: ${MAX_PRICE_THRESHOLD}")
        logger.info(f"Search interval: {SEARCH_INTERVAL_MINUTES} minutes")

        while True:
            try:
                await self.search_and_analyze()
                logger.info(f"Next search in {SEARCH_INTERVAL_MINUTES} minutes...")
                await asyncio.sleep(SEARCH_INTERVAL_MINUTES * 60)
            except Exception as e:
                logger.error(f"Error in bot loop: {e}")
                await asyncio.sleep(60)

    async def search_and_analyze(self):
        """Search websites and analyze results."""
        all_items = []

        async with RetailScraper() as scraper:
            for query in self.search_queries:
                logger.info(f"Searching for: {query}")
                
                # Search multiple sites
                amazon_items = await scraper.scrape_amazon(query, MAX_PRICE_THRESHOLD)
                walmart_items = await scraper.scrape_walmart(query, MAX_PRICE_THRESHOLD)
                ebay_items = await scraper.scrape_ebay(query, MAX_PRICE_THRESHOLD)
                
                items = amazon_items + walmart_items + ebay_items
                all_items.extend(items)

        if all_items:
            # Analyze with AI
            analyzed_items = self.ai_engine.analyze_items(all_items, MAX_PRICE_THRESHOLD)
            
            # Save to database
            self.database.add_items(analyzed_items)
            
            # Check for penny items
            penny_items = self.ai_engine.identify_penny_items(analyzed_items)
            if penny_items:
                logger.info(f"🎉 Found {len(penny_items)} penny items!")
                self.notifier.notify_penny_items(penny_items)
            
            # Get lowest-priced items
            lowest_items = self.ai_engine.find_lowest_prices(all_items, top_n=5)
            if lowest_items:
                self.notifier.notify_lowest_deals(lowest_items)
        else:
            logger.warning("No items found in this search cycle")


async def main():
    """Main entry point."""
    bot = PennyAIBot()
    await bot.run()


if __name__ == "__main__":
    if DEBUG_MODE:
        logger.info("Running in DEBUG mode")
    asyncio.run(main())
