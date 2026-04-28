import psutil
import time
from django.utils.deprecation import MiddlewareMixin
from .apps import django_process, cpu_count

class SystemMonitorMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Store start time and resource usage
        request.start_time = time.time()
        request.cpu_percent = psutil.cpu_percent()
        request.memory_info = psutil.virtual_memory().percent
        

    def process_response(self, request, response):
        # Calculate duration
        duration = time.time() - request.start_time

        # Example: Add custom headers with server status
        response['X-System-CPU-Usage'] = f"{request.cpu_percent}%"
        response['X-System-Memory-Usage'] = f"{request.memory_info}%"
        response['X-Api-Page-Duration'] = f"{duration:.2f}s"

        # Check only the Django process, not the whole system
        mem_in_mb = django_process.memory_info().rss / 1024 / 1024
        django_mem_bytes = django_process.memory_info().rss 
        # Total system memory
        total_mem_bytes = psutil.virtual_memory().total
        # Calculate percentage
        django_percentage = (django_mem_bytes / total_mem_bytes) * 100

        response['X-Api-Memory-Usage'] = f"{mem_in_mb:.2f} MB ({django_percentage:.2f}%)"

        if django_process:
            # interval=None makes this non-blocking (immediate)
            raw_cpu = django_process.cpu_percent(interval=None)
        # Normalize for multi-core (e.g., 200% on 4 cores becomes 50%)
        normalized_cpu = raw_cpu / cpu_count

        response['X-Api-CPU-Usage'] = f"{normalized_cpu:.2f}%"

        # You can also log this data here
        #print(f"CPU: {request.cpu_percent}%, Mem: {request.memory_info}%, Time: {duration:.2f}s, Django Mem: {mem_in_mb:.2f} MB ({django_percentage:.2f}%)")

        return response
