import os

import dotenv
dotenv.load_dotenv()

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, BaseParser


class RawImageParser(BaseParser):
    """
    Accept raw request bodies such as image/jpeg or image/png and return bytes.
    Placed last in parser_classes to avoid shadowing JSON/multipart parsers.
    """
    media_type = "*/*"

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()
from supabase import create_client
from .models import AppUser, Product, Category
from .serializers import (
	CreateUserSerializer,
	AppUserSerializer,
	ProductSerializer,
	CategorySerializer,
	UpdateAppUserSerializer
)

import requests

from .storage import SupabaseBucketManager

supabase_bucket_manager = SupabaseBucketManager.from_env("image_assets")

supabase_url = os.getenv("SUPABASE_URL")
service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(
    supabase_url,
    service_role_key
)

admin_auth_client = supabase.auth.admin


@api_view(['POST'])
def create_user_view(request):
	serializer = CreateUserSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	validated = serializer.validated_data
	app_user_id = validated["supabase_uid"]
	role = "user"
	tokens = 50
	default_image_url = "https://images.pexels.com/photos/1043471/pexels-photo-1043471.jpeg"
	uploaded_image_url = ""
	try:
		image_bytes = requests.get(default_image_url).content
		uploaded_image_url = supabase_bucket_manager.store_bytes(image_bytes,f"/profile/{app_user_id}.jpg")
	except Exception:
		return Response({
			"created":False,
			"response":"Failed to create user."
		}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	info_prompt = "A man standing with jacket on his hand and his handsome."

	app_user_defaults = {
        "supabase_uid": validated["supabase_uid"],
        "name": validated.get("name", ""),
        "tokens": tokens,
        "info_prompt": validated.get("info_prompt",info_prompt),
        "base_image_path": uploaded_image_url,
        "email": validated["email"],
        "role": role,
    }
	
	app_user, created = AppUser.objects.update_or_create(
        id=app_user_id,
        defaults=app_user_defaults,
    )

	return Response(
        {
            "created": created,
            "app_user": AppUserSerializer(app_user).data,
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
	serializer = AppUserSerializer(request.user)
	return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser, RawImageParser])
def update_user_view(request, user_id):
	try:
		user = AppUser.objects.get(id=user_id)
	except AppUser.DoesNotExist:
		raise NotFound("User not found")

	if str(request.user.id) != str(user_id) and request.user.role != "super_user":
		raise PermissionDenied("You are not allowed to update this user")

	# Handle raw-bytes image uploads (e.g., Content-Type: image/jpeg with raw body)
	if isinstance(request.data, (bytes, bytearray)):
		ct = request.META.get("CONTENT_TYPE", "") or request.content_type or ""
		if not ct.startswith("image/"):
			return Response({"detail": "Unsupported media type"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
		image_bytes = bytes(request.data)
		ext = ct.split("/")[-1].lower() if "/" in ct else "jpg"
		if ext == "jpeg":
			ext = "jpg"
		try:
			if user.base_image_path:
				try:
					supabase_bucket_manager.delete_by_url(user.base_image_path)
				except Exception:
					pass
			object_path = f"profile/{user.supabase_uid}.{ext}"
			new_url = supabase_bucket_manager.store_bytes(image_bytes, object_path)
			user.base_image_path = new_url
			user.save()
			return Response(AppUserSerializer(user).data)
		except Exception as e:
			return Response({"detail": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	# Otherwise, handle JSON/form and optional multipart file via serializer
	serializer = UpdateAppUserSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	validated = serializer.validated_data

	updated = False

	if "name" in validated:
		user.name = validated["name"]
		updated = True
	if "info_prompt" in validated:
		user.info_prompt = validated["info_prompt"]
		updated = True

	uploaded_file = validated.get("image")
	if uploaded_file is not None:
		try:
			image_bytes = uploaded_file.read()
			ext = "jpg"
			if getattr(uploaded_file, "name", None) and "." in uploaded_file.name:
				ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
				if ext == "jpeg":
					ext = "jpg"
			if user.base_image_path:
				try:
					supabase_bucket_manager.delete_by_url(user.base_image_path)
				except Exception:
					pass
			object_path = f"profile/{user.supabase_uid}.{ext}"
			new_url = supabase_bucket_manager.store_bytes(image_bytes, object_path)
			user.base_image_path = new_url
			updated = True
		except Exception as e:
			return Response({"detail": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	if updated:
		user.save()

	return Response(AppUserSerializer(user).data)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_token_view(request):
    return Response({"valid": True, "user": request.user.email})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categories_list_view(request):
	queryset = Category.objects.all()
	serializer = CategorySerializer(queryset, many=True)

	return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def products_list_view(request):
	queryset = Product.objects.select_related("category").all()
	params = request.query_params

	category_ids = params.get("category_ids")
	min_price = params.get("min_price")
	max_price = params.get("max_price")
	page_size = params.get("page_size")
    
	if page_size is None:
		page_size = 100

	if category_ids is not None:
		try:
			category_ids = [str(cid) for cid in category_ids.split(",")]
		except ValueError:
			raise ValidationError({
                "category_ids": "Must be a comma-separated list of integers."
            })
		queryset = queryset.filter(category_id__in=category_ids)
	
	if min_price is not None:
		try:
			min_price_val = float(min_price)
		except ValueError:
			raise ValidationError({"min_price": "Must be a valid number."})
		queryset = queryset.filter(price__gte=min_price_val)

	if max_price is not None:
		try:
			max_price_val = float(max_price)
		except ValueError:
			raise ValidationError({"max_price": "Must be a valid number."})
		queryset = queryset.filter(price__lte=max_price_val)

	paginator = PageNumberPagination()
	paginator.page_size = page_size
	paginator.page_size_query_param = "page_size"
	paginator.max_page_size = 300

	page = paginator.paginate_queryset(queryset, request)
	serializer = ProductSerializer(page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_detail_view(request, product_id):
    try:
        product = Product.objects.select_related("category").get(id=product_id)
    except Product.DoesNotExist:
        raise NotFound("Product not found")

    serializer = ProductSerializer(product)
    return Response(serializer.data)