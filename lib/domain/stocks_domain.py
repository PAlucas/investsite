from lib.db.repositories.stocks_repository import StocksRepository
from lib.db.models.stocks import Stocks
from typing import List, Optional

class StocksDomain:
    """
    Domain layer for handling stock-related business logic.
    This layer is responsible for business rules and orchestrating repository operations.
    Uses the repository pattern for data access.
    """
    
    def __init__(self):
        """
        Initialize the domain with its repository.
        """
        self.repository = StocksRepository()
    
    def save_stocks(self, stocks: List[dict]) -> List[Stocks]:
        """
        Save a list of stocks to the database.
        Only saves stocks that don't already exist.
        
        Args:
            stocks: List of dictionaries containing stock data with 'name' and 'code' keys
            
        Returns:
            List of newly created Stock objects
        """
        return self.repository.bulk_create_stocks(stocks)
    
    def save_news_urls(self, stock: Stocks, url: str) -> Stocks:
        """
        Update a stock with a news URL.
        
        Args:
            stock: The stock object to update
            url: The news URL to save
            
        Returns:
            The updated stock object
        """
        return self.repository.update(stock.id, url_news=url)
    
    def get_all_stocks(self) -> List[Stocks]:
        """
        Get all active stocks from the database.
        
        Returns:
            List of all active Stock objects
        """
        return self.repository.find_all()
    
    def get_all_stocks_without_news_url(self) -> List[Stocks]:
        """
        Get all active stocks from the database.
        
        Returns:
            List of all active Stock objects
        """
        return self.repository.get_all_filtered({"url_news": None})
    
    def get_all_stocks_with_news_url(self) -> List[Stocks]:
        """
        Get all active stocks from the database where url_news is not None.
        
        Returns:
            List of Stock objects with url_news field populated
        """
        return self.repository.get_all_filtered({"url_news": {"$ne": None}})
    
    def get_stock_by_code(self, code: str) -> Optional[Stocks]:
        """
        Get an active stock by its code.
        
        Args:
            code: The stock code to search for
            
        Returns:
            The found Stock object or None if not found
        """
        return self.repository.find_by_code(code)
    
    def get_stock_by_id(self, stock_id: str) -> Optional[Stocks]:
        """
        Get an active stock by its ID.
        
        Args:
            stock_id: The stock UUID to search for
            
        Returns:
            The found Stock object or None if not found
        """
        return self.repository.find_by_id(stock_id)
    
    def stock_exists(self, code: str) -> bool:
        """
        Check if an active stock with the given code exists.
        
        Args:
            code: The stock code to check
            
        Returns:
            True if the stock exists, False otherwise
        """
        return self.repository.exists(code=code)
    
    def soft_delete_stock(self, stock_id: str) -> bool:
        """
        Soft delete a stock by setting its deleted_at timestamp.
        
        Args:
            stock_id: The UUID of the stock to delete
            
        Returns:
            True if the stock was deleted, False otherwise
        """
        return self.repository.soft_delete(stock_id)
    
    def search_stocks_by_name(self, name_fragment: str) -> List[Stocks]:
        """
        Search for stocks where the name contains the given fragment.
        
        Args:
            name_fragment: The fragment to search for in stock names
            
        Returns:
            List of matching stocks
        """
        return self.repository.find_by_name_contains(name_fragment)
