import requests
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)

def create_robust_session():
    """
    Creates a requests session with retry capabilities and proper configuration.
    
    Returns:
        requests.Session: Configured session with retry strategy
    """
    # Create a session with retry capabilities
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=5,  # Total number of retries
        backoff_factor=1,  # Backoff factor for sleep between retries
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods=["GET"],  # HTTP methods to retry
    )
    
    # Mount the adapter to the session
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def get_rotating_user_agents():
    """
    Returns a list of user agents to rotate through for web scraping.
    
    Returns:
        list: List of user agent strings
    """
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    ]

def get_random_user_agent():
    """
    Returns a random user agent from the list of available user agents.
    
    Returns:
        str: Random user agent string
    """
    user_agents = get_rotating_user_agents()
    return random.choice(user_agents)

def get_default_headers(referer=None):
    """
    Returns default headers for web requests with a random user agent.
    
    Args:
        referer (str, optional): The referer URL. Defaults to None.
    
    Returns:
        dict: Dictionary of HTTP headers
    """
    current_user_agent = get_random_user_agent()
    
    headers = {
        'User-Agent': current_user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    # Add referer if provided
    if referer:
        headers['Referer'] = referer
    
    return headers
