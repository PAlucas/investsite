from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from lib.db.repositories.infomoney_news_repository import InfomoneyNewsRepository
from lib.db.models.stocks import Stocks
from lib.db.models.infomoney_news import InfomoneyNews
logger = logging.getLogger(__name__)

class InfomoneyNewsDomain:
    """
    Domain layer for Infomoney news operations.
    Handles business logic related to news articles from Infomoney.
    """
    
    def __init__(self):
        """
        Initialize the domain with repositories.
        """
        self.news_repository = InfomoneyNewsRepository()
    
    def get_all_news(self) -> List[Dict[str, Any]]:
        """
        Get all news articles.
        
        Returns:
            List of news articles as dictionaries
        """
        news_articles = self.news_repository.find_all()
        return [article.to_dict() for article in news_articles]
    
    def get_news_by_stock(self, stock: Stocks) -> List[Dict[str, Any]]:
        """
        Get all news articles for a specific stock.
        
        Args:
            stock_code: The code of the stock
            
        Returns:
            List of news articles for the stock as dictionaries
        """
        # Then, get all news for that stock
        news_articles = self.news_repository.find_by_stock_id(stock.id)
        return [article.to_dict() for article in news_articles]
    
    def get_all_news_url_without_date(self) -> set[str]:
        news_without_date = self.get_news_without_date()
        news_url = [news.url for news in news_without_date]
        news_url = set(news_url)
        return news_url
        
    
    def get_news_without_date(self) -> List[InfomoneyNews]:
        """
        Get all news articles without a published date.
        
        Returns:
            List of news articles without a published date as dictionaries
        """
        news_articles = self.news_repository.find_without_date()
        return news_articles
    
    def get_news_without_content(self) -> List[Dict[str, Any]]:
        """
        Get all news articles without content.
        
        Returns:
            List of news articles without content as dictionaries
        """
        news_articles = self.news_repository.find_without_content()
        return [article.to_dict() for article in news_articles]
    
    def save_news_urls(self, stock: Stocks, urls: List[str]) -> int:
        """
        Save multiple news URLs for a stock.
        
        Args:
            stock: The stock object
            urls: List of news URLs to save
            
        Returns:
            Number of news articles saved
        """
        # Save the news URLs
        existing_news = self.news_repository.find_by(stock_id=stock.id)
        existing_urls = set(news.url for news in existing_news)
        new_urls = [url for url in urls if url not in existing_urls]
        created_news = self.news_repository.save_news_urls(stock.id, new_urls)
        return len(created_news)
    
    def update_news_dates(self, updates: List[Dict[str, Any]]) -> int:
        """
        Update the published dates for multiple news articles.
        
        Args:
            updates: List of dictionaries with 'id' and 'published_date' keys
            
        Returns:
            Number of news articles updated
        """
        # Convert string dates to datetime objects if needed
        processed_updates = []
        for update in updates:
            if 'id' in update and 'date' in update:
                date_value = update['date']
                if isinstance(date_value, str):
                    try:
                        # Try to parse the date string
                        date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"Invalid date format for news article {update['id']}: {date_value}")
                        continue
                
                processed_updates.append({
                    'id': update['id'],
                    'published_date': date_value
                })
        
        # Update the dates
        return self.news_repository.update_dates(processed_updates)
    
    def update_news_content(self, url: str, content_data: Dict[str, Any]) -> bool:
        """
        Update the content and published_date for a news article by its URL.
        
        Args:
            url: The URL of the news article
            content_data: Dictionary containing 'content' and 'published_date' fields
            
        Returns:
            True if the news article was updated, False otherwise
        """
        try:
            # Find the news article by URL
            news_article : List[InfomoneyNews] = self.news_repository.find_by_url(url)
            
            if not news_article:
                logger.warning(f"News article with URL {url} not found")
                return False
            
            # Extract content and published_date from the content_data
            content = content_data.get('content')
            published_date = content_data.get('published_date')
            title = content_data.get('title')
            
            if not content or not published_date:
                logger.warning(f"Missing content or published_date for news article with URL {url}")
                return False
            
            # Update the news article
            for article in news_article:
                self.news_repository.update(article.id, content=content, published_date=published_date, title=title)
            logger.info(f"Updated content and published_date for news article with URL {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating content for news article with URL {url}: {e}")
            return False
    
    def get_news_by_id(self, news_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a news article by its ID.
        
        Args:
            news_id: The ID of the news article
            
        Returns:
            The news article as a dictionary or None if not found
        """
        news_article = self.news_repository.find_by_id(news_id)
        if news_article:
            return news_article.to_dict()
        return None
