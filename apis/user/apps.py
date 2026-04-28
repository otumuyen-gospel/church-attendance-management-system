import os

from django.apps import AppConfig
import atexit
from concurrent.futures import ThreadPoolExecutor

import psutil

# Global variable to hold the executor
executor = None

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    label='user'

    def ready(self):
        global django_process
        global cpu_count
        global executor

        # Initialize the executor
        executor = ThreadPoolExecutor(max_workers=5)
        # Register the cleanup function
        atexit.register(self.cleanup)

        #Initialize process once
        django_process = psutil.Process(os.getpid())
        #Store core count for normalization
        cpu_count = psutil.cpu_count() or 1
        #Prime the counter (first call is always 0.0)
        django_process.cpu_percent(interval=None)

    def cleanup(self):
        global executor
        if executor:
            # wait=False ensures tasks doesn't need to finish, before shutdown
            executor.shutdown(wait=False)