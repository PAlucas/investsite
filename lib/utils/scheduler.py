from apscheduler.schedulers.background import BackgroundScheduler
import requests
import pytz
import logging
import os
tz = pytz.timezone("America/Sao_Paulo")

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app

        
    def add_all_masters_morning_flows_to_queue(self):
        base_url = "http://127.0.0.1:5000/api"
        headers = {
            "Content-type": "application/json"
        }
        
        requests.get(url=base_url+"/stocks/fetch", headers=headers)
        requests.get(url=base_url + "/news/save-stock-urls", headers=headers)
        requests.post(url=base_url + "/news/fetch",  headers=headers)
        requests.post(url=base_url + "/news/update-content",  headers=headers)
        requests.get(url=base_url + "/historical-data/fetch?pages=2",  headers=headers)
        
    def init_scheduler(self):
        logger.info('Initializing scheduler')
        self.scheduler.add_job(self.add_all_masters_morning_flows_to_queue, 'cron', hour=0, minute=0, max_instances=1, timezone=tz)
        self.scheduler.start()