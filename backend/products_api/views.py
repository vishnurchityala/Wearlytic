from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import base64

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

db = firestore.client()

@api_view(['GET'])
def get_products(request):
    """
    Retrieves paginated products from Firebase using Firestore cursors.
    """
    page_size = int(request.query_params.get('page_size', 10))
    start_after = request.query_params.get('start_after')

    try:
        products_ref = db.collection('products')
        query = products_ref.order_by(firestore.FieldPath.document_id()).limit(page_size)

        if start_after:
            decoded_start_after = base64.b64decode(start_after).decode('utf-8')
            start_after_doc = products_ref.document(decoded_start_after).get()
            if start_after_doc.exists:
                query = query.start_after(start_after_doc)
            else:
                return Response({'error': 'Invalid cursor'}, status=status.HTTP_400_BAD_REQUEST)

        results = query.stream()
        products = []
        last_doc_id = None
        for doc in results:
            product = doc.to_dict()
            products.append(product)
            last_doc_id = doc.id

        next_cursor = None
        if last_doc_id:
            next_cursor = base64.b64encode(last_doc_id.encode('utf-8')).decode('utf-8')

        return Response({
            'results': products,
            'next_cursor': next_cursor,
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)