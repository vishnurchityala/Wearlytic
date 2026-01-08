from django.db import models

class AppUser(models.Model):
	id = models.CharField(primary_key=True, max_length=64)
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

	def __str__(self) -> str:
		return f"{self.name or self.email} ({self.id})"


class Category(models.Model):
	name = models.CharField(max_length=255, unique=True)

	def __str__(self) -> str:
		return self.name


class Product(models.Model):
	id = models.CharField(primary_key=True, max_length=64)
	title = models.CharField(max_length=255)
	price = models.FloatField()
	url = models.URLField(max_length=1024)
	image_url = models.URLField(max_length=1024)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

	def __str__(self) -> str:
		return f"{self.title} ({self.id})"
