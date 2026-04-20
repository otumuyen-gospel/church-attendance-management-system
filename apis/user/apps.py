from django.apps import AppConfig
import atexit
from concurrent.futures import ThreadPoolExecutor

# Global variable to hold the executor
executor = None

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    label='user'

    def ready(self):
        global executor
        # Initialize the executor
        executor = ThreadPoolExecutor(max_workers=5)

        # Register the cleanup function
        atexit.register(self.cleanup)

    def cleanup(self):
        global executor
        if executor:
            # wait=False ensures tasks doesn't need to finish, before shutdown
            executor.shutdown(wait=False)