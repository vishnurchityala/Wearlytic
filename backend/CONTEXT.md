# Backend Context

This file gives working context for agents and contributors making changes in the `backend` project. Read it before editing backend code so changes stay compatible with the web app, Supabase auth/storage, and the image-generation workflow.

## Project Summary

The backend is a Django REST API used by the Wearlytic web app. It owns app-user records, product/category APIs, Supabase JWT authentication, Supabase Storage asset uploads, and Gemini-powered product/outfit image generation.

The backend is not the scraping pipeline. Scraping and ingestion live in sibling services:

- `../scraping-agent`
- `../data-ingestor`

## Tech Stack

- Django 5.0.9
- Django REST Framework
- `django-cors-headers`
- Supabase Python client
- Supabase JWT validation through JWKS
- PostgreSQL/Supabase Postgres for production-style DB usage
- SQLite fallback in settings for simple local startup
- Google Gemini image generation through `google-genai`
- Vercel Python deployment config in `vercel.json`

## Repository Layout

| Path | Role |
| --- | --- |
| `manage.py` | Django CLI entrypoint. |
| `backend/settings.py` | Project settings, installed apps, database selection, CORS, DRF auth class. |
| `backend/urls.py` | Root URL config. Mounts `api.urls` under `/api/`. |
| `backend/wsgi.py` | WSGI entrypoint used by Vercel config. |
| `backend/asgi.py` | ASGI entrypoint. |
| `api/models.py` | Database models for users, products, categories, image-generation tasks, and generated images. |
| `api/serializers.py` | DRF serializers and response shapes. |
| `api/views.py` | Function-based API views. |
| `api/urls.py` | API route table, relative to `/api/` from the project root. |
| `api/authentication.py` | Custom Supabase JWT authentication class. |
| `api/storage.py` | Supabase Storage helper for byte/file uploads and deletes. |
| `api/utils.py` | Gemini image-generation helper. |
| `api/migrations/` | Django migrations. |
| `api/tests.py` | Empty placeholder test module. |
| `requirements.txt` | Pinned Python dependencies. |
| `vercel.json` | Vercel deployment routing/build config. |

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Default local URL: `http://localhost:8000`

