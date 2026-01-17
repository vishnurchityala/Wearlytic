from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import requests
import jwt
import os
import dotenv
dotenv.load_dotenv()
from jwt import InvalidTokenError, ExpiredSignatureError
from .models import AppUser
"""
Token validation functions
"""


SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_ISSUER = f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1"
JWKS_URL = f"{SUPABASE_ISSUER}/.well-known/jwks.json"
_JWKS_CACHE = None


def get_public_key(kid: str):
    """
    Fetch the public key from Supabase JWKS for a given key ID.
    """
    global _JWKS_CACHE
    if _JWKS_CACHE is None:
        _JWKS_CACHE = requests.get(JWKS_URL).json()

    for key in _JWKS_CACHE["keys"]:
        if key["kid"] == kid:
            return jwt.algorithms.ECAlgorithm.from_jwk(key)
    raise ValueError(f"Public key not found for kid={kid}")

def validate_access_token(token: str) -> dict:
    """
    Validate a Supabase OAuth JWT (ES256) and return payload.
    Raises ValueError if token is invalid or expired.
    """
    try:
        # Read the token header without verification to get the kid
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("Token missing 'kid' header")

        # Fetch public key
        public_key = get_public_key(kid)

        # Decode & verify token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=SUPABASE_ISSUER,
        )
        return payload

    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def validate_supabase_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            issuer=SUPABASE_ISSUER,
        )
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except InvalidTokenError:
        raise ValueError("Invalid token")

class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = validate_access_token(token)
            # You can fetch or create a Django user here if needed
            try:
                user = AppUser.objects.get(supabase_uid=payload["sub"])
            except AppUser.DoesNotExist:
                email = payload['email']
                name = "DUMMY_NAME"
                role = "user"
                tokens = 50
                default_image_url = "https://images.pexels.com/photos/1043471/pexels-photo-1043471.jpeg"
                info_prompt = "A man standing with jacket on his hand and his handsome."

                # default values for account creation
                app_user_defaults = {
                    "supabase_uid": payload["sub"],
                    "name":name,
                    "tokens": tokens,
                    "info_prompt": info_prompt,
                    "base_image_path": default_image_url,
                    "email": email,
                    "role": role,
                }
                user, created = AppUser.objects.update_or_create(
                    id=payload["sub"],
                    defaults=app_user_defaults,
                )
            return (user, token)
        except ValueError as e:
            raise exceptions.AuthenticationFailed(str(e))
