from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer, BigInteger
from lib.db.models.base import Base
from lib.db.models.stocks import Stocks
import datetime
from typing import Optional

class HistoricalStockData(Base):
    """
    Model representing historical stock price data.
    Stores daily price information including open, close, high, low, and volume.
    """
    __tablename__ = 'historical_stock_data'
    
    # Foreign key to the Stocks table
    stock_id: Mapped[str] = mapped_column(String, ForeignKey('stocks.id'), nullable=False, index=True)
    trading_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, index=True)
    variation: Mapped[str] = mapped_column(String(20), nullable=False)
    open_price: Mapped[str] = mapped_column(String(20), nullable=False)
    close_price: Mapped[str] = mapped_column(String(20), nullable=False)
    min_price: Mapped[str] = mapped_column(String(20), nullable=False)
    max_price: Mapped[str] = mapped_column(String(20), nullable=False)
    volume: Mapped[str] = mapped_column(String(20), nullable=False)
    
    stock = relationship("Stocks", backref="historical_data")
    
    def __repr__(self):
        return f"<HistoricalStockData {self.stock.code if self.stock else 'Unknown'}: {self.date_display} - {self.price}>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary"""
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'trading_date': self.trading_date.isoformat() if self.trading_date else None,
            'variation': self.variation,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_api_response(cls, stock_id: str, entry_data):
        """
        Create a HistoricalStockData instance from API response data
        
        Args:
            stock_id: The ID of the stock this data belongs to
            entry_data: A single entry from the API response
            
        Returns:
            HistoricalStockData: A new instance with data from the API
        """
        # Extract date information
        date_info = entry_data[0]
        date_display = date_info['display']
        date_timestamp = int(date_info['timestamp'])
        trading_date = datetime.datetime.fromtimestamp(date_timestamp)
        
        open_price = entry_data[1]
        close_price = entry_data[2]
        variation = entry_data[3]
        min_price = entry_data[4]
        max_price = entry_data[5]
        volume = entry_data[6]
        
        # Create the instance
        return cls(
            stock_id=stock_id,
            trading_date=trading_date,
            open_price=open_price,
            close_price=close_price,
            variation=variation,
            min_price=min_price,
            max_price=max_price,
            volume=volume,
        )
