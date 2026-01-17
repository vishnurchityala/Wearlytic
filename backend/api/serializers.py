from rest_framework import serializers
from .models import AppUser, Category, Product


class AppUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = AppUser
		fields = [
			"id",
			"supabase_uid",
			"name",
			"tokens",
			"info_prompt",
			"base_image_path",
			"email",
			"role",
		]

class CreateUserSerializer(serializers.Serializer):
	supabase_uid = serializers.CharField(max_length=255)
	email = serializers.EmailField()
	name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
	info_prompt = serializers.CharField(required=False, allow_blank=True, default="")


class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
	category = CategorySerializer(read_only=True)

	class Meta:
		model = Product
		fields = [
			"id",
			"title",
			"price",
			"url",
			"image_url",
			"category",
		]


