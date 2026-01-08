from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
	is_authenticated_view,
	create_user_view,
	generate_token_view,
	validate_token_view,
	products_list_view,
)

urlpatterns = [
	path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('auth/token/generate/', generate_token_view, name='token_generate'),
	path('auth/token/validate/', validate_token_view, name='token_validate'),
	path('users/create/', create_user_view, name='users_create'),
	path('is_authenticated/', is_authenticated_view, name='is_authenticated'),
	path('products/', products_list_view, name='products_list'),
]


