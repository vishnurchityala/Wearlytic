import time
from django.core.management.base import BaseCommand
from api.models import ImageGenerationTask, ImageGeneration
from api.utils import generate_ai_product_image

class Command(BaseCommand):
    help = "Process image generation tasks"

    def handle(self, *args, **options):
        while True:
            pending_tasks = ImageGenerationTask.objects.filter(status="pending")
            for task in pending_tasks:
                task.status = "processing"
                task.save(update_fields=["status"])

                try:
                    image_url = generate_ai_product_image(task.get_full_prompt(), [])

                    ImageGeneration.objects.create(
                        task=task,
                        creator=task.creator,
                        image=image_url
                    )

                    task.status = "completed"
                except Exception:
                    task.status = "failed"

                task.save(update_fields=["status"])

            time.sleep(2)
