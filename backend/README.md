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

## Deployment

The root [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)
workflow does not build or deploy the backend. It only rebuilds the
`scraping-agent` and `data-ingestor` services on the VPS.

## Contribution Scope

External pull requests are not currently accepted for this service unless maintainers explicitly request them. Wearlytic currently accepts external PRs only for adding or improving website scrapers in [`../scraping-agent`](../scraping-agent/README.md).
