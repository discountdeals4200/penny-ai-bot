"""Database models and operations."""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from loguru import logger

Base = declarative_base()


class Item(Base):
    """Model for retail items found by bot."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)  # Amazon, Walmart, eBay, etc.
    deal_score = Column(Float, default=0)
    is_penny = Column(Boolean, default=False)
    is_legitimate = Column(Boolean, default=True)
    notified = Column(Boolean, default=False)
    scraped_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)


class SearchLog(Base):
    """Log of bot searches."""
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    items_found = Column(Integer, default=0)
    penny_items = Column(Integer, default=0)
    executed_at = Column(DateTime, default=datetime.now)


class Database:
    """Database manager."""

    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def add_items(self, items: list):
        """Add items to database."""
        session = self.SessionLocal()
        try:
            for item_data in items:
                existing = session.query(Item).filter_by(
                    url=item_data.get("url"),
                    source=item_data.get("source")
                ).first()
                if not existing:
                    item = Item(
                        title=item_data.get("title"),
                        price=item_data.get("price"),
                        url=item_data.get("url"),
                        source=item_data.get("source"),
                        deal_score=item_data.get("deal_score", 0),
                        is_penny=item_data.get("price", 999) <= 0.01,
                        is_legitimate=item_data.get("is_legitimate", True)
                    )
                    session.add(item)
            session.commit()
            logger.info(f"Added {len(items)} items to database")
        except Exception as e:
            logger.error(f"Error adding items to database: {e}")
            session.rollback()
        finally:
            session.close()

    def get_penny_items(self) -> list:
        """Retrieve all penny items."""
        session = self.SessionLocal()
        try:
            items = session.query(Item).filter(Item.is_penny == True).all()
            return [{
                "title": item.title,
                "price": item.price,
                "url": item.url,
                "source": item.source
            } for item in items]
        finally:
            session.close()

    def get_lowest_items(self, limit: int = 10) -> list:
        """Retrieve lowest-priced items."""
        session = self.SessionLocal()
        try:
            items = session.query(Item).order_by(Item.price).limit(limit).all()
            return [{
                "title": item.title,
                "price": item.price,
                "url": item.url,
                "source": item.source
            } for item in items]
        finally:
            session.close()