Useful commands:

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
python manage.py test
```

## Settings Behavior

`backend/settings.py` calls `load_dotenv()` and reads environment variables directly.

Database selection order:

1. `DATABASE_URL`, parsed as Postgres.
2. `SUPABASE_DB_HOST` plus Supabase DB variables, parsed as Postgres.
3. SQLite fallback at `backend/db.sqlite3`.

Current settings characteristics:

- `DEBUG = True`
- `CORS_ALLOW_ALL_ORIGINS = True`
- `SECRET_KEY` is hard-coded.
- `ALLOWED_HOSTS` includes localhost, Vercel/Render domains, and one IP.
- DRF authentication defaults to `api.authentication.SupabaseJWTAuthentication`.

Treat those defaults as development-oriented unless maintainers explicitly decide otherwise.

## Environment Variables

Common variables:

```bash
DATABASE_URL=
SUPABASE_DB_HOST=
SUPABASE_DB_NAME=
SUPABASE_DB_USER=
SUPABASE_DB_PASSWORD=
SUPABASE_DB_PORT=
SUPABASE_DB_SSLMODE=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_BUCKET=
SUPABASE_PROJECT_ID=
SUPABASE_JWT_SECRET=
GEMINI_API_KEY=
```

Notes:

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are required by `SupabaseBucketManager.from_env()`.
- Several modules create Supabase helpers at import time, so missing Supabase env can break import, tests, or startup before a request is handled.
- `SUPABASE_BUCKET` defaults to `generated-images` inside `storage.py`, but some call sites explicitly use bucket name `image_assets`.
- `GEMINI_API_KEY` is required only when image generation is called.

## URL Mounting And Frontend Contract

Root routes in `backend/urls.py`:

| Path | Purpose |
| --- | --- |
| `/` | Plain `OK` health response. |
| `/admin/` | Django admin. |
| `/api/` | Includes `api.urls`. |

Routes in `api/urls.py` are relative to `/api/` from the backend root.

The web app sometimes calls paths like `/api/products/` and sometimes paths like `/users/me`. `web-app/src/api/env.js` normalizes paths depending on whether `VITE_API_BASE_URL` already ends with `/api`. Preserve route compatibility when changing URL structure.

## API Routes

| Method | Full Path | Auth | View | Purpose |
| --- | --- | --- | --- | --- |
| `POST` | `/api/users/create/` | Public | `create_user_view` | Create or update app user data from Supabase identity input. |
| `GET` | `/api/users/me/` | Required | `me_view` | Return authenticated `AppUser`. |
| `PATCH` | `/api/users/<user_id>/` | Required | `update_user_view` | Update own `name` and/or `info_prompt`. |
| `PATCH` | `/api/users/<user_id>/base_image/` | Required | `update_user_base_image_view` | Replace own base image in Supabase Storage. |
| `GET` | `/api/users/me/generations/` | Required | `list_generations` | List generated images for current user. |
| `GET` | `/api/products/` | Required | `products_list_view` | Paginated product list with category and price filters. |
| `GET` | `/api/products/<product_id>/` | Required | `product_detail_view` | Fetch one product by UUID. |
| `GET` | `/api/categories/` | Required | `categories_list_view` | List all categories. |
| `GET` | `/api/catalog/metadata/` | Public | `catalog_metadata_view` | Return normalized catalog product count and freshness metadata. |
| `POST` | `/api/image_generations/` | Required | `image_generation_view` | Generate an AI image using profile base image plus selected product images. |
| `POST` | `/api/auth/validate/` | Required | `validate_token_view` | Return token validity and authenticated email. |

## Data Models

### `AppUser`

Represents a Wearlytic user linked to a Supabase identity.

Important fields:

- `id`: UUID primary key. The code often sets this to the Supabase user UUID.
- `supabase_uid`: unique Supabase user ID.
- `name`
- `tokens`
- `info_prompt`
- `base_image_path`: public URL to the user's base image.
- `email`
- `role`: `"user"` or `"super_user"`.

`is_authenticated` returns `True` so DRF permission checks can treat `AppUser` like an authenticated user object.

### `Category`

Simple UUID-keyed category table with unique `name`.

### `Product`

Product records served to the web app.

Important fields:

- `id`
- `title`
- `price`
- `url`
- `image_url`
- `category`

Indexes exist on:

- `price`
- `category, price`

### `CatalogMetadata`

Flexible key/value metadata for catalog stats.

Important rows:

- `total_products`: preferred product count source for the metadata API.
- `last_fetched`: ISO datetime string for the last successful catalog fetch.

The API syncs `total_products` from `Product.objects.count()` on each metadata request. If the count changed, it also refreshes `last_fetched`, so direct product inserts become visible on the next metadata read.

### `ImageGenerationTask`

Tracks an image generation request.

Important fields:

- `creator`
- `product_ids`
- `custom_prompt`
- `status`: `"pending"`, `"processing"`, `"completed"`, `"failed"`
- timestamps

`product_ids` uses `django.contrib.postgres.fields.ArrayField`, which is Postgres-specific. The SQLite fallback may not support all migration/runtime paths involving this model.

### `ImageGeneration`

Stores generated image metadata.

Important fields:

- `task`
- `creator`
- `image`: public URL returned by Supabase Storage
- `created_at`

## Serializers And Response Shapes

### Products

`ProductSerializer` nests the category:

```json
{
  "id": "uuid",
  "title": "Product title",
  "price": 999.0,
  "url": "https://...",
  "image_url": "https://...",
  "category": {
    "id": "uuid",
    "name": "Category"
  }
}
```

### Users

`AppUserSerializer` exposes:

```json
{
  "id": "uuid",
  "supabase_uid": "uuid",
  "name": "",
  "tokens": 50,
  "info_prompt": "",
  "base_image_path": "https://...",
  "email": "user@example.com",
  "role": "user"
}
```

### Image Generations

`ImageGenerationSerializer` returns the generated image plus nested task and creator data. `ImageGenerationTaskSerializer.get_products()` resolves `product_ids` back into `Product` rows.

## Authentication Flow

The default DRF authentication class is `SupabaseJWTAuthentication`.

Expected request header:

```http
Authorization: Bearer <supabase-access-token>
```

Current auth behavior:

1. Reads bearer token from `Authorization`.
2. Reads unverified JWT header to get `kid`.
3. Fetches/caches Supabase JWKS from `https://<SUPABASE_PROJECT_ID>.supabase.co/auth/v1/.well-known/jwks.json`.
4. Validates ES256 token with audience `authenticated` and Supabase issuer.
5. Looks up `AppUser` by `supabase_uid = payload["sub"]`.
6. If no user exists, auto-creates one with default profile image, default prompt, role `user`, and 50 tokens.

