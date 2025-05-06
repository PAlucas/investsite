from flask import Blueprint, jsonify, request, views
from lib.application.infomoney_news_application import InfomoneyNewsApplication
from typing import List, Dict, Any, Optional
from flasgger import swag_from
import logging

# Create blueprint
infomoney_news_bp = Blueprint('infomoney_news', __name__)
logger = logging.getLogger(__name__)

class InfomoneyNewsView(views.MethodView):
    """Class-based view for handling InfoMoney news operations"""
    
    def __init__(self):
        self.news_application = InfomoneyNewsApplication()
    
    def get(self, news_id=None):
        """
        Get InfoMoney news endpoint
        ---
        tags:
          - news
        parameters:
          - name: news_id
            in: path
            type: string
            required: false
            description: News ID to retrieve a specific article
          - name: stock_code
            in: query
            type: string
            required: false
            description: Stock code to retrieve news for a specific stock
        responses:
          200:
            description: List of news articles or a single news article
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                news_count:
                  type: integer
                  example: 25
                news:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                        example: 123e4567-e89b-12d3-a456-426614174000
                      title:
                        type: string
                        example: Petrobras anuncia novos investimentos
                      url:
                        type: string
                        example: https://www.infomoney.com.br/mercados/petrobras-anuncia-novos-investimentos/
                      date:
                        type: string
                        format: date-time
                      stock_code:
                        type: string
                        example: PETR4
                      created_at:
                        type: string
                        format: date-time
                      updated_at:
                        type: string
                        format: date-time
          404:
            description: News not found
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: News with ID XXX not found
        """
        stock_code = request.args.get('stock_code')
        
        if news_id:
            # Get specific news by ID using the application layer
            news = self.news_application.get_news_by_id(news_id)
            if news is None:
                return jsonify({
                    'success': False,
                    'message': f'News with ID {news_id} not found'
                }), 404
            
            return jsonify({
                'success': True,
                'news': news
            })
        elif stock_code:
            # Get news for a specific stock using the application layer
            result = self.news_application.get_news_by_stock_code(stock_code)
            
            # Check if the operation was successful
            if not result.get('success', False):
                return jsonify(result), 404
            
            return jsonify(result)
        else:
            # Get all news using the application layer
            news_list = self.news_application.get_all_news()
            return jsonify({
                'success': True,
                'news_count': len(news_list),
                'news': news_list
            })


class InfomoneyNewsFetchView(views.MethodView):
    """Class-based view for fetching news from InfoMoney"""
    
    def __init__(self):
        self.news_application = InfomoneyNewsApplication()
    
    def post(self):
        """
        Fetch news from InfoMoney and save to database
        ---
        tags:
          - news
        summary: Fetch news from InfoMoney
        description: Scrapes news from InfoMoney website and saves them to the database
        responses:
          200:
            description: News fetched and saved successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Successfully fetched and saved news from InfoMoney
          500:
            description: Error fetching news
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Error fetching news: Connection error"
        """
        try:
            logger.info("Starting to fetch news from InfoMoney")
            self.news_application.save_infomoney_news()
            return jsonify({
                'success': True,
                'message': 'Successfully fetched and saved news from InfoMoney'
            })
        except Exception as e:
            logger.error(f"Error fetching news from InfoMoney: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error fetching news: {str(e)}'
            }), 500


class InfomoneyNewsUrlStockView(views.MethodView):
    """Class-based view for saving news URLs for stocks"""
    
    def __init__(self):
        self.news_application = InfomoneyNewsApplication()
    
    def get(self):
        """
        Save news URLs for all stocks
        ---
        tags:
          - news
          - stocks
        summary: Save news URLs for stocks
        description: Fetches and saves news URLs for all stocks in the database
        responses:
          200:
            description: News URLs saved successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Successfully saved news URLs for stocks
          500:
            description: Error saving news URLs
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Error saving news URLs: Connection error"
        """
        try:
            logger.info("Starting to save news URLs for stocks")
            self.news_application.save_url_news_stock()
            return jsonify({
                'success': True,
                'message': 'Successfully saved news URLs for stocks'
            })
        except Exception as e:
            logger.error(f"Error saving news URLs for stocks: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error saving news URLs for stocks: {str(e)}'
            }), 500


class InfomoneyNewsUpdateContentView(views.MethodView):
    """Class-based view for updating news content and published dates"""
    
    def __init__(self):
        self.news_application = InfomoneyNewsApplication()
    
    def post(self):
        """
        Update content and published dates for news articles
        ---
        tags:
          - news
        summary: Update news content and dates
        description: Fetches and updates content and published dates for news articles that don't have this information
        responses:
          200:
            description: News content updated successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Successfully updated news content and dates
          500:
            description: Error updating news content
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Error updating news content: Connection error"
        """
        try:
            logger.info("Starting to update news content and dates")
            self.news_application.update_news_content()
            return jsonify({
                'success': True,
                'message': 'Successfully updated news content and dates'
            })
        except Exception as e:
            logger.error(f"Error updating news content and dates: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error updating news content and dates: {str(e)}'
            }), 500


# Register the views with the blueprint
news_view = InfomoneyNewsView.as_view('infomoney_news_api')
news_fetch_view = InfomoneyNewsFetchView.as_view('infomoney_news_fetch_api')
news_url_stock_view = InfomoneyNewsUrlStockView.as_view('infomoney_news_url_stock_api')
news_update_content_view = InfomoneyNewsUpdateContentView.as_view('infomoney_news_update_content_api')

# Add URL rules
infomoney_news_bp.add_url_rule('/', view_func=news_view, methods=['GET'])
infomoney_news_bp.add_url_rule('/<string:news_id>', view_func=news_view, methods=['GET'])
infomoney_news_bp.add_url_rule('/fetch', view_func=news_fetch_view, methods=['POST'])
infomoney_news_bp.add_url_rule('/save-stock-urls', view_func=news_url_stock_view, methods=['GET'])
infomoney_news_bp.add_url_rule('/update-content', view_func=news_update_content_view, methods=['POST'])