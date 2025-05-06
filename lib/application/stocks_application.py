from lib.services.stocks_service import StocksService
from lib.domain.stocks_domain import StocksDomain
from typing import List, Optional
from lib.db.models.stocks import Stocks
import logging

logger = logging.getLogger(__name__)

class StocksApplication:
    """
    Application layer for stocks functionality.
    This layer orchestrates the flow between services and domain.
    Uses the repository pattern through the domain layer.
    """
    
    def __init__(self):
        """
        Initialize the application with its dependencies.
        """
        self.stocks_service = StocksService()
        self.stocks_domain = StocksDomain()
    
    def fetch_and_save_stocks(self) -> int:
        """
        Fetch stocks from Genial Investimentos and save them to the database.
        Orchestrates the process between the service and domain layers.
        
        Returns:
            int: Number of new stocks added to the database
        """
        logger.info("Starting to fetch stocks from InfoMoney...")
        # Use the service layer to fetch stock data from external source
        stock_data = [stock.code for stock in self.stocks_domain.get_all_stocks()]
        seen_codes = set(stock_data)
        stocks = self.stocks_service.get_stocks_from_investing(seen_codes)
        logger.info(f"Successfully fetched {len(stocks)} stocks from InfoMoney")
        
        # Use the domain layer to save the stocks to the database
        new_stocks = self.stocks_domain.save_stocks(stocks)
        logger.info(f"Added {len(new_stocks)} new stocks to the database from InfoMoney")
        
        return len(new_stocks)
    
    def get_all_stocks(self) -> List[Stocks]:
        """
        Get all active stocks from the database.
        
        Returns:
            List of all active Stock objects
        """
        return self.stocks_domain.get_all_stocks()
    
    def get_stock_by_code(self, code: str) -> Optional[Stocks]:
        """
        Get a stock by its code.
        
        Args:
            code: The stock code to search for
            
        Returns:
            The found Stock object or None if not found
        """
        return self.stocks_domain.get_stock_by_code(code)
    
    def get_stock_by_id(self, stock_id: str) -> Optional[Stocks]:
        """
        Get a stock by its ID.
        
        Args:
            stock_id: The stock ID to search for
            
        Returns:
            The found Stock object or None if not found
        """
        return self.stocks_domain.get_stock_by_id(stock_id)
    
    def search_stocks_by_name(self, name_fragment: str) -> List[Stocks]:
        """
        Search for stocks where the name contains the given fragment.
        
        Args:
            name_fragment: The fragment to search for in stock names
            
        Returns:
            List of matching stocks
        """
        return self.stocks_domain.search_stocks_by_name(name_fragment)
    
    def delete_stock(self, stock_id: str) -> bool:
        """
        Soft delete a stock.
        
        Args:
            stock_id: The ID of the stock to delete
            
        Returns:
            True if the stock was deleted, False otherwise
        """
        return self.stocks_domain.soft_delete_stock(stock_id)
