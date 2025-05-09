import time
import random
import logging
import json
from typing import Optional, List, Any, Dict, NamedTuple
from dataclasses import dataclass
from datetime import datetime
from lib.utils.http_session import create_robust_session, get_default_headers

logger = logging.getLogger(__name__)

@dataclass
class StockHistoryEntry:
    """Represents a single historical stock data entry"""
    date_display: str
    date_timestamp: int
    price: str
    previous_close: str
    variation: str
    min_price: str
    max_price: str
    volume: str
    
    @property
    def date(self) -> datetime:
        """Convert timestamp to datetime object"""
        return datetime.fromtimestamp(int(self.date_timestamp))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary"""
        return {
            'date': {
                'display': self.date_display,
                'timestamp': self.date_timestamp,
                'datetime': self.date.isoformat()
            },
            'price': self.price,
            'previous_close': self.previous_close,
            'variation': self.variation,
            'min': self.min_price,
            'max': self.max_price,
            'volume': self.volume
        }

@dataclass
class StockHistoryResponse:
    """Response object for historical stock data"""
    symbol: str
    entries: List[StockHistoryEntry]
    page: int
    items_per_page: int
    total_entries: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'symbol': self.symbol,
            'page': self.page,
            'items_per_page': self.items_per_page,
            'total_entries': self.total_entries,
            'entries': [entry.to_dict() for entry in self.entries]
        }

class HistoricalDataService:
    """
    Service for fetching historical stock data from InfoMoney API.
    """
    
    @staticmethod
    def get_stock_history(symbol: str, page: int = 0, items_per_page: int = 50) -> Optional[StockHistoryResponse]:
        """
        Fetch historical stock data from InfoMoney API.
        
        Args:
            symbol (str): The stock symbol (e.g., 'BBSE3')
            page (int, optional): Page number for pagination. Defaults to 0.
            items_per_page (int, optional): Number of items per page. Defaults to 50.
            
        Returns:
            Optional[StockHistoryResponse]: Structured response object containing historical data
            Returns None if an error occurs
        """
        # Create a session with retry capabilities
        session = create_robust_session()
        headers = get_default_headers(referer=f'https://www.infomoney.com.br/cotacoes/b3/acao/{symbol.lower()}/historico/')
        
        # Add additional headers from the curl command
        headers.update({
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.infomoney.com.br',
            'priority': 'u=1, i',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest'
        })
        
        url = 'https://www.infomoney.com.br/wp-json/infomoney/v1/quotes/history'
        
        # Prepare data payload
        data = {
            'page': page,
            'numberItems': items_per_page,
            'symbol': symbol
        }
        
        try:
            logger.info(f"Fetching historical data for {symbol} (page {page})")
            
            # Add jitter to delay to appear more human-like
            jitter = random.uniform(0.5, 2.0)
            time.sleep(jitter)
            
            # Make the POST request
            response = session.post(
                url,
                headers=headers,
                data=data,
                timeout=(10, 30)  # (connect timeout, read timeout)
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Failed to fetch historical data for {symbol}: Status code {response.status_code}")
                return None
                
            # Parse the JSON response
            try:
                # The response is directly a list of lists as shown in the example
                raw_history_data = response.json()
                logger.info(f"Successfully fetched historical data for {symbol} with {len(raw_history_data)} records")
                
                # Convert raw data to structured response
                entries = []
                for entry in raw_history_data:
                    try:
                        # Extract data from the raw entry
                        date_info = entry[0]
                        price = entry[1]
                        previous_close = entry[2]
                        variation = entry[3]
                        min_price = entry[4]
                        max_price = entry[5]
                        volume = entry[6]
                        
                        # Create StockHistoryEntry object
                        history_entry = StockHistoryEntry(
                            date_display=date_info['display'],
                            date_timestamp=date_info['timestamp'],
                            price=price,
                            previous_close=previous_close,
                            variation=variation,
                            min_price=min_price,
                            max_price=max_price,
                            volume=volume
                        )
                        entries.append(history_entry)
                    except (IndexError, KeyError, TypeError) as e:
                        logger.warning(f"Error processing entry: {e}")
                        continue
                
                # Create response object
                response_obj = StockHistoryResponse(
                    symbol=symbol,
                    entries=entries,
                    page=page,
                    items_per_page=items_per_page,
                    total_entries=len(entries)
                )
                
                return response_obj
                
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing error for {symbol}: {json_error}")
                logger.debug(f"Response content: {response.content[:200]}...")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error fetching historical data for {symbol}: {e}")
            return None
