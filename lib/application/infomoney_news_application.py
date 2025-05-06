import logging
from typing import List, Dict, Any, Optional
from lib.domain.stocks_domain import StocksDomain
from lib.domain.infomoney_news_domain import InfomoneyNewsDomain
from lib.services.infomoney_news_service import InfomoneyNewsService
from lib.db.models.stocks import Stocks

logger = logging.getLogger(__name__)

class InfomoneyNewsApplication:
    """
    Application layer class for handling Infomoney news operations.
    Orchestrates between services and domain layer.
    """
    
    def __init__(self):
        """
        Initialize the application with domain dependencies.
        
        Args:
            stocks_domain: Domain layer for stocks operations
            news_domain: Domain layer for news operations
        """
        self.stocks_domain = StocksDomain()
        self.news_domain = InfomoneyNewsDomain()
        
    def save_url_news_stock(self):
        """
        Fetch and save news for all stocks from Infomoney.
        Uses the enhanced web scraping techniques to avoid detection.
        """
        logger.info("Starting to fetch and save Infomoney news for all stocks")
        
        # Get all stocks from the domain layer
        stocks = self.stocks_domain.get_all_stocks_without_news_url()
        
        if not stocks:
            logger.warning("No stocks found to fetch news for")
            return
        
        logger.info(f"Found {len(stocks)} stocks to fetch news for")
        
        for stock in stocks:
            try:
                # Since we're now working with actual Stock objects instead of dictionaries
                stock_code = stock.code
                if not stock_code:
                    logger.warning(f"Stock missing code: {stock}")
                    continue
                
                logger.info(f"Fetching news for stock {stock_code}")
                
                # Use the service layer to fetch news links
                new_link = InfomoneyNewsService.get_url_news(stock)
                
                if not new_link:
                    logger.info(f"No news found for stock {stock_code}")
                    continue
                
                logger.info(f"Found {new_link} news links for stock {stock_code}")
                
                # Save the news URLs to the domain layer - now passing the stock object directly
                self.stocks_domain.save_news_urls(stock, new_link)
                
                logger.info(f"Successfully saved news for stock {stock_code}")
                
            except Exception as e:
                logger.error(f"Error processing news for stock {stock}: {e}")
                continue
        
        logger.info("Completed fetching and saving Infomoney news for all stocks")
    
    def save_infomoney_news(self):
        """
        Fetch and save news for all stocks from Infomoney.
        Uses the enhanced web scraping techniques to avoid detection.
        """
        logger.info("Starting to fetch and save Infomoney news for all stocks")
        
        # Get all stocks from the domain layer
        stocks = self.stocks_domain.get_all_stocks_with_news_url()
        
        if not stocks:
            logger.warning("No stocks found to fetch news for")
            return
        
        logger.info(f"Found {len(stocks)} stocks to fetch news for")
        
        for stock in stocks:
            try:
                # Since we're now working with actual Stock objects instead of dictionaries
                stock_code = stock.code
                if not stock_code:
                    logger.warning(f"Stock missing code: {stock}")
                    continue
                
                logger.info(f"Fetching news for stock {stock_code}")
                
                # Use the service layer to fetch news links
                news_links = InfomoneyNewsService.fetch_news_by_stock(stock)
                
                if not news_links:
                    logger.info(f"No news found for stock {stock_code}")
                    continue
                
                logger.info(f"Found {len(news_links)} news links for stock {stock_code}")
                
                # Save the news URLs to the domain layer - now passing the stock object directly
                self.news_domain.save_news_urls(stock, news_links)
                
                logger.info(f"Successfully saved news for stock {stock_code}")
                
            except Exception as e:
                logger.error(f"Error processing news for stock {stock}: {e}")
                continue
        
        logger.info("Completed fetching and saving Infomoney news for all stocks")
    
    def get_news_by_id(self, news_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a news article by its ID.
        
        Args:
            news_id: The ID of the news article
            
        Returns:
            The news article as a dictionary or None if not found
        """
        logger.info(f"Getting news article with ID {news_id}")
        return self.news_domain.get_news_by_id(news_id)
    
    def get_news_by_stock_code(self, stock_code: str) -> Dict[str, Any]:
        """
        Get all news articles for a specific stock by its code.
        
        Args:
            stock_code: The code of the stock
            
        Returns:
            Dictionary with stock information and list of news articles
        """
        logger.info(f"Getting news for stock with code {stock_code}")
        
        # Get the stock by code
        stock = self.stocks_domain.get_stock_by_code(stock_code)
        if not stock:
            logger.warning(f"Stock with code {stock_code} not found")
            return {
                'success': False,
                'message': f'Stock with code {stock_code} not found'
            }
        
        # Get news for the stock
        news_list = self.news_domain.get_news_by_stock(stock)
        
        return {
            'success': True,
            'stock_code': stock_code,
            'stock_name': stock.name,
            'stock_company': stock.company,
            'news_count': len(news_list),
            'news': news_list
        }
    
    def get_all_news(self) -> List[Dict[str, Any]]:
        """
        Get all news articles.
        
        Returns:
            List of all news articles as dictionaries
        """
        logger.info("Getting all news articles")
        return self.news_domain.get_all_news()
    
    def update_news_dates(self, batch_size=10):
        """
        Update the dates for news articles that don't have dates yet.
        Processes in batches to avoid overwhelming the server.
        
        Args:
            batch_size (int): Number of news articles to process in each batch
        """
        logger.info("Starting to update dates for news articles")
        
        # Get news articles without dates
        news_without_dates = self.news_domain.get_news_without_date()
        
        if not news_without_dates:
            logger.info("No news articles found without dates")
            return
        
        logger.info(f"Found {len(news_without_dates)} news articles without dates")
        
        # Process in batches
        for i in range(0, len(news_without_dates), batch_size):
            batch = news_without_dates[i:i+batch_size]
            updated_news = []
            
            for news in batch:
                try:
                    url = news.get('url')
                    if not url:
                        logger.warning(f"News missing URL: {news}")
                        continue
                    
                    logger.info(f"Fetching date for news article at {url}")
                    
                    # Use the service layer to fetch the date
                    date = InfomoneyNewsService.get_news_date(url)
                    
                    if date:
                        updated_news.append({
                            'id': news.get('id'),
                            'url': url,
                            'date': date
                        })
                        logger.info(f"Found date {date} for news article at {url}")
                    else:
                        logger.warning(f"Could not find date for news article at {url}")
                    
                except Exception as e:
                    logger.error(f"Error fetching date for news article at {news.get('url')}: {e}")
                    continue
            
            # Update the dates in the domain layer
            if updated_news:
                self.news_domain.update_news_dates(updated_news)
                logger.info(f"Updated dates for {len(updated_news)} news articles")
        
        logger.info("Completed updating dates for news articles")

    def update_news_content(self):
        logger.info("Starting to update content for news articles")
        news_url = self.news_domain.get_all_news_url_without_date()
        for url in news_url:
            try:
                logger.info(f"Fetching content for news article at {url}")
                # Use the service layer to fetch the content
                content = InfomoneyNewsService.fetch_news_by_url(url)
                if content:
                    logger.info(f"Found content for news article at {url}")
                    # Use the domain layer to update the content
                    self.news_domain.update_news_content(url, content)
                else:
                    logger.warning(f"Could not find content for news article at {url}")
            except Exception as e:
                logger.error(f"Error fetching content for news article at {url}: {e}")
                continue