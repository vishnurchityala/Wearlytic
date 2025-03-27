from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
from urllib.parse import urlencode

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

db = firestore.client()

@api_view(['GET'])
def get_products(request):
    try:
        page = int(request.GET.get("page", 1))  # Default to page 1
        page_size = int(request.GET.get("page_size", 30))  # Default page size 30
        base_url = request.build_absolute_uri(request.path)  # Get API base URL

        if page < 1:
            return Response({"error": "Page number must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)

        products_ref = db.collection("products").order_by("created_at")  # Order by creation time

        total_count = len(list(products_ref.stream()))  # Count total products
        total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages

        products = []
        paginated_ref = products_ref.offset((page - 1) * page_size).limit(page_size)  # Skip previous pages
        for doc in paginated_ref.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            products.append(data)

        # Generate next and previous page URLs
        next_page = f"{base_url}?{urlencode({'page': page + 1, 'page_size': page_size})}" if page < total_pages else None
        prev_page = f"{base_url}?{urlencode({'page': page - 1, 'page_size': page_size})}" if page > 1 else None

        return Response({
            "products": products,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_products": total_count,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": next_page,
            "prev_page": prev_page
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