Important details:

- `validate_supabase_access_token()` exists for HS256 validation but is not used by `SupabaseJWTAuthentication`.
- JWKS are cached in process memory through `_JWKS_CACHE`.
- Auth auto-creation uploads a default image to Supabase Storage, so authentication can perform network I/O.
- The auth module imports `SupabaseBucketManager.from_env("image_assets")` at import time.

## User Creation Flow

`POST /api/users/create/` is public and accepts:

```json
{
  "supabase_uid": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "info_prompt": "optional prompt"
}
```

It:

1. Downloads a default image from Pexels.
2. Uploads it to Supabase Storage at `/profile/<supabase_uid>.jpg`.
3. Creates or updates `AppUser` with role `user` and 100 tokens.

Note the token default differs from auth auto-create, which uses 50 tokens.

## Profile Update Flow

`PATCH /api/users/<user_id>/`:

- Requires auth.
- Allows users to update only their own record.
- Updates `name` and `info_prompt`.

`PATCH /api/users/<user_id>/base_image/`:

- Requires auth.
- Allows users to update only their own base image.
- Accepts multipart file fields named `image` or `file`.
- Also supports raw image bytes if request content type starts with `image/`.
- Also supports `image_base64` in JSON/form data.
- Deletes the existing Supabase object by URL when possible.
- Uploads the replacement to `profile/<supabase_uid>.<ext>`.

## Product Listing Flow

`GET /api/products/`:

- Requires auth.
- Uses `Product.objects.select_related("category").all()`.
- Optional query params:
  - `category_ids`: comma-separated category UUIDs.
  - `min_price`: numeric.
  - `max_price`: numeric.
  - `page_size`: defaults to 100, max 300.
- Uses DRF `PageNumberPagination`.

Returned paginated shape:

```json
{
  "count": 123,
  "next": "https://...",
  "previous": null,
  "results": []
}
```

### Catalog Metadata

`GET /api/catalog/metadata/` returns:

```json
{
  "product_count": 123,
  "last_data_fetched": "2026-06-06T12:00:00Z"
}
```

`last_data_fetched` is initialized when metadata is seeded or first requested, and refreshes when the metadata endpoint detects a product-count change.

## Image Generation Flow

`POST /api/image_generations/`:

```json
{
  "custom_prompt": "optional user prompt",
  "input_products": [
    {
      "id": "uuid",
      "image_url": "https://..."
    }
  ]
}
```

Current behavior:

