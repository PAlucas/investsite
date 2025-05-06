import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import random
import logging
from lib.utils.http_session import create_robust_session, get_default_headers, get_random_user_agent

logger = logging.getLogger(__name__)

class StocksService:
    """
    Service for handling external data operations related to stocks.
    Responsible for fetching data from external sources.
    """
    @staticmethod
    def get_stocks_from_investing(seen_codes : set) -> list:
        """
        Fetch stocks from InfoMoney API using their XML endpoint.
        Returns a list of stock dictionaries with code, name, price, and performance data.
        """
        # Create a session with retry capabilities
        session = create_robust_session()
        
        stock_data : list = []
        
        # InfoMoney API base URL
        base_url = "https://api.infomoney.com.br/ativos/top-alta-baixa-por-ativo/acao"
        
        # Total pages to fetch (from the sample response)
        total_pages = 40
        
        # Loop through pages to collect stock data
        for page in range(1, total_pages + 1):
            try:
                # Add jitter to delay to appear more human-like
                jitter = random.uniform(1.0, 3.0)
                time.sleep(jitter)
                
                # Construct URL for the current page with parameters
                url = f"{base_url}?sector=Todos&orderAtributte=Volume&pageIndex={page}&pageSize=15"
                
                # Get headers with a random user agent
                headers = get_default_headers(referer='https://www.infomoney.com.br/')
                
                logger.info(f"Fetching page {page} from InfoMoney API with user agent: {headers['User-Agent'][:30]}...")
                
                # Make the request with proper timeouts
                response = session.get(
                    url, 
                    headers=headers, 
                    timeout=(10, 30)  # (connect timeout, read timeout)
                )
                
                # Check if the request was successful
                if response.status_code != 200:
                    logger.error(f"Failed to fetch page {page}: Status code {response.status_code}")
                    continue
                
                # Parse the XML response
                try:
                    # Parse XML using ElementTree
                    root = ET.fromstring(response.content)
                    
                    # Extract namespace if present
                    ns = {'ns': 'http://schemas.datacontract.org/2004/07/InfoMoney.Framework.WebApi.Services.HighLowByAssets'}
                    
                    # Find all QuoteHighLow elements
                    quotes = root.findall('.//ns:QuoteHighLow', ns) if ns else root.findall('.//QuoteHighLow')
                    
                    if not quotes:
                        # Try without namespace if no elements found
                        quotes = root.findall('.//QuoteHighLow')
                    
                    # Process each quote
                    for quote in quotes:
                        # Extract stock information
                        try:
                            # Helper function to get text from an element with namespace handling
                            def get_element_text(parent, tag_name):
                                element = parent.find(f'ns:{tag_name}', ns) if ns else parent.find(tag_name)
                                return element.text if element is not None else None
                            
                            stock_code = get_element_text(quote, 'StockCode')
                            stock_name = get_element_text(quote, 'StockName')
                            price = get_element_text(quote, 'Value')
                            price_formatted = get_element_text(quote, 'ValueFormatted')
                            var_day = get_element_text(quote, 'ChangeDay')
                            var_day_formatted = get_element_text(quote, 'ChangeDayFormatted')
                            var_12m = get_element_text(quote, 'Change12M')
                            var_12m_formatted = get_element_text(quote, 'Change12MFormatted')
                            volume = get_element_text(quote, 'Volume')
                            volume_formatted = get_element_text(quote, 'VolumeFormatted')
                            date = get_element_text(quote, 'Date')
                            
                            # Only add if we haven't seen this code before
                            if stock_code and stock_code not in seen_codes:
                                stock_info = {
                                    'code': stock_code,
                                    'name': stock_name,
                                    'company': stock_name,
                                    'url': f"https://infomoney.com.br/{stock_code}"
                                }
                                stock_data.append(stock_info)
                                seen_codes.add(stock_code)
                                logger.debug(f"Added stock: {stock_code} - {stock_name}")
                        except Exception as e:
                            logger.error(f"Error processing stock quote: {e}")
                            continue
                    
                    # Get total pages from the response if it's the first page
                    if page == 1:
                        total_pages_elem = root.find('.//ns:TotalPages', ns) if ns else root.find('.//TotalPages')
                        if total_pages_elem is not None and total_pages_elem.text:
                            try:
                                total_pages = int(total_pages_elem.text)
                                logger.info(f"Total pages to fetch: {total_pages}")
                            except ValueError:
                                logger.warning(f"Could not parse total pages value: {total_pages_elem.text}")
                    
                    logger.info(f"Processed page {page}/{total_pages}, found {len(stock_data)} stocks so far")
                    
                except ET.ParseError as xml_error:
                    logger.error(f"XML parsing error for page {page}: {xml_error}")
                    logger.debug(f"Response content: {response.content[:200]}...")
                    continue
                
            except requests.exceptions.ConnectionError as conn_error:
                logger.error(f"Connection error for page {page}: {conn_error}")
                time.sleep(5)  # Wait longer before retrying
                continue
                
            except requests.exceptions.Timeout as timeout_error:
                logger.error(f"Timeout error for page {page}: {timeout_error}")
                time.sleep(5)  # Wait longer before retrying
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error for page {page}: {e}")
                continue
        
        logger.info(f"Completed scraping from Investing.com. Found {len(stock_data)} unique stocks.")
        return stock_data
