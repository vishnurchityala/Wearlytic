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

## Environment

Create `web-app/.env` with:

```bash
VITE_API_BASE_URL=
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

## Contribution Scope

External pull requests are not currently accepted for this service unless maintainers explicitly request them. Wearlytic currently accepts external PRs only for adding or improving website scrapers in [`../scraping-agent`](../scraping-agent/README.md).