1. Requires authenticated user.
2. Requires non-empty `input_products`.
3. Requires every input product to include an `id`.
4. Loads `AppUser`.
5. Rejects any role other than `"super_user"` with HTTP `403` and a guardrail payload that confirms credits were not charged.
6. Super users bypass credit checks and are not charged credits for image generation.
7. Downloads the user's `base_image_path`.
8. Downloads every selected product image URL.
9. Creates `ImageGenerationTask(status="pending")`.
10. Marks task `processing`.
11. Calls `generate_ai_product_image(info_prompt + custom_prompt, base_image, input_images)`.
12. Uploads generated bytes to Supabase Storage at `/generations/<task_id>.jpg`.
13. Creates `ImageGeneration`.
14. Marks task `completed`.
15. Returns serialized `ImageGeneration`.

Known behavior to preserve or fix deliberately:

- `info_prompt + custom_prompt` concatenates without adding a separating space.
- Product IDs are taken from request payload without verifying those product rows exist before task creation.
- Failed generation marks the task failed and returns serialized task with HTTP 417.

## Storage Helper

`api/storage.py` defines `SupabaseBucketManager`.

Capabilities:

- Upload raw bytes with `store_bytes()`.
- Upload local files with `store_file()`.
- Delete by bucket-relative path with `delete_path()`.
- Delete by public Supabase URL with `delete_by_url()`.
- Extract object path from Supabase object URL.

Important details:

- Object paths are normalized with `lstrip("/")`.
- Uploads default to upsert behavior.
- `contentType` is guessed from the object path when not provided.
- Service-role key is required.

## Gemini Helper

`api/utils.py` defines `generate_ai_product_image()`.

It:

- Builds a Gemini client from `GEMINI_API_KEY`.
- Sends the text prompt, base image bytes, and product image bytes.
- Uses model `gemini-2.5-flash-image`.
- Requests `response_modalities=["IMAGE"]`.
- Returns the first inline image bytes found.
- Raises `RuntimeError` if no image is returned.

## Frontend Expectations

The web app currently calls backend endpoints from:

- `web-app/src/api/env.js`
- `web-app/src/api/users.js`
- profile components
- playground components

Do not change these contracts without updating the web app:

- `/api/categories`
- `/api/products/`
- `/api/users/me`
- `/api/image_generations/`
- `/api/users/me/generations/`
- `/users/me`
- `/users/<id>/`
- `/users/<id>/base_image/`

The frontend API helper can normalize `/api/...` duplication when `VITE_API_BASE_URL` already ends with `/api`.

## Tests

`api/tests.py` is currently a placeholder. There is no meaningful backend test suite yet.

Suggested future test coverage:

- Supabase JWT authentication with mocked JWKS.
- Product filtering and pagination.
- User profile update authorization.
- Base-image upload parser variants.
- Image-generation success/failure with mocked HTTP image fetches, Gemini, and Supabase Storage.

## Deployment Notes

`vercel.json` configures Vercel Python deployment:

- Source: `backend/wsgi.py`
- Runtime: `python3.12`
- All routes are sent to `backend/wsgi.py`

Check Vercel env vars carefully because import-time Supabase setup means missing variables can fail app boot.

The root `.github/workflows/deploy.yml` GitHub Actions workflow does not deploy
the backend. That workflow only rebuilds `scraping-agent` and `data-ingestor` on
the VPS.

## Known Caveats

- `SECRET_KEY`, `DEBUG`, and CORS settings are development-friendly and should be hardened before production exposure.
- `SupabaseBucketManager.from_env("image_assets")` is called at import time in multiple modules.
- `ImageGenerationTask.product_ids` uses Postgres `ArrayField`, so SQLite fallback is not equivalent for all flows.
- Default user creation differs between `create_user_view` and auth auto-create: 100 tokens vs 50 tokens.
- `api/admin.py` does not register models yet.
- `backend/db.sqlite3`, generated images, local virtualenvs, and `.env` files should not be committed.

## Contribution Scope

External pull requests are not currently accepted for this service unless maintainers explicitly request them. Wearlytic currently accepts external PRs only for adding or improving website scrapers in `../scraping-agent`.
