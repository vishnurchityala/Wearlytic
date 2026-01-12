import os
import threading
import time
from django.apps import AppConfig
from .models import ImageGenerationTask, ImageGeneration
from .utils import generate_ai_product_image
from uuid import uuid4

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return

        def run_background_task():
            while True:
                try:
                    pending_tasks = ImageGenerationTask.objects.filter(status="pending")
                    for task in pending_tasks:
                        task.status = "processing"
                        task.save(update_fields=["status"])

                        image_url = generate_ai_product_image(task.get_full_prompt(), [])

                        ImageGeneration.objects.create(
                            id=str(uuid4()),
                            task=task,
                            creator=task.creator,
                            image=image_url
                        )

                        task.status = "completed"
                        task.save(update_fields=["status"])
                except Exception as e:
                    print("Background task error:", e)

                time.sleep(2)

        thread = threading.Thread(target=run_background_task, daemon=True)
        thread.start()
        print("Background task started")
