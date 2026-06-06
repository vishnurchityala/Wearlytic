import os
import datetime
import json
import logging
import dotenv
dotenv.load_dotenv()

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, BaseParser
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .utils import generate_ai_product_image


class RawImageParser(BaseParser):
    media_type = "*/*"

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()
from supabase import create_client
from .models import AppUser, Product, Category, CatalogMetadata, ImageGenerationTask,ImageGeneration
from .serializers import (
	CreateUserSerializer,
	AppUserSerializer,
	ProductSerializer,
	CategorySerializer,
	CatalogMetadataSerializer,
	UpdateAppUserSerializer,
	ImageGenerationTaskSerializer,
	ImageGenerationSerializer
)

import requests

from .storage import SupabaseBucketManager

logger = logging.getLogger(__name__)

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
	tokens = 100
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
@parser_classes([FormParser, JSONParser])
def update_user_view(request, user_id):
	try:
		user = AppUser.objects.get(id=user_id)
	except AppUser.DoesNotExist:
		raise NotFound("User not found")

	if str(request.user.id) != str(user_id):
		raise PermissionDenied("You are not allowed to update this user")

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

	if updated:
		user.save()

	return Response(AppUserSerializer(user).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, RawImageParser, JSONParser])
def update_user_base_image_view(request, user_id):
	try:
		user = AppUser.objects.get(id=user_id)
	except AppUser.DoesNotExist:
		raise NotFound("User not found")

	if str(request.user.id) != str(user_id):
		raise PermissionDenied("You are not allowed to update this user")

	image_bytes = None
	uploaded_file = request.FILES.get("image") or request.FILES.get("file")
	if uploaded_file is not None:
		image_bytes = uploaded_file.read()
	elif isinstance(request.data, (bytes, bytearray)):
		ct = request.META.get("CONTENT_TYPE", "") or request.content_type or ""
		if ct.startswith("image/"):
			image_bytes = bytes(request.data)
	else:
		possible_file = request.data.get("file") if hasattr(request.data, "get") else None
		if possible_file is not None and hasattr(possible_file, "read"):
			image_bytes = possible_file.read()
		else:
			image_b64 = request.data.get("image_base64") if hasattr(request.data, "get") else None
			if image_b64:
				import base64
				try:
					image_bytes = base64.b64decode(image_b64)
				except Exception:
					return Response({"detail": "Invalid image_base64 payload"}, status=status.HTTP_400_BAD_REQUEST)

	if not image_bytes:
		return Response({"detail": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

	try:
		if user.base_image_path:
			try:
				supabase_bucket_manager.delete_by_url(user.base_image_path)
			except Exception:
				pass
		ext = "jpg"
		if uploaded_file and getattr(uploaded_file, "name", None) and "." in uploaded_file.name:
			ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
		else:
			ct = request.META.get("CONTENT_TYPE", "") or request.content_type or ""
			if ct.startswith("image/"):
				ext = ct.split("/")[-1].lower()
				if ext == "jpeg":
					ext = "jpg"
		object_path = f"profile/{user.supabase_uid}.{ext}"
		new_url = supabase_bucket_manager.store_bytes(image_bytes, object_path)
		user.base_image_path = new_url
		user.save()
	except Exception as e:
		return Response({"detail": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return Response({"base_image_path": user.base_image_path})
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


def _catalog_metadata_value(key):
	try:
		return CatalogMetadata.objects.get(key=key).value
	except CatalogMetadata.DoesNotExist:
		return None


def _sync_catalog_metadata():
	product_count = Product.objects.count()
	total_products, _created = CatalogMetadata.objects.get_or_create(
		key="total_products",
		defaults={"value": product_count},
	)
	product_count_changed = total_products.value != product_count
	if product_count_changed:
		total_products.value = product_count
		total_products.save(update_fields=["value", "updated_at"])

	last_fetched, _created = CatalogMetadata.objects.get_or_create(
		key="last_fetched",
		defaults={"value": timezone.now().isoformat()},
	)
	if product_count_changed or not last_fetched.value:
		last_fetched.value = timezone.now().isoformat()
		last_fetched.save(update_fields=["value", "updated_at"])

	return product_count, last_fetched.value


def _normalize_product_count(value):
	if isinstance(value, bool):
		return None
	if isinstance(value, int) and value >= 0:
		return value
	if isinstance(value, str) and value.isdigit():
		return int(value)
	return None


def _normalize_last_fetched(value):
	if not value:
		return None
	if isinstance(value, datetime.datetime):
		last_fetched = value
	elif isinstance(value, str):
		last_fetched = parse_datetime(value)
	else:
		return None

	if last_fetched is not None and timezone.is_naive(last_fetched):
		return timezone.make_aware(last_fetched, timezone=datetime.timezone.utc)
	return last_fetched


@api_view(["GET"])
@permission_classes([AllowAny])
def catalog_metadata_view(request):
	synced_product_count, synced_last_fetched = _sync_catalog_metadata()
	product_count = _normalize_product_count(_catalog_metadata_value("total_products"))
	if product_count is None:
		product_count = synced_product_count

	serializer = CatalogMetadataSerializer({
		"product_count": product_count,
		"last_data_fetched": _normalize_last_fetched(synced_last_fetched),
	})
	return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_detail_view(request, product_id):
    try:
        product = Product.objects.select_related("category").get(id=product_id)
    except Product.DoesNotExist:
        raise NotFound("Product not found")

    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def image_generation_view(request):
	body_data = request.data
	input_products = body_data.get("input_products", [])
	try:
		product_ids = [product["id"] for product in input_products]
	except (KeyError, TypeError):
		raise ValidationError("Each input product must include an id")
	custom_prompt = body_data.get("custom_prompt", "") or ""
	user_id = str(request.user.id)

	if not input_products:
		raise ValidationError("input_products is required")

	try:
		user = AppUser.objects.get(id=user_id)
		if user.role != "super_user":
			return Response(
				{
					"code": "image_generation_super_user_required",
					"detail": "Image generation is limited to Super Users. Your credits were not charged.",
					"required_role": "super_user",
					"current_role": user.role,
					"required_credits": 0,
					"available_credits": user.tokens or 0,
					"credits_charged": 0,
				},
				status=status.HTTP_403_FORBIDDEN,
			)
		info_prompt = user.info_prompt
		response = requests.get(user.base_image_path, timeout=10)
		response.raise_for_status()
		base_image = response.content
	except AppUser.DoesNotExist:
		raise NotFound("User not found")
	except requests.exceptions.RequestException:
		logger.exception(
			"Failed to fetch base image for image generation",
			extra={
				"user_id": user_id,
				"base_image_path": getattr(user, "base_image_path", ""),
			},
		)
		raise ValidationError("Failed to fetch base image")
	
	input_images = []

	for product in input_products:
		try:
			image_url = product["image_url"]
			response = requests.get(image_url, timeout=10)
			response.raise_for_status()
			input_images.append(response.content)
		except (KeyError, requests.exceptions.RequestException):
			logger.exception(
				"Failed to fetch product image for image generation",
				extra={
					"user_id": user_id,
					"product_id": product.get("id") if isinstance(product, dict) else None,
					"image_url": product.get("image_url") if isinstance(product, dict) else None,
				},
			)
			raise ValidationError("Invalid or unreachable product image")
	
	image_generation_task = ImageGenerationTask.objects.create(
		creator=user,
		product_ids=product_ids,
		custom_prompt=custom_prompt,
		created_at=str(datetime.datetime.now()),
		updated_at=str(datetime.datetime.now()),
		status="pending"
	)
	try:
		image_generation_task.status = "processing"
		image_generation_task.save()
		image_generated_bytes = generate_ai_product_image(info_prompt+custom_prompt,base_image,input_images)
		image_generated = supabase_bucket_manager.store_bytes(image_generated_bytes,f'/generations/{image_generation_task.id}.jpg')
		image_generation = ImageGeneration.objects.create(
			task=image_generation_task,
			creator=user,
			image=image_generated,
			created_at = str(datetime.datetime.now())
		)
		image_generation_task.status = "completed"
		image_generation_task.save()
		serializer = ImageGenerationSerializer(image_generation)
		return Response(serializer.data)
	except Exception:
		logger.exception(
			"Image generation processing failed",
			extra={
				"task_id": str(image_generation_task.id),
				"user_id": str(user.id),
				"product_count": len(input_products),
			},
		)
		image_generation_task.status = "failed"
		image_generation_task.save()
	
	serializer = ImageGenerationTaskSerializer(image_generation_task)
	return Response(serializer.data,status=status.HTTP_417_EXPECTATION_FAILED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_generations(request):
	try:
		serializer = AppUserSerializer(request.user)
		user_id = serializer.data['id']
		user = AppUser.objects.get(id=user_id)
	except AppUser.DoesNotExist:
		raise NotFound("User not found")
	
	if str(user_id) != str(user.id):
		return Response(status=status.HTTP_401_UNAUTHORIZED)
	
	generations = ImageGeneration.objects.filter(creator=user)
	serializer = ImageGenerationSerializer(generations,many=True)

	return Response(serializer.data,status=status.HTTP_200_OK)
