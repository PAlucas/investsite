import logging
import requests
from flask import Flask, current_app
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os

logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Service for scheduling tasks in the application.
    Follows clean architecture principles by keeping scheduling logic separate.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.scheduler = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the scheduler with the Flask app.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Configure job stores
        jobstores = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
        
        # Create scheduler
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        
        # Register extension with app
        app.scheduler = self
        
        # Set up scheduled tasks based on configuration
        self._setup_scheduled_tasks()
        
        # Register start/shutdown handlers
        @app.before_first_request
        def start_scheduler():
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler started")
        
        @app.teardown_appcontext
        def shutdown_scheduler(exception=None):
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler shut down")
    
    def _setup_scheduled_tasks(self):
        """
        Set up all scheduled tasks based on app configuration.
        Tasks are defined in the app config with SCHEDULER_TASKS.
        """
        if not self.app.config.get('SCHEDULER_ENABLED', False):
            logger.info("Scheduler is disabled in configuration")
            return
        
        base_url = self.app.config.get('API_BASE_URL', 'http://localhost:5000')
        
        # Schedule stock fetching (daily at 6 PM)
        self.scheduler.add_job(
            func=self._make_api_request,
            trigger=CronTrigger(hour=1, minute=0),
            id='fetch_stocks',
            name='Fetch stocks from external sources',
            replace_existing=True,
            kwargs={
                'url': f"{base_url}/api/stocks/fetch",
                'method': 'GET'
            }
        )
        
        # Schedule news URL fetching (daily at 7 PM)
        self.scheduler.add_job(
            func=self._make_api_request,
            trigger=CronTrigger(hour=2, minute=0),
            id='save_stock_urls',
            name='Save news URLs for stocks',
            replace_existing=True,
            kwargs={
                'url': f"{base_url}/api/news/save-stock-urls",
                'method': 'GET'
            }
        )
        
        # Schedule news fetching (daily at 8 PM)
        self.scheduler.add_job(
            func=self._make_api_request,
            trigger=CronTrigger(hour=3, minute=0),
            id='fetch_news',
            name='Fetch news from InfoMoney',
            replace_existing=True,
            kwargs={
                'url': f"{base_url}/api/news/fetch",
                'method': 'POST',
                'json': {}
            }
        )
        
        # Schedule news content updating (daily at 9 PM)
        self.scheduler.add_job(
            func=self._make_api_request,
            trigger=CronTrigger(hour=4, minute=0),
            id='update_news_content',
            name='Update news content',
            replace_existing=True,
            kwargs={
                'url': f"{base_url}/api/news/update-content",
                'method': 'POST',
                'json': {}
            }
        )
        
        logger.info("Scheduled tasks have been set up")
    
    def _make_api_request(self, url, method='GET', **kwargs):
        """
        Make an API request to the specified URL.
        
        Args:
            url: The URL to make the request to
            method: HTTP method to use
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            Response from the API
        """
        with self.app.app_context():
            try:
                logger.info(f"Making scheduled {method} request to {url}")
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                logger.info(f"Scheduled request to {url} completed successfully: {response.status_code}")
                return response.json()
            except Exception as e:
                logger.error(f"Error in scheduled request to {url}: {str(e)}")
                return {"error": str(e)}
    
    def add_job(self, **kwargs):
        """
        Add a job to the scheduler.
        
        Args:
            **kwargs: Arguments to pass to scheduler.add_job
        
        Returns:
            Job instance
        """
        return self.scheduler.add_job(**kwargs)
    
    def remove_job(self, job_id):
        """
        Remove a job from the scheduler.
        
        Args:
            job_id: ID of the job to remove
        """
        self.scheduler.remove_job(job_id)
    
    def get_jobs(self):
        """
        Get all jobs in the scheduler.
        
        Returns:
            List of jobs
        """
        return self.scheduler.get_jobs()
