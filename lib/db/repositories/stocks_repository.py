from typing import List, Optional
from sqlalchemy import select
from lib.db.models.stocks import Stocks
from lib.db.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)

class StocksRepository(BaseRepository[Stocks]):
    """
    Repository for handling Stock model database operations.
    Extends the BaseRepository with Stock-specific operations.
    """
    
    def __init__(self):
        """Initialize the repository with the Stocks model class"""
        super().__init__(Stocks)
    
    def find_by_code(self, code: str) -> Optional[Stocks]:
        """
        Find a stock by its code.
        
        Args:
            code: The stock code to search for
            
        Returns:
            The found stock or None if not found
        """
        return self.find_one_by(code=code)
    
    def find_by_name_contains(self, name_fragment: str) -> List[Stocks]:
        """
        Find stocks where the name contains the given fragment.
        
        Args:
            name_fragment: The fragment to search for in stock names
            
        Returns:
            List of matching stocks
        """
        with self.session() as session:
            stmt = select(Stocks).where(
                Stocks.name.ilike(f'%{name_fragment}%'),
                Stocks.deleted_at.is_(None)
            )
            return session.execute(stmt).scalars().all()
    
    def bulk_create_stocks(self, stocks_data: List[dict]) -> List[Stocks]:
        """
        Create multiple stocks, skipping any that already exist with the same code.
        
        Args:
            stocks_data: List of dictionaries containing stock data with 'name', 'code', and optionally 'company' keys
            
        Returns:
            List of newly created Stock objects
        """
        new_stocks_data = []
        updated_stocks = []
        
        # Filter out stocks that already exist
        for stock_data in stocks_data:
            if 'code' not in stock_data:
                logger.warning(f"Skipping stock data without code: {stock_data}")
                continue
                
            existing_stock = self.find_by_code(stock_data['code'])
            
            if existing_stock:
                # If the stock exists and we have company data, update it
                if 'company' in stock_data and stock_data['company'] and not existing_stock.company:
                    logger.info(f"Updating company information for {stock_data['code']}")
                    with self.session() as session:
                        existing_stock.company = stock_data['company']
                        session.add(existing_stock)
                        session.commit()
                        updated_stocks.append(existing_stock)
            else:
                # This is a new stock
                new_stocks_data.append(stock_data)
        
        # Create the new stocks
        created_stocks = []
        if new_stocks_data:
            created_stocks = self.create_many(new_stocks_data)
            logger.info(f"Created {len(created_stocks)} new stocks")
        
        logger.info(f"Updated company information for {len(updated_stocks)} existing stocks")
        return created_stocks
