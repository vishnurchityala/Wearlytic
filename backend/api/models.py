from django.db import models

class AppUser(models.Model):
	id = models.CharField(primary_key=True, max_length=64)
	supabase_uid = models.CharField(max_length=255, unique=True)
	name = models.CharField(max_length=255, blank=True, default="")
	tokens = models.IntegerField(default=50)
	info_prompt = models.TextField(blank=True, default="")
	base_image_path = models.CharField(max_length=1024, blank=True, default="")
	email = models.EmailField(unique=True)

	def __str__(self) -> str:
		return f"{self.name or self.email} ({self.id})"
