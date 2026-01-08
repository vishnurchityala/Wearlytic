from rest_framework import serializers
from .models import AppUser


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
		]


class CreateUserSerializer(serializers.Serializer):
	supabase_uid = serializers.CharField(max_length=255)
	email = serializers.EmailField()
	name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
	info_prompt = serializers.CharField(required=False, allow_blank=True, default="")
	base_image_path = serializers.CharField(max_length=1024, required=False, allow_blank=True, default="")


class GenerateTokenInputSerializer(serializers.Serializer):
	supabase_uid = serializers.CharField(max_length=255, required=False)
	email = serializers.EmailField(required=False)

	def validate(self, attrs):
		if not attrs.get("supabase_uid") and not attrs.get("email"):
			raise serializers.ValidationError("Provide 'supabase_uid' (preferred) or 'email'.")
		return attrs


