import threading
import os
import time
from django.apps import AppConfig

# Global flag to control task
task_running = False
background_thread = None

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        global task_running, background_thread
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        def fetch_and_process_task():
            global task_running
            while task_running:
                print("Processing Image Generation Jobs.")
                time.sleep(1)
        
        task_running = True
        background_thread = threading.Thread(target=fetch_and_process_task, daemon=True)
        background_thread.start()
        print("Background task started")
