import os
from flask import Flask, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from flasgger import Swagger
import sys
import logging
from lib.utils.scheduler  import Scheduler
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the session manager functions
from lib.db.session_manager import set_session_factory

# Import logging configuration
from lib.utils.logging_config import set_log_level, set_log_format, configure_logging

# Configure logging based on environment
if os.environ.get('FLASK_ENV') == 'development':
    set_log_level(logging.DEBUG)
else:
    set_log_level(logging.INFO)

# Set custom log format
set_log_format('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize logging
logger = configure_logging()

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure database
    db_uri = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-replace-in-production')
    
    # Configure scheduler
    app.config['SCHEDULER_ENABLED'] = os.getenv('SCHEDULER_ENABLED', 'False').lower() == 'true'
    app.config['API_BASE_URL'] = os.getenv('API_BASE_URL', 'http://localhost:5000')
    
    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    
    swagger_template = {
        "info": {
            "title": "Investing API",
            "description": "API for tracking stocks and InfoMoney news",
            "contact": {
                "responsibleOrganization": "RachaConta",
                "email": "contact@example.com"
            },
            "version": "1.0"
        },
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
    }
    
    # Create engine and session factory
    engine = create_engine(db_uri)
    session_factory_instance = sessionmaker(bind=engine)
    
    # Initialize the session factory
    set_session_factory(session_factory_instance)
    
    # Register blueprints
    from routes.stocks_routes_class import stocks_bp
    from routes.infomoney_news_routes import infomoney_news_bp
    
    app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    app.register_blueprint(infomoney_news_bp, url_prefix='/api/news')
    
    # Initialize Swagger
    Swagger(app, config=swagger_config, template=swagger_template)
    Scheduler().init_scheduler()
    
    # Register base route
    @app.route('/')
    def index():
        """
        Home endpoint
        ---
        responses:
          200:
            description: Welcome message
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Welcome to the Investing API
        """
        return jsonify({'message': 'Welcome to the Investing API'})
    
    # Health check endpoint for production monitoring
    @app.route('/health')
    def health_check():
        """
        Health check endpoint
        ---
        responses:
          200:
            description: Health status
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
        """
        return jsonify({'status': 'healthy'})
    
    return app

# Create app instance for running directly
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_DEBUG', False))
