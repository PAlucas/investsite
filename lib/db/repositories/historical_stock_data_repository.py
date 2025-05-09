from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from lib.db.repositories.base_repository import BaseRepository
from lib.db.models.historical_stock_data import HistoricalStockData
from sqlalchemy import func, desc, asc

class HistoricalStockDataRepository(BaseRepository[HistoricalStockData]):
    """
    Repository for HistoricalStockData model.
    Provides specific methods for handling historical stock price data.
    """
    
    def __init__(self):
        """Initialize with the HistoricalStockData model"""
        super().__init__(HistoricalStockData)
    
    def find_by_stock_id(self, stock_id: str) -> List[HistoricalStockData]:
        """
        Find all historical data for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            List of historical data entries for the stock
        """
        return self.find_by(stock_id=stock_id)
    
    def find_by_stock_id_and_date_range(self, stock_id: str, start_date: datetime, end_date: datetime) -> List[HistoricalStockData]:
        """
        Find historical data for a specific stock within a date range.
        
        Args:
            stock_id: The ID of the stock
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)
            
        Returns:
            List of historical data entries for the stock within the date range
        """
        filters = {
            "stock_id": stock_id,
            "trading_date": {"$gte": start_date, "$lte": end_date}
        }
        return self.get_all_filtered(filters)
    
    def find_latest_by_stock_id(self, stock_id: str) -> Optional[HistoricalStockData]:
        """
        Find the most recent historical data entry for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            The most recent historical data entry or None if not found
        """
        entries = self.session.query(self.model).filter(
            self.model.stock_id == stock_id,
            self.model.deleted_at.is_(None)
        ).order_by(desc(self.model.trading_date)).limit(1).all()
        
        return entries[0] if entries else None
    
    def find_oldest_by_stock_id(self, stock_id: str) -> Optional[HistoricalStockData]:
        """
        Find the oldest historical data entry for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            The oldest historical data entry or None if not found
        """
        entries = self.session.query(self.model).filter(
            self.model.stock_id == stock_id,
            self.model.deleted_at.is_(None)
        ).order_by(asc(self.model.trading_date)).limit(1).all()
        
        return entries[0] if entries else None
    
    def get_date_range_for_stock(self, stock_id: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the date range of available historical data for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            Tuple of (oldest_date, newest_date), either value may be None if no data exists
        """
        oldest = self.find_oldest_by_stock_id(stock_id)
        newest = self.find_latest_by_stock_id(stock_id)
        
        oldest_date = oldest.trading_date if oldest else None
        newest_date = newest.trading_date if newest else None
        
        return (oldest_date, newest_date)
    
    def save_entries(self, entries: List[Dict[str, Any]]) -> List[HistoricalStockData]:
        """
        Save multiple historical data entries.
        
        Args:
            entries: List of dictionaries with historical data entry fields
            
        Returns:
            List of created historical data entries
        """
        return self.create_many(entries)
    
    def find_by_date(self, date: datetime) -> List[HistoricalStockData]:
        """
        Find all historical data entries for a specific date.
        
        Args:
            date: The date to search for
            
        Returns:
            List of historical data entries for the date
        """
        # Calculate start and end of the day
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        filters = {
            "trading_date": {"$gte": start_of_day, "$lte": end_of_day}
        }
        return self.get_all_filtered(filters)
