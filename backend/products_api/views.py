from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

db = firestore.client()

PAGE_SIZE = 30  # Number of products per page

@api_view(['GET'])
def get_products(request):
    try:
        page = int(request.GET.get("page", 1))
        last_doc_id = request.GET.get("last_doc", None)

        print(f"📌 Fetching Page: {page} | Last Doc ID: {last_doc_id}")

        # Query Firestore, ordered by a known field (created_at)
        products_ref = db.collection("products").order_by("created_at")

        # Apply pagination cursor
        if last_doc_id:
            last_doc = db.collection("products").document(last_doc_id).get()
            if last_doc.exists:
                products_ref = products_ref.start_after(last_doc)

        # Fetch the products
        docs = products_ref.limit(PAGE_SIZE).stream()
        products = [doc.to_dict() | {"id": doc.id} for doc in docs]

        # Set next page cursor (last document ID in this batch)
        next_page_cursor = products[-1]["id"] if len(products) == PAGE_SIZE else None

        return Response({
            "products": products,
            "page": page,
            "page_size": PAGE_SIZE,
            "has_next": bool(next_page_cursor),
            "has_prev": page > 1,
            "next_page_url": f"/api/products/?page={page + 1}&last_doc={next_page_cursor}" if next_page_cursor else None,
            "prev_page_url": f"/api/products/?page={page - 1}" if page > 1 else None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
