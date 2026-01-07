from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenVerifySerializer

from .models import AppUser


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
	"""
	Create an AppUser from provided inputs. Also ensures a Django auth user exists for JWT.
	Expected JSON:
	{
		"supabase_uid": "string",  // required; will also be used as id
		"name": "string",
		"info_prompt": "string",
		"base_image_path": "string",
		"email": "user@example.com"  // required
	}
	"""
	payload = request.data or {}
	required_fields = ["supabase_uid", "email"]
	missing = [f for f in required_fields if not payload.get(f)]
	if missing:
		return Response(
			{"detail": f"Missing required fields: {', '.join(missing)}"},
			status=status.HTTP_400_BAD_REQUEST,
		)

	# Use Supabase UID as our primary id; ignore any tokens input and default to 50
	app_user_id = payload["supabase_uid"]
	app_user_defaults = {
		"supabase_uid": payload["supabase_uid"],
		"name": payload.get("name", ""),
		"tokens": 50,
		"info_prompt": payload.get("info_prompt", ""),
		"base_image_path": payload.get("base_image_path", ""),
		"email": payload["email"],
	}

	# Create or update the AppUser
	app_user, created = AppUser.objects.update_or_create(
		id=app_user_id,
		defaults=app_user_defaults,
	)

	# Ensure a Django auth user exists for JWT issuance (username = email)
	UserModel = get_user_model()
	auth_user, _ = UserModel.objects.get_or_create(
		username=app_user.email,
		defaults={"email": app_user.email},
	)
	# We do not set a password here; external auth (e.g., Supabase) is expected.
	# If the user was created with a password earlier, we keep it as is.

	return Response(
		{
			"created": created,
			"app_user": {
				"id": app_user.id,
				"supabase_uid": app_user.supabase_uid,
				"name": app_user.name,
				"tokens": app_user.tokens,
				"info_prompt": app_user.info_prompt,
				"base_image_path": app_user.base_image_path,
				"email": app_user.email,
			},
		},
		status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
	)


@api_view(['POST'])
def generate_token_view(request):
	"""
	Generate JWT tokens for an AppUser/Django auth user.
	Expected JSON:
	{
		"supabase_uid": "string"   // preferred
		// or
		"email": "user@example.com"
	}
	"""
	data = request.data or {}
	email = data.get("email")
	supabase_uid = data.get("supabase_uid")
	if not email and not supabase_uid:
		return Response(
			{"detail": "Provide 'supabase_uid' (preferred) or 'email'."},
			status=status.HTTP_400_BAD_REQUEST,
		)

	try:
		if supabase_uid:
			app_user = AppUser.objects.get(supabase_uid=supabase_uid)
		else:
			app_user = AppUser.objects.get(email=email)
	except AppUser.DoesNotExist:
		return Response(
			{"detail": "AppUser not found."},
			status=status.HTTP_404_NOT_FOUND,
		)

	# Issue tokens for corresponding Django auth user (username=email)
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
	"""
	Validate a JWT (access or refresh).
	Expected JSON:
	{
		"token": "jwt_here"
	}
	"""
	token = (request.data or {}).get("token")
	if not token:
		return Response(
			{"detail": "Field 'token' is required."},
			status=status.HTTP_400_BAD_REQUEST,
		)
	serializer = TokenVerifySerializer(data={"token": token})
	serializer.is_valid(raise_exception=True)
	return Response({"valid": True}, status=status.HTTP_200_OK)
