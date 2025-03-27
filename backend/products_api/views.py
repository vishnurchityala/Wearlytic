from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import base64
from urllib.parse import urlencode

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

db = firestore.client()

@api_view(['GET'])
def get_products(request):
    """
    Retrieves paginated products from Firestore using cursors.
    If `start_after` is not provided, it automatically fetches the first page.
    """
    page_size = int(request.query_params.get('page_size', 10))  # Default page size
    start_after = request.query_params.get('start_after')

    try:
        products_ref = db.collection('products')  # Collection reference
        query = products_ref.order_by("product_name").limit(page_size)

        # If start_after is provided, fetch the document snapshot
        if start_after:
            decoded_cursor = base64.b64decode(start_after).decode('utf-8')
            cursor_doc = db.collection('products').document(decoded_cursor).get()
            if cursor_doc.exists:
                query = query.start_after(cursor_doc)  # Use the document snapshot
            else:
                return Response({'error': 'Invalid cursor'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the results
        results = list(query.stream())

        products = []
        first_doc_id = None
        last_doc_id = None

        for doc in results:
            product = doc.to_dict()
            products.append(product)
            if first_doc_id is None:
                first_doc_id = doc.id
            last_doc_id = doc.id

        # Generate next page cursor
        next_cursor = None
        if last_doc_id:
            next_cursor = base64.b64encode(last_doc_id.encode('utf-8')).decode('utf-8')

        # Generate previous page cursor
        prev_cursor = None
        if start_after:
            prev_query = (
                products_ref.order_by("product_name", direction=firestore.Query.DESCENDING)
                .limit(page_size + 1)
            )
            decoded_cursor = base64.b64decode(start_after).decode('utf-8')
            prev_doc = db.collection('products').document(decoded_cursor).get()
            if prev_doc.exists:
                prev_query = prev_query.start_after(prev_doc)
            prev_docs = list(prev_query.stream())

            if len(prev_docs) > 1:
                prev_cursor = base64.b64encode(prev_docs[-2].id.encode('utf-8')).decode('utf-8')

        # Generate next and prev URLs
        base_url = request.build_absolute_uri(request.path)
        next_url = f"{base_url}?{urlencode({'start_after': next_cursor})}" if next_cursor else None
        prev_url = f"{base_url}?{urlencode({'start_after': prev_cursor})}" if prev_cursor else None

        return Response({
            'products': products,
            'page_size': page_size,
            'has_next': next_url is not None,
            'has_prev': prev_url is not None,
            'next_page': next_url,
            'prev_page': prev_url
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
