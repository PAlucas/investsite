from flask import Blueprint, jsonify, request, views
from lib.application.historical_stock_data_application import HistoricalStockDataApplication
from typing import List, Dict, Any, Optional
import logging

# Create blueprint
historical_data_bp = Blueprint('historical_data', __name__)
logger = logging.getLogger(__name__)

class HistoricalDataView(views.MethodView):
    """Class-based view for handling historical stock data operations"""
    
    def __init__(self):
        self.historical_application = HistoricalStockDataApplication()
    
    def get(self, stock_code=None):
        """
        Get historical data endpoint
        ---
        parameters:
          - name: stock_code
            in: path
            type: string
            required: false
            description: Stock code to retrieve historical data for
          - name: start_date
            in: query
            type: string
            required: false
            description: Start date for filtering (YYYY-MM-DD)
          - name: end_date
            in: query
            type: string
            required: false
            description: End date for filtering (YYYY-MM-DD)
        responses:
          200:
            description: Historical data for a stock
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                stock:
                  type: object
                  properties:
                    id:
                      type: string
                    code:
                      type: string
                    name:
                      type: string
                history:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      stock_id:
                        type: string
                      trading_date:
                        type: string
                        format: date-time
                      variation:
                        type: string
                      min_price:
                        type: string
                      max_price:
                        type: string
                      volume:
                        type: string
          404:
            description: Stock not found
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: Stock with code XXXX not found
        """
        if not stock_code:
            return jsonify({
                'success': False,
                'message': 'Stock code is required'
            }), 400
        
        # Check if date range parameters are provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            # Get historical data within date range
            result = self.historical_application.get_stock_history_by_date_range(
                stock_code, start_date, end_date
            )
        else:
            # Get all historical data for the stock
            result = self.historical_application.get_stock_history_by_code(stock_code)
        
        if not result.get('success', False):
            return jsonify(result), 404
        
        return jsonify(result)


class LatestPriceView(views.MethodView):
    """Class-based view for getting the latest price of a stock"""
    
    def __init__(self):
        self.historical_application = HistoricalStockDataApplication()
    
    def get(self, stock_code):
        """
        Get latest price endpoint
        ---
        parameters:
          - name: stock_code
            in: path
            type: string
            required: true
            description: Stock code to retrieve latest price for
        responses:
          200:
            description: Latest price data for a stock
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                stock:
                  type: object
                  properties:
                    id:
                      type: string
                    code:
                      type: string
                    name:
                      type: string
                latest_price:
                  type: object
                  properties:
                    id:
                      type: string
                    stock_id:
                      type: string
                    trading_date:
                      type: string
                      format: date-time
                    variation:
                      type: string
                    min_price:
                      type: string
                    max_price:
                      type: string
                    volume:
                      type: string
          404:
            description: Stock not found or no price data available
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: No historical data found for stock XXXX
        """
        result = self.historical_application.get_latest_stock_price(stock_code)
        
        if not result.get('success', False):
            return jsonify(result), 404
        
        return jsonify(result)


class PriceVariationView(views.MethodView):
    """Class-based view for calculating price variation"""
    
    def __init__(self):
        self.historical_application = HistoricalStockDataApplication()
    
    def get(self, stock_code):
        """
        Get price variation endpoint
        ---
        parameters:
          - name: stock_code
            in: path
            type: string
            required: true
            description: Stock code to calculate price variation for
          - name: days
            in: query
            type: integer
            required: false
            description: Number of days to look back (default 30)
        responses:
          200:
            description: Price variation data for a stock
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                stock:
                  type: object
                  properties:
                    id:
                      type: string
                    code:
                      type: string
                    name:
                      type: string
                days:
                  type: integer
                  example: 30
                start_date:
                  type: string
                  format: date-time
                end_date:
                  type: string
                  format: date-time
                start_price:
                  type: string
                end_price:
                  type: string
                absolute_variation:
                  type: number
                  format: float
                percentage_variation:
                  type: number
                  format: float
          404:
            description: Stock not found or no price data available
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: No historical data available for this stock
        """
        days = request.args.get('days', default=30, type=int)
        result = self.historical_application.get_price_variation(stock_code, days)
        
        if not result.get('success', False):
            return jsonify(result), 404
        
        return jsonify(result)


class FetchHistoricalDataView(views.MethodView):
    """Class-based view for fetching historical data from external sources"""
    
    def __init__(self):
        self.historical_application = HistoricalStockDataApplication()
    
    def get(self):
        """
        Fetch historical data endpoint
        ---
        parameters:
          - name: pages
            in: query
            type: integer
            required: false
            description: Number of pages to fetch (default 1)
        responses:
          200:
            description: Historical data fetched and saved successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                stock_code:
                  type: string
                stock_id:
                  type: string
                entries_saved:
                  type: integer
                duplicates_skipped:
                  type: integer
                pages_fetched:
                  type: integer
          404:
            description: Stock not found
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: Stock with code XXXX not found
          500:
            description: Error fetching historical data
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: Error fetching historical data
        """
        pages = request.args.get('pages', default=1, type=int)
        result = self.historical_application.fetch_and_save_historical_data(pages)
        
        if not result.get('success', False):
            if 'Stock with code' in result.get('message', ''):
                return jsonify(result), 404
            else:
                return jsonify(result), 500
        
        return jsonify(result)


class DateRangeView(views.MethodView):
    """Class-based view for getting available date range for historical data"""
    
    def __init__(self):
        self.historical_application = HistoricalStockDataApplication()
    
    def get(self, stock_code):
        """
        Get available date range endpoint
        ---
        parameters:
          - name: stock_code
            in: path
            type: string
            required: true
            description: Stock code to get date range for
        responses:
          200:
            description: Available date range for historical data
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                stock:
                  type: object
                  properties:
                    id:
                      type: string
                    code:
                      type: string
                    name:
                      type: string
                date_range:
                  type: object
                  properties:
                    oldest_date:
                      type: string
                      format: date-time
                    newest_date:
                      type: string
                      format: date-time
                    has_data:
                      type: boolean
          404:
            description: Stock not found
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: Stock with code XXXX not found
        """
        result = self.historical_application.get_available_date_range(stock_code)
        
        if not result.get('success', False):
            return jsonify(result), 404
        
        return jsonify(result)


# Register the views with the blueprint
historical_data_view = HistoricalDataView.as_view('historical_data_api')
latest_price_view = LatestPriceView.as_view('latest_price_api')
price_variation_view = PriceVariationView.as_view('price_variation_api')
fetch_historical_data_view = FetchHistoricalDataView.as_view('fetch_historical_data_api')
date_range_view = DateRangeView.as_view('date_range_api')

# Add URL rules
historical_data_bp.add_url_rule('/<string:stock_code>', view_func=historical_data_view, methods=['GET'])
historical_data_bp.add_url_rule('/<string:stock_code>/latest', view_func=latest_price_view, methods=['GET'])
historical_data_bp.add_url_rule('/<string:stock_code>/variation', view_func=price_variation_view, methods=['GET'])
historical_data_bp.add_url_rule('/fetch', view_func=fetch_historical_data_view, methods=['GET'])
historical_data_bp.add_url_rule('/<string:stock_code>/date-range', view_func=date_range_view, methods=['GET'])
