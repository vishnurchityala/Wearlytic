import os
import dotenv
dotenv.load_dotenv()
from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL")
service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(
    supabase_url,
    service_role_key
)

admin_auth_client = supabase.auth.admin

app_user = admin_auth_client.get_user_by_id('488c0ec3-56b9-4bd4-bc73-924ea5fab269')

import jwt
import requests
from jwt import InvalidTokenError, ExpiredSignatureError

PROJECT_ID = "knrbxuzorgcjgfmtkias"
ISSUER = f"https://{PROJECT_ID}.supabase.co/auth/v1"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"


def get_public_key(kid: str):
    jwks = requests.get(JWKS_URL).json()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwt.algorithms.ECAlgorithm.from_jwk(key)
    raise ValueError("Public key not found")


def validate_supabase_access_token(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        public_key = get_public_key(kid)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=ISSUER,
        )
        return payload

    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")

    
print(validate_supabase_access_token("eyJhbGciOiJFUzI1NiIsImtpZCI6ImQxNWZjNTk2LTNiMjctNDQyZC1hYjdiLWJmMjRiNjY5YjhiMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2tucmJ4dXpvcmdjamdmbXRraWFzLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIzYWYzZGVmNC04NjIxLTQzZTQtYmJiNS1hMDcxZjQ0NTM1ZjIiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY4NjgzOTIyLCJpYXQiOjE3Njg2ODAzMjIsImVtYWlsIjoidmlzaG51cmNoaXR5YWxhQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZ29vZ2xlIiwicHJvdmlkZXJzIjpbImdvb2dsZSJdfSwidXNlcl9tZXRhZGF0YSI6eyJhdmF0YXJfdXJsIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSUFGbjdYZVp1cWFhRjNyZHg0cnY4UlF4cG12aDM3eER6NXJnWFJBSWM1TGJNSHVHSnQ9czk2LWMiLCJlbWFpbCI6InZpc2hudXJjaGl0eWFsYUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiVmlzaG51IENoaXR5YWxhIiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwibmFtZSI6IlZpc2hudSBDaGl0eWFsYSIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0lBRm43WGVadXFhYUYzcmR4NHJ2OFJReHBtdmgzN3hEejVyZ1hSQUljNUxiTUh1R0p0PXM5Ni1jIiwicHJvdmlkZXJfaWQiOiIxMTU5MDM0OTQyODk5ODU0NDMwMDQiLCJzdWIiOiIxMTU5MDM0OTQyODk5ODU0NDMwMDQifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJvYXV0aCIsInRpbWVzdGFtcCI6MTc2ODY4MDMyMn1dLCJzZXNzaW9uX2lkIjoiY2RmNzNiMGYtNTFjNy00ZGZlLTg1YzEtYzA1OTM5ODgxOGYyIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.saVUdyDRNU1iGq1GqE3moTK-EMHvkE_BjtT1s6Onk0OJX6n19ZRPyZ1ahaBVat1P47QlAFAG2o9humzWYiainQ"))