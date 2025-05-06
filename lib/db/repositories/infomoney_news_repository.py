from typing import List, Optional, Dict, Any
from datetime import datetime
from lib.db.repositories.base_repository import BaseRepository
from lib.db.models.infomoney_news import InfomoneyNews

class InfomoneyNewsRepository(BaseRepository[InfomoneyNews]):
    """
    Repository for InfomoneyNews model.
    Provides specific methods for handling news articles from Infomoney.
    """
    
    def __init__(self):
        """Initialize with the InfomoneyNews model"""
        super().__init__(InfomoneyNews)
    
    def find_by_url(self, url: str) -> List[InfomoneyNews]:
        """
        Find a news article by its URL.
        
        Args:
            url: The URL of the news article
            
        Returns:
            The found news article or None if not found
        """
        return self.find_by(url=url)
    
    def find_by_stock_id(self, stock_id: str) -> List[InfomoneyNews]:
        """
        Find all news articles for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            List of news articles for the stock
        """
        return self.find_by(stock_id=stock_id)
    
    def find_without_date(self) -> List[InfomoneyNews]:
        """
        Find all news articles without a published date.
        
        Returns:
            List of news articles without a published date
        """
        # Use the get_all_filtered method with a custom filter
        filters = {
            "published_date": None
        }
        return self.get_all_filtered(filters)
    
    def find_without_content(self) -> List[InfomoneyNews]:
        """
        Find all news articles without content.
        
        Returns:
            List of news articles without content
        """
        # Use the get_all_filtered method with a custom filter
        filters = {
            "content": None
        }
        return self.get_all_filtered(filters)
    
    def update_dates(self, updates: List[Dict[str, Any]]) -> int:
        """
        Update the published dates for multiple news articles.
        
        Args:
            updates: List of dictionaries with 'id' and 'published_date' keys
            
        Returns:
            Number of news articles updated
        """
        count = 0
        for update in updates:
            if 'id' in update and 'published_date' in update:
                try:
                    self.update(update['id'], published_date=update['published_date'])
                    count += 1
                except Exception as e:
                    # Log error but continue with other updates
                    print(f"Error updating news article {update['id']}: {e}")
        return count
    
    def save_news_urls(self, stock_id: str, urls: List[str]) -> List[InfomoneyNews]:
        """
        Save multiple news URLs for a stock.
        Skip URLs that already exist.
        
        Args:
            stock_id: The ID of the stock
            urls: List of news URLs to save
            
        Returns:
            List of created news articles
        """
        # Filter out URLs that already exist
        existing_urls = set(item.url for item in self.find_by(stock_id=stock_id))
        new_urls = [url for url in urls if url not in existing_urls]
        
        # Create news items for new URLs
        news_items = []
        for url in new_urls:
            news_items.append({
                'url': url,
                'stock_id': stock_id
            })
        
        # Create the news items
        if news_items:
            return self.create_many(news_items)
        return []
