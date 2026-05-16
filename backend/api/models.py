import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField 

class AppUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    supabase_uid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, default="")
    tokens = models.IntegerField(default=50)
    info_prompt = models.TextField(blank=True, default="")
    base_image_path = models.CharField(max_length=1024, blank=True, default="")
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=32,
        choices=(
            ("user", "User"),
            ("super_user", "Super User"),
        ),
        default="user",
    )

    @property
    def is_authenticated(self):
        return True

    def __str__(self) -> str:
        return f"{self.name or self.email} ({self.id})"


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField()
    price = models.FloatField()
    url = models.URLField()
    image_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self) -> str:
        return f"{self.title} ({self.id})"

    class Meta:
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["category", "price"]),
        ]


class ImageGenerationTask(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    creator = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="tasks")
    product_ids = ArrayField(
        models.UUIDField(),
        blank=True,
        default=list,
        help_text="List of product UUIDs associated with this task"
    )
    custom_prompt = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=32,
        choices=(
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ),
        default="pending"
    )
    
    def get_full_prompt(self):
        base_prompt = self.creator.info_prompt or ""
        return f"{base_prompt} {self.custom_prompt}".strip()
    
    def get_base_image_path(self):
        return self.creator.base_image_path

    def __str__(self):
        return f"Task {self.id} by {self.creator}"


class ImageGeneration(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    task = models.ForeignKey(ImageGenerationTask, on_delete=models.CASCADE, related_name="generated_images")
    creator = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="generated_images")
    image = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} for Task {self.task.id}"
