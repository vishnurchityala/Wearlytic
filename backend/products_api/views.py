from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings

if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

db = firestore.client()

class ProductPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
def get_products(request):
    try:
        products_ref = db.collection('products')
        all_products = [doc.to_dict() for doc in products_ref.stream()]

        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(all_products, request)
        return paginator.get_paginated_response(paginated_products)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)