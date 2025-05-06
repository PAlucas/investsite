from flask import Blueprint, jsonify, request, views
from lib.application.stocks_application import StocksApplication
from lib.db.models.stocks import Stocks
from typing import List, Optional
from flasgger import swag_from
import logging

# Create blueprint
stocks_bp = Blueprint('stocks', __name__)
logger = logging.getLogger(__name__)

class StocksView(views.MethodView):
    """Class-based view for handling stock operations"""
    
    def __init__(self):
        self.stocks_application = StocksApplication()
    
    def get(self, code=None):
        """
        Get stocks endpoint
        ---
        parameters:
          - name: code
            in: path
            type: string
            required: false
            description: Stock code to retrieve
        responses:
          200:
            description: List of stocks or a single stock
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                stocks:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                        example: 123e4567-e89b-12d3-a456-426614174000
                      code:
                        type: string
                        example: PETR4
                      name:
                        type: string
                        example: PETROBRAS PN
                      company:
                        type: string
                        example: Petróleo Brasileiro S.A.
                      created_at:
                        type: string
                        format: date-time
                      updated_at:
                        type: string
                        format: date-time
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
        
        if code:
            # Get specific stock by code
            stock: Optional[Stocks] = self.stocks_application.get_stock_by_code(code)
            if stock is None:
                return jsonify({
                    'success': False,
                    'message': f'Stock with code {code} not found'
                }), 404
            
            return jsonify({
                'success': True,
                'stock': stock.to_dict()
            })
        else:
            # Get all stocks
            stocks: List[Stocks] = self.stocks_application.get_all_stocks()
            return jsonify({
                'success': True,
                'stocks': [stock.to_dict() for stock in stocks]
            })
    
    def post(self):
        """
        Create stocks endpoint
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - stocks
              properties:
                stocks:
                  type: array
                  items:
                    type: object
                    required:
                      - code
                      - name
                    properties:
                      code:
                        type: string
                        example: PETR4
                      name:
                        type: string
                        example: PETROBRAS PN
                      company:
                        type: string
                        example: Petróleo Brasileiro S.A.
        responses:
          201:
            description: Stocks created successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Successfully created 1 stock(s)
                stocks:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      code:
                        type: string
                      name:
                        type: string
          400:
            description: Invalid request data
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: No stocks data provided
        """
        data = request.get_json()
        
        if not data or 'stocks' not in data:
            return jsonify({
                'success': False,
                'message': 'No stocks data provided'
            }), 400
        
        new_stocks: List[Stocks] = self.stocks_application.save_stocks(data['stocks'])
        
        return jsonify({
            'success': True,
            'message': f'Added {len(new_stocks)} new stocks',
            'stocks': [stock.to_dict() for stock in new_stocks]
        })


class StocksFetchView(views.MethodView):
    """Class-based view for fetching stocks from external sources"""
    
    def __init__(self):
        self.stocks_application = StocksApplication()
    
    def get(self):
        """
        Fetch stocks from external source and save to database
        ---
        tags:
          - stocks
        summary: Fetch stocks from Investing.com and save to database
        description: Scrapes stock data from Investing.com and saves new stocks to the database
        responses:
          200:
            description: Stocks fetched and saved successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                source:
                  type: string
                  example: investing
                message:
                  type: string
                  example: Fetched and added 150 new stocks from Investing.com
          500:
            description: Error fetching stocks
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Error fetching stocks: Connection error"
        """
        
        try:
            logger.info("Fetching stocks from Genial Investimentos")
            count: int = self.stocks_application.fetch_and_save_stocks()
            return jsonify({
                'success': True,
                'source': 'genial',
                'message': f'Fetched and added {count} new stocks from Genial Investimentos'
            })
        except Exception as e:
            logger.error(f"Error fetching stocks: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error fetching stocks: {str(e)}'
            }), 500


# Register the views with the blueprint
stocks_view = StocksView.as_view('stocks_api')
stocks_fetch_view = StocksFetchView.as_view('stocks_fetch_api')

# Add URL rules
stocks_bp.add_url_rule('/', view_func=stocks_view, methods=['GET', 'POST'])
stocks_bp.add_url_rule('/<string:code>', view_func=stocks_view, methods=['GET'])
stocks_bp.add_url_rule('/fetch', view_func=stocks_fetch_view, methods=['GET'])
