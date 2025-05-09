from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from lib.db.repositories.historical_stock_data_repository import HistoricalStockDataRepository
from lib.db.repositories.stocks_repository import StocksRepository
from lib.db.models.stocks import Stocks
from lib.db.models.historical_stock_data import HistoricalStockData
from lib.services.historical_data_service import HistoricalDataService, StockHistoryResponse

logger = logging.getLogger(__name__)

class HistoricalStockDataDomain:
    """
    Domain layer for historical stock data operations.
    Handles business logic related to historical stock price data.
    """
    
    def __init__(self):
        """
        Initialize the domain with repositories.
        """
        self.historical_repository = HistoricalStockDataRepository()
        self.stocks_repository = StocksRepository()
        self.historical_service = HistoricalDataService()
    
    def get_stock_history(self, stock_id: str) -> List[Dict[str, Any]]:
        """
        Get all historical data for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            List of historical data entries as dictionaries
        """
        history_entries = self.historical_repository.find_by_stock_id(stock_id)
        return [entry.to_dict() for entry in history_entries]
    
    def get_stock_history_by_code(self, stock_code: str) -> List[Dict[str, Any]]:
        """
        Get all historical data for a stock by its code.
        
        Args:
            stock_code: The code of the stock (e.g., 'BBSE3')
            
        Returns:
            List of historical data entries as dictionaries
        """
        stock = self.stocks_repository.find_by_code(stock_code)
        if not stock:
            logger.warning(f"Stock with code {stock_code} not found")
            return []
        
        return self.get_stock_history(stock.id)
    
    def get_stock_history_by_date_range(self, stock_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific stock within a date range.
        
        Args:
            stock_id: The ID of the stock
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)
            
        Returns:
            List of historical data entries as dictionaries
        """
        history_entries = self.historical_repository.find_by_stock_id_and_date_range(
            stock_id, start_date, end_date
        )
        return [entry.to_dict() for entry in history_entries]
    
    def get_latest_stock_price(self, stock_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent historical data entry for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            The most recent historical data entry as a dictionary or None if not found
        """
        latest_entry = self.historical_repository.find_latest_by_stock_id(stock_id)
        return latest_entry.to_dict() if latest_entry else None
    
    def get_latest_stock_price_by_code(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent historical data entry for a stock by its code.
        
        Args:
            stock_code: The code of the stock (e.g., 'BBSE3')
            
        Returns:
            The most recent historical data entry as a dictionary or None if not found
        """
        stock = self.stocks_repository.find_by_code(stock_code)
        if not stock:
            logger.warning(f"Stock with code {stock_code} not found")
            return None
        
        return self.get_latest_stock_price(stock.id)
    
    def get_date_range_for_stock(self, stock_id: str) -> Dict[str, Any]:
        """
        Get the date range of available historical data for a specific stock.
        
        Args:
            stock_id: The ID of the stock
            
        Returns:
            Dictionary with 'oldest_date' and 'newest_date' fields
        """
        oldest_date, newest_date = self.historical_repository.get_date_range_for_stock(stock_id)
        
        return {
            'oldest_date': oldest_date.isoformat() if oldest_date else None,
            'newest_date': newest_date.isoformat() if newest_date else None,
            'has_data': oldest_date is not None and newest_date is not None
        }
    
    def fetch_and_save_historical_data(self, stock: Stocks, pages: int = 1) -> Dict[str, Any]:
        """
        Fetch historical data from the API and save it to the database.
        Ensures no duplicate entries for the same stock and date are saved.
        
        Args:
            stock_code: The code of the stock (e.g., 'BBSE3')
            pages: Number of pages to fetch (each page contains 50 items)
            
        Returns:
            Dictionary with results summary
        """
        
        # Get existing entries to avoid duplicates
        existing_entries = self.historical_repository.find_by_stock_id(stock.id)
        existing_dates = {entry.trading_date.date() for entry in existing_entries}
        
        logger.info(f"Found {len(existing_dates)} existing dates for stock {stock.code}")
        
        total_entries_saved = 0
        total_duplicates_skipped = 0
        errors = []
        
        # Fetch data for each page
        for page in range(pages):
            try:
                # Fetch data from the API
                history_response = self.historical_service.get_stock_history(stock.code, page=page)
                
                if not history_response:
                    errors.append(f"Failed to fetch page {page}")
                    continue
                
                # Convert API response to database entries
                entries_to_save = []
                duplicates_in_page = 0
                
                for entry in history_response.entries:
                    # Create a dictionary with the entry data
                    entry_data = [
                        {'display': entry.date_display, 'timestamp': entry.date_timestamp},
                        entry.price,
                        entry.previous_close,
                        entry.variation,
                        entry.min_price,
                        entry.max_price,
                        entry.volume
                    ]
                    
                    # Create a HistoricalStockData instance from the API response
                    historical_entry = HistoricalStockData.from_api_response(stock.id, entry_data)
                    
                    # Check if this date already exists for this stock
                    entry_date = historical_entry.trading_date.date()
                    if entry_date in existing_dates:
                        duplicates_in_page += 1
                        continue  # Skip this entry
                    
                    # Add this date to our set of existing dates to prevent duplicates within the same batch
                    existing_dates.add(entry_date)
                    
                    # Convert to dictionary for bulk save
                    entries_to_save.append({
                        'stock_id': historical_entry.stock_id,
                        'trading_date': historical_entry.trading_date,
                        'variation': historical_entry.variation,
                        'open_price': historical_entry.open_price,
                        'close_price': historical_entry.close_price,
                        'min_price': historical_entry.min_price,
                        'max_price': historical_entry.max_price,
                        'volume': historical_entry.volume
                    })
                
                logger.info(f"Page {page}: Found {len(history_response.entries)} entries, "
                           f"skipped {duplicates_in_page} duplicates, saving {len(entries_to_save)} entries")
                total_duplicates_skipped += duplicates_in_page
                
                # Save entries to the database
                if entries_to_save:
                    saved_entries = self.historical_repository.save_entries(entries_to_save)
                    total_entries_saved += len(saved_entries)
                
            except Exception as e:
                logger.error(f"Error fetching or saving historical data for {stock.code} (page {page}): {e}")
                errors.append(f"Error on page {page}: {str(e)}")
        
        return {
            'success': total_entries_saved > 0 or total_duplicates_skipped > 0,
            'stock_code': stock.code,
            'stock_id': stock.id,
            'entries_saved': total_entries_saved,
            'duplicates_skipped': total_duplicates_skipped,
            'pages_fetched': pages,
            'errors': errors if errors else None
        }
    
    def get_price_variation(self, stock_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Calculate price variation for a stock over a specified number of days.
        
        Args:
            stock_id: The ID of the stock
            days: Number of days to look back
            
        Returns:
            Dictionary with variation information
        """
        # Get the latest price
        latest_entry = self.historical_repository.find_latest_by_stock_id(stock_id)
        if not latest_entry:
            return {
                'success': False,
                'error': 'No historical data available for this stock'
            }
        
        # Calculate the start date
        end_date = latest_entry.trading_date
        start_date = end_date - timedelta(days=days)
        
        # Get the earliest price within the date range
        history_entries = self.historical_repository.find_by_stock_id_and_date_range(
            stock_id, start_date, end_date
        )
        
        if not history_entries:
            return {
                'success': False,
                'error': f'No historical data available for the last {days} days'
            }
        
        # Sort by date
        sorted_entries = sorted(history_entries, key=lambda x: x.trading_date)
        earliest_entry = sorted_entries[0]
        
        # Calculate variation
        try:
            latest_price_numeric = float(latest_entry.variation.replace(',', '.'))
            earliest_price_numeric = float(earliest_entry.variation.replace(',', '.'))
            
            absolute_variation = latest_price_numeric - earliest_price_numeric
            percentage_variation = (absolute_variation / earliest_price_numeric) * 100 if earliest_price_numeric != 0 else 0
            
            return {
                'success': True,
                'stock_id': stock_id,
                'days': days,
                'start_date': earliest_entry.trading_date.isoformat(),
                'end_date': latest_entry.trading_date.isoformat(),
                'start_price': earliest_entry.variation,
                'end_price': latest_entry.variation,
                'absolute_variation': round(absolute_variation, 2),
                'percentage_variation': round(percentage_variation, 2)
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating price variation: {e}")
            return {
                'success': False,
                'error': f'Error calculating price variation: {str(e)}'
            }
