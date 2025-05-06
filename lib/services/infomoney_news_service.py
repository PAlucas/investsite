from bs4 import BeautifulSoup
import time
import random
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lib.db.models.stocks import Stocks
from lib.utils.http_session import create_robust_session, get_default_headers
from bs4 import Tag
from typing import Optional, Dict, Any
logger = logging.getLogger(__name__)

class InfomoneyNewsService:
    """
    Service for fetching news from Infomoney website.
    Uses enhanced web scraping techniques to avoid detection and handle errors.
    """
    @staticmethod
    def get_url_news(stock: Stocks) -> str:
        """
        Get the URL for fetching news from Infomoney website.
        
        Args:
            stock: The stock to fetch news for
            
        Returns:
            The URL for fetching news
        """
        session = create_robust_session()
        try:
            headers = get_default_headers(referer='https://www.infomoney.com.br/')
            response = session.get(stock.url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return InfomoneyNewsService.get_news_url(soup)
        except Exception as e:
            logger.error(f"Error fetching news for stock {stock.code}: {e}")
            raise Exception(f"Error fetching news for stock {stock.code}: {e}")
            
    @staticmethod
    def get_news_url(soup: BeautifulSoup) -> Optional[str]:
        a_tags : list[Tag] = soup.find_all('a', {'class': 'href-title'})
        for tag in a_tags:
            if tag.get('href').__contains__('tudo-sobre'):
                return tag.get('href')
        return None
    
    @staticmethod
    def fetch_news_by_stock(stock: Stocks) -> list[str]:
        """
        Get the urls news from stock
        
        Args:
            stock: The stock to fetch news for
            
        Returns:
            The urls news for fetching news
        """
        session = create_robust_session()
        try:
            headers = get_default_headers(referer='https://www.infomoney.com.br/')
            response = session.get(stock.url_news, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return InfomoneyNewsService.fetch_news_by_stock_url(soup)
        except Exception as e:
            logger.error(f"Error fetching news urls for stock {stock.code}: {e}")
            raise Exception(f"Error fetching news urls for stock {stock.code}: {e}")
        
    @staticmethod
    def fetch_news_by_stock_url(soup: BeautifulSoup) -> list[str]:
        div_tags : list[Tag] = soup.find_all('div', {'data-ds-component': 'card-sm'})
        news_urls : list[str] = []
        for tag in div_tags:
            a_tag : Tag = tag.find('a')
            news_urls.append(a_tag.get('href'))
        return news_urls
    
    @staticmethod
    def fetch_news_by_url(url: str) -> Optional[dict[str, Any]]:
        session = create_robust_session()
        try:
            headers = get_default_headers(referer='https://www.infomoney.com.br/')
            response = session.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return InfomoneyNewsService._fetch_news_by_url_info(soup)
        except Exception as e:
            logger.error(f"Error fetching news for url {url}: {e}")
            raise Exception(f"Error fetching news for url {url}: {e}")
    
    @staticmethod
    def _fetch_news_by_url_info(soup: BeautifulSoup) -> Optional[dict[str, Any]]:
        try:
            article_tag : Tag = soup.find('article', {'data-ds-component': 'article'})
            title_tag : Tag = soup.find('h1')
            content : str = article_tag.get_text(strip=True)
            author_tag : Tag = soup.find('div', {'data-ds-component': 'author-small'})
            datetime_tag : Tag = author_tag.find('time')
            datetime_str : str = datetime_tag.get('datetime')
            # Convert ISO 8601 string to Python datetime object
            from datetime import datetime
            published_date = datetime.fromisoformat(datetime_str)
            return {
                'content': content,
                'published_date': published_date,
                'title': title_tag.get_text(strip=True)
            }
        except Exception as e:
            logger.error(f"Error fetching news {e}")
            raise Exception(f"Error fetching news {e}")
        

            
        