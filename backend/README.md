# Backend

![Django](https://img.shields.io/badge/Django-092e20?logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-a30000)
![Supabase](https://img.shields.io/badge/Supabase-3fcf8e?logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169e1?logo=postgresql&logoColor=white)

The backend is the Django REST API for Wearlytic.

## Responsibility

- Manage app users linked to Supabase identities.
- Serve authenticated product and category APIs.
- Store and update user profile/base-image metadata.
- Validate Supabase JWTs for protected endpoints.
- Store generated image assets through Supabase Storage.
- Trigger Gemini-powered product/outfit image generation.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Default local URL: `http://localhost:8000`

## Commands

```bash
python manage.py migrate
python manage.py runserver
python manage.py test
```

## API Surface

Root URLs:

| Path | Purpose |
| --- | --- |
| `/` | Plain `OK` health response. |
| `/admin/` | Django admin. |
| `/api/` | Mount point for app APIs. |

Current app routes:

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/users/create/` | Public | Create or update an app user from Supabase identity data. |
| `GET` | `/api/users/me/` | Required | Return the authenticated app user. |
| `PATCH` | `/api/users/<user_id>/` | Required | Update own `name` and `info_prompt`. |
| `PATCH` | `/api/users/<user_id>/base_image/` | Required | Replace own base image in Supabase Storage. |
| `GET` | `/api/users/me/generations/` | Required | List generated images for the current user. |
| `GET` | `/api/products/` | Required | Paginated product list with `category_ids`, `min_price`, `max_price`, and `page_size` filters. |
| `GET` | `/api/products/<product_id>/` | Required | Fetch one product by UUID. |
| `GET` | `/api/categories/` | Required | List all product categories. |
| `GET` | `/api/catalog/metadata/` | Public | Return catalog product count and last-data timestamp. |
| `POST` | `/api/image_generations/` | Required | Generate a try-on image for `super_user` accounts. |
| `POST` | `/api/auth/validate/` | Required | Validate the bearer token and return the authenticated email. |

## Environment

The API falls back to SQLite when Postgres settings are not provided.

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

`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are currently read during module
import by storage/auth helpers, so local commands may still need Supabase config
even when using SQLite. Image generation calls Gemini model
`gemini-2.5-flash-image` and requires `GEMINI_API_KEY`.

## Deployment

The root [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)
workflow does not build or deploy the backend. It only rebuilds the
`scraping-agent` and `data-ingestor` services on the VPS.

## Contribution Scope

External pull requests are not currently accepted for this service unless maintainers explicitly request them. Wearlytic currently accepts external PRs only for adding or improving website scrapers in [`../scraping-agent`](../scraping-agent/README.md).
