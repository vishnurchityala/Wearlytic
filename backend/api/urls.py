from django.urls import path
from .views import (
	create_user_view,
    validate_token_view,
    products_list_view
)

urlpatterns = [
	path('users/create/', create_user_view, name='users_create'),
	path('products/', products_list_view, name='list_products'),
	path('auth/validate/', validate_token_view, name='validate_token'),
]