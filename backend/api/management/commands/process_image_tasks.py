import logging
import time
from django.core.management.base import BaseCommand
from api.models import ImageGenerationTask, ImageGeneration
from api.utils import generate_ai_product_image

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Process image generation tasks"

    def handle(self, *args, **options):
        while True:
            pending_tasks = ImageGenerationTask.objects.filter(status="pending").select_related("creator")
            for task in pending_tasks:
                if task.creator.role != "super_user":
                    task.status = "failed"
                    task.save(update_fields=["status"])
                    self.stdout.write(
                        f"Skipped image generation task {task.id}: image generation is limited to Super Users."
                    )
                    continue

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
                    logger.exception(
                        "Queued image generation task failed",
                        extra={
                            "task_id": str(task.id),
                            "user_id": str(task.creator_id),
                            "product_count": len(task.product_ids or []),
                        },
                    )
                    task.status = "failed"

                task.save(update_fields=["status"])

            time.sleep(2)
