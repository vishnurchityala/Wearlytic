from django.urls import path
from .views import (
	create_user_view,
    validate_token_view,
    products_list_view,
    product_detail_view,
    categories_list_view,
    me_view,
    update_user_view,
    update_user_base_image_view
)

urlpatterns = [
	path('users/create/', create_user_view, name='users_create'),
	path('users/me/', me_view, name='users_me'),
    path('users/<uuid:user_id>/base_image/', update_user_base_image_view, name='users_update_base_image'),
    path('users/<uuid:user_id>/', update_user_view, name='users_update'),
	path('products/', products_list_view, name='list_products'),
	path('categories/', categories_list_view, name='list_categories'),
    path("products/<uuid:product_id>/", product_detail_view, name="product-detail"),
	path('auth/validate/', validate_token_view, name='validate_token'),
]