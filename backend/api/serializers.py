from rest_framework import serializers
from .models import ImageGenerationTask, ImageGeneration, Product, AppUser, Category


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


class CatalogMetadataSerializer(serializers.Serializer):
    product_count = serializers.IntegerField(min_value=0)
    last_data_fetched = serializers.DateTimeField(allow_null=True)


class UpdateAppUserSerializer(serializers.Serializer):
	name = serializers.CharField(max_length=255, required=False, allow_blank=True)
	info_prompt = serializers.CharField(required=False, allow_blank=True)
	image = serializers.FileField(required=False, allow_empty_file=False)

class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ["id", "name", "email", "role","tokens"]

class ImageGenerationTaskSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer(read_only=True)
    products = serializers.SerializerMethodField()

    class Meta:
        model = ImageGenerationTask
        fields = ["id", "creator", "product_ids", "products", "custom_prompt", "status", "created_at", "updated_at"]
        read_only_fields = ["status", "created_at", "updated_at"]

    def get_products(self, obj):
        products = Product.objects.filter(id__in=obj.product_ids)
        return ProductSerializer(products, many=True).data

class ImageGenerationSerializer(serializers.ModelSerializer):
    task = ImageGenerationTaskSerializer(read_only=True)
    creator = CreatorSerializer(read_only=True)

    class Meta:
        model = ImageGeneration
        fields = ["id", "task", "creator", "image", "created_at"]
        read_only_fields = ["created_at"]
