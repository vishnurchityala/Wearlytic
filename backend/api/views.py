from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenVerifySerializer

from .models import AppUser
from .serializers import (
	CreateUserSerializer,
	AppUserSerializer,
	GenerateTokenInputSerializer,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_authenticated_view(request):
	user = request.user
	return Response({
		"authenticated": True,
		"user_id": getattr(user, "id", None),
		"username": getattr(user, "username", None),
		"email": getattr(user, "email", None),
	})


@api_view(['POST'])
def create_user_view(request):
	serializer = CreateUserSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	validated = serializer.validated_data

	app_user_id = validated["supabase_uid"]
	app_user_defaults = {
		"supabase_uid": validated["supabase_uid"],
		"name": validated.get("name", ""),
		"tokens": 50,
		"info_prompt": validated.get("info_prompt", ""),
		"base_image_path": validated.get("base_image_path", ""),
		"email": validated["email"],
	}

	app_user, created = AppUser.objects.update_or_create(
		id=app_user_id,
		defaults=app_user_defaults,
	)

	UserModel = get_user_model()
	auth_user, _ = UserModel.objects.get_or_create(
		username=app_user.email,
		defaults={"email": app_user.email},
	)

	return Response(
		{
			"created": created,
			"app_user": AppUserSerializer(app_user).data,
		},
		status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
	)


@api_view(['POST'])
def generate_token_view(request):
	input_serializer = GenerateTokenInputSerializer(data=request.data)
	input_serializer.is_valid(raise_exception=True)
	data = input_serializer.validated_data

	try:
		if data.get("supabase_uid"):
			app_user = AppUser.objects.get(supabase_uid=data["supabase_uid"])
		else:
			app_user = AppUser.objects.get(email=data["email"])
	except AppUser.DoesNotExist:
		return Response(
			{"detail": "AppUser not found."},
			status=status.HTTP_404_NOT_FOUND,
		)

	UserModel = get_user_model()
	try:
		auth_user = UserModel.objects.get(username=app_user.email)
	except UserModel.DoesNotExist:
		return Response(
			{"detail": "Auth user missing. Create user first via /api/users/create/."},
			status=status.HTTP_400_BAD_REQUEST,
		)

	refresh = RefreshToken.for_user(auth_user)
	return Response(
		{
			"access": str(refresh.access_token),
			"refresh": str(refresh),
		},
		status=status.HTTP_200_OK,
	)


@api_view(['POST'])
def validate_token_view(request):
	token = (request.data or {}).get("token")
	if not token:
		return Response(
			{"detail": "Field 'token' is required."},
			status=status.HTTP_400_BAD_REQUEST,
		)
	serializer = TokenVerifySerializer(data={"token": token})
	serializer.is_valid(raise_exception=True)
	return Response({"valid": True}, status=status.HTTP_200_OK)
