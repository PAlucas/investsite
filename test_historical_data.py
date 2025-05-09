import logging
import sys
import json
from lib.services.historical_data_service import HistoricalDataService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def test_historical_data_service():
    """
    Test the HistoricalDataService by fetching historical data for BBSE3
    """
    print("Testing HistoricalDataService.get_stock_history...")
    
    # Test with BBSE3 stock
    symbol = "BBSE3"
    
    # Fetch historical data
    history_response = HistoricalDataService.get_stock_history(symbol)
    
    if history_response is None:
        print(f"❌ Failed to fetch historical data for {symbol}")
        return
    
    print(f"✅ Successfully fetched historical data for {symbol}")
    print(f"Symbol: {history_response.symbol}")
    print(f"Page: {history_response.page}")
    print(f"Items per page: {history_response.items_per_page}")
    print(f"Total entries: {history_response.total_entries}")
    
    # Display the first 3 records
    print("\nSample data (first 3 entries):")
    for i, entry in enumerate(history_response.entries[:3]):
        print(f"\nEntry {i+1}:")
        print(f"  Date: {entry.date_display} (Timestamp: {entry.date_timestamp})")
        print(f"  Date (ISO): {entry.date.isoformat()}")
        print(f"  Price: {entry.price}")
        print(f"  Previous Close: {entry.previous_close}")
        print(f"  Variation: {entry.variation}")
        print(f"  Min: {entry.min_price}")
        print(f"  Max: {entry.max_price}")
        print(f"  Volume: {entry.volume}")
    
    # Convert to dictionary and then to JSON
    response_dict = history_response.to_dict()
    
    # Print JSON representation (first 3 entries)
    response_dict['entries'] = response_dict['entries'][:3]  # Limit to first 3 for display
    print("\nJSON representation:")
    print(json.dumps(response_dict, indent=2))

if __name__ == "__main__":
    test_historical_data_service()
