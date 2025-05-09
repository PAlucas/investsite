from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from lib.domain.historical_stock_data_domain import HistoricalStockDataDomain
from lib.domain.stocks_domain import StocksDomain

logger = logging.getLogger(__name__)

class HistoricalStockDataApplication:
    """
    Application layer for historical stock data operations.
    Acts as a facade between the API routes and the domain layer.
    """
    
    def __init__(self):
        """Initialize with domain instances"""
        self.historical_domain = HistoricalStockDataDomain()
        self.stocks_domain = StocksDomain()
    
    def get_stock_history(self, stock_id: str) -> List[Dict[str, Any]]:
        """
        Get all historical data for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            List of historical data entries as dictionaries
        """
        return self.historical_domain.get_stock_history(stock_id)
    
    def get_stock_history_by_code(self, stock_code: str) -> Dict[str, Any]:
        """
        Get all historical data for a stock by its code.
        
        Args:
            stock_code: The code of the stock (e.g., 'BBSE3')
            
        Returns:
            Dictionary with success status and historical data entries
        """
        stock = self.stocks_domain.get_stock_by_code(stock_code)
        if not stock:
            return {
                'success': False,
                'message': f'Stock with code {stock_code} not found'
            }
        
        history = self.historical_domain.get_stock_history(stock.id)
        return {
            'success': True,
            'stock': stock.to_dict(),
            'history': history
        }
    
    def get_stock_history_by_date_range(self, stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get historical data for a specific stock within a date range.
        
        Args:
            stock_code: The code of the stock
            start_date: The start date in ISO format (YYYY-MM-DD)
            end_date: The end date in ISO format (YYYY-MM-DD)
            
        Returns:
            Dictionary with success status and historical data entries
        """
        stock = self.stocks_domain.get_stock_by_code(stock_code)
        if not stock:
            return {
                'success': False,
                'message': f'Stock with code {stock_code} not found'
            }
        
        try:
            # Parse dates
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            
            # Ensure end date includes the entire day
            end = end.replace(hour=23, minute=59, second=59)
            
            history = self.historical_domain.get_stock_history_by_date_range(stock.id, start, end)
            return {
                'success': True,
                'stock': stock.to_dict(),
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'history': history,
                'count': len(history)
            }
        except ValueError as e:
            return {
                'success': False,
                'message': f'Invalid date format: {str(e)}'
            }
    
    def get_latest_stock_price(self, stock_code: str) -> Dict[str, Any]:
        """
        Get the most recent historical data entry for a stock by its code.
        
        Args:
            stock_code: The code of the stock (e.g., 'BBSE3')
            
        Returns:
            Dictionary with success status and the latest price data
        """
        stock = self.stocks_domain.get_stock_by_code(stock_code)
        if not stock:
            return {
                'success': False,
                'message': f'Stock with code {stock_code} not found'
            }
        
        latest_price = self.historical_domain.get_latest_stock_price(stock.id)
        if not latest_price:
            return {
                'success': False,
                'message': f'No historical data found for stock {stock_code}'
            }
        
        return {
            'success': True,
            'stock': stock.to_dict(),
            'latest_price': latest_price
        }
    
    def fetch_and_save_historical_data(self, pages: int = 1) -> Dict[str, Any]:
        """
        Fetch historical data from the API and save it to the database.
        
        Args:

            pages: Number of pages to fetch (each page contains 50 items)
            
        Returns:
            Dictionary with results summary
        """
        stocks = self.stocks_domain.get_all_stocks_with_news_url()
        if not stocks:
            return {
                'success': False,
                'message': 'No stocks found'
            }
        for stock in stocks:
            result = self.historical_domain.fetch_and_save_historical_data(stock, pages)
        return result
    
    def get_price_variation(self, stock_code: str, days: int = 30) -> Dict[str, Any]:
        """
        Calculate price variation for a stock over a specified number of days.
        
        Args:
            stock_code: The code of the stock
            days: Number of days to look back
            
        Returns:
            Dictionary with variation information
        """
        stock = self.stocks_domain.get_stock_by_code(stock_code)
        if not stock:
            return {
                'success': False,
                'message': f'Stock with code {stock_code} not found'
            }
        
        variation = self.historical_domain.get_price_variation(stock.id, days)
        if variation.get('success', False):
            variation['stock'] = stock.to_dict()
        
        return variation
    
    def get_available_date_range(self, stock_code: str) -> Dict[str, Any]:
        """
        Get the date range of available historical data for a stock.
        
        Args:
            stock_code: The code of the stock
            
        Returns:
            Dictionary with date range information
        """
        stock = self.stocks_domain.get_stock_by_code(stock_code)
        if not stock:
            return {
                'success': False,
                'message': f'Stock with code {stock_code} not found'
            }
        
        date_range = self.historical_domain.get_date_range_for_stock(stock.id)
        return {
            'success': True,
            'stock': stock.to_dict(),
            'date_range': date_range
        }
