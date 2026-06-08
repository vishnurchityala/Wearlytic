# Web App

![React](https://img.shields.io/badge/React-20232a?logo=react&logoColor=61dafb)
![Vite](https://img.shields.io/badge/Vite-646cff?logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-06b6d4?logo=tailwindcss&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3fcf8e?logo=supabase&logoColor=white)

The web app is the main user-facing Wearlytic client.

## Responsibility

- Authenticate users with Supabase.
- Browse and filter fashion products.
- Manage user profile details and base images.
- Select products for AI-assisted outfit/image generation.
- Display previously generated images.

## Local Development

```bash
npm install
npm run dev
```

Default local URL: `http://localhost:5173`

## Commands

```bash
npm run dev
npm run lint
npm run build
npm run preview
```

## Routes

| Path | Auth | Purpose |
| --- | --- | --- |
| `/` | Public | Landing page. |
| `/landing` | Public | Landing page. |
| `/playground` | Required | Product browser, filters, selected-product canvas, and image generation. |
| `/profile` | Required | Profile details, base image upload, and past generations. |

`AuthProvider` reads the current Supabase session on mount. Protected routes
redirect unauthenticated users to `/landing`.

## Environment

Create `web-app/.env` with:

```bash
VITE_API_BASE_URL=
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

`VITE_API_BASE_URL` may be set to the backend API base, such as
`http://localhost:8000/api`. The shared API helper in `src/api/env.js` trims
trailing slashes, prevents duplicate `/api/api/...` paths, and rewrites
paginated absolute URLs returned by Django back through the configured base.

Current backend calls include product/category browsing, catalog metadata,
profile reads/updates, base-image upload, generation history, and
`POST /api/image_generations/` for `super_user` image generation.

## Deployment

The root [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)
workflow does not build or deploy the web app. It only rebuilds the
`scraping-agent` and `data-ingestor` services on the VPS.

## Contribution Scope

External pull requests are not currently accepted for this service unless maintainers explicitly request them. Wearlytic currently accepts external PRs only for adding or improving website scrapers in [`../scraping-agent`](../scraping-agent/README.md).
