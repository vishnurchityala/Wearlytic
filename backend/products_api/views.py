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
    Supports next and previous pagination.
    """
    page_size = int(request.query_params.get('page_size', 10))  # Default page size
    start_after = request.query_params.get('start_after')
    end_before = request.query_params.get('end_before')

    try:
        products_ref = db.collection('products')  # Collection reference

        # Base query ordered by document name
        query = products_ref.order_by("__name__").limit(page_size + 1)  # Fetch extra to determine next/prev

        # Handling forward pagination (next page)
        if start_after:
            decoded_cursor = base64.b64decode(start_after).decode('utf-8')
            cursor_doc = db.collection('products').document(decoded_cursor).get()
            if cursor_doc.exists:
                query = query.start_after(cursor_doc)
            else:
                return Response({'error': 'Invalid cursor for next page'}, status=status.HTTP_400_BAD_REQUEST)

        # Handling backward pagination (previous page)
        if end_before:
            decoded_cursor = base64.b64decode(end_before).decode('utf-8')
            cursor_doc = db.collection('products').document(decoded_cursor).get()
            if cursor_doc.exists:
                query = products_ref.order_by("__name__").limit(page_size + 1).end_before(cursor_doc)
            else:
                return Response({'error': 'Invalid cursor for previous page'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the results
        results = list(query.stream())

        products = []
        first_doc_id = None
        last_doc_id = None

        for i, doc in enumerate(results):
            if i == 0:
                first_doc_id = doc.id  # First item in the fetched results
            last_doc_id = doc.id  # Last item in the fetched results
            products.append(doc.to_dict())

        # Remove extra document if it exists
        if len(products) > page_size:
            products.pop()  # Remove extra item to keep the page size correct
            last_doc_id = products[-1]['id']  # Update last doc ID

        # Generate next and previous cursors
        next_cursor = base64.b64encode(last_doc_id.encode('utf-8')).decode('utf-8') if last_doc_id else None
        prev_cursor = base64.b64encode(first_doc_id.encode('utf-8')).decode('utf-8') if first_doc_id else None

        # Generate URLs
        base_url = request.build_absolute_uri(request.path)
        next_url = f"{base_url}?{urlencode({'start_after': next_cursor, 'page_size': page_size})}" if next_cursor else None
        prev_url = f"{base_url}?{urlencode({'end_before': prev_cursor, 'page_size': page_size})}" if prev_cursor else None

        return Response({
            'products': products,
            'page_size': page_size,
            'has_next': bool(next_url),
            'has_prev': bool(prev_url),
            'next_page': next_url,
            'prev_page': prev_url
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
