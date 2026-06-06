# Wearlytic Web App Context

Last updated: 2026-04-26

This file is the working context for agents making changes in this `web-app` project. Read it before editing code so changes stay aligned with the current app structure, backend contracts, and local conventions.

## Project Summary

Wearlytic is a React frontend for a virtual clothes try-on product. Users can browse clothing products, filter by category and price, select up to 3 products, enter a custom prompt, and generate try-on images through the backend. Authenticated users can also manage profile details, upload a base image used for generation, and view past image generations.

The frontend is a Vite single-page app deployed with Vercel rewrites. It uses Supabase Google OAuth and talks to a separate backend through `VITE_API_BASE_URL`.

## Tech Stack

- Framework/build: Vite 7, React 19, React DOM 19.
- Routing: `react-router-dom` 7 with `createBrowserRouter`.
- Styling: Tailwind CSS 4 via `@tailwindcss/vite` and `@import "tailwindcss"` in `src/index.css`.
- Auth: Supabase JS client, Google OAuth.
- Icons: Font Awesome React packages.
- Layout utility: `react-resizable-panels` for the desktop playground split view.
- Package manager: npm. `package-lock.json` is present.
- Language: JavaScript with JSX. There is no TypeScript setup.
- Tests: no test framework is configured currently.

## Common Commands

```bash
npm install
npm run dev
npm run build
npm run lint
npm run preview
```

Notes:

- `npm run dev` starts Vite locally.
- `npm run build` creates `dist/`.
- `npm run lint` runs ESLint over the project.
- `dist/` and `node_modules/` are ignored by `.gitignore`, although local copies may exist.

## Environment Variables

The local `.env` currently defines these variable names:

```bash
VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY
VITE_API_BASE_URL
VITE_DATABASE_URL
```

Important:

- Never commit secret values.
- `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are used by `src/auth/supabaseAuth.js`.
- `VITE_API_BASE_URL` is used by the centralized API env service in `src/api/env.js`.
- `VITE_DATABASE_URL` is present in `.env` but is not referenced by the current frontend source.
- Backend calls should use `apiFetch()` or `apiUrl()` from `src/api/env.js`, not hardcoded hostnames.

## App Entry And Routing

The active app entry is `src/main.jsx`, which mounts `src/routes/AppRouter.jsx`.

Routes:

- `/` renders `LandingPage`.
- `/landing` renders `LandingPage`.
- `/playground` renders `PlaygroundPage`, protected by auth.
- `/profile` renders `ProfilePage`, protected by auth.

Routing details:

- `AuthLayout` in `src/routes/AppRouter.jsx` wraps all routes in `AuthProvider`.
- `ProtectedRoute` checks `useAuth()`.
- While auth is loading, protected routes show a centered spinner.
- Unauthenticated users are redirected to `/landing`.
- `vercel.json` rewrites every path to `/`, which supports client-side routing on Vercel.

Page-owned components live beside their page folders. Shared chrome lives in `src/layout`.

## Authentication

Auth lives in:

- `src/auth/supabaseAuth.js`
- `src/auth/AuthProvider.jsx`
- `src/auth/AuthContext.js`

Current behavior:

- `supabaseAuth.js` creates a Supabase client using `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
- `AuthProvider` calls `supabase.auth.getSession()` once on mount.
- `AuthContext.js` exports `AuthContext` and `useAuth()`.
- Auth context values: `user`, `token`, `loading`, `loginWithGoogle`, `logout`.
- `loginWithGoogle` in `AuthProvider` redirects to `window.location.origin`.
- `logout` signs out through Supabase, clears local auth state, and navigates to `/`.

Important caveats:

- `AuthProvider` does not currently subscribe to `supabase.auth.onAuthStateChange`.
- `supabaseAuth.js` exports a separate `loginWithGoogle()` that redirects to `/auth/callback`, but there is no `/auth/callback` route and this function is not the one used by `LoginButton`.
- The navbar uses normal `<a href>` links instead of React Router `<Link>`, so navigation triggers full page reloads.

## Backend Integration

The app expects a backend API compatible with the configured `VITE_API_BASE_URL` service.

Central API service:

- `src/api/env.js` exports `API_BASE_URL`, `apiUrl(path)`, and `apiFetch(path, options)`.
- `API_BASE_URL` comes from `import.meta.env.VITE_API_BASE_URL`.
- `apiUrl()` trims trailing slashes from the base URL and safely joins endpoint paths.
- `apiUrl()` also accepts absolute backend URLs, extracts their path/query/hash, and rebuilds them against `VITE_API_BASE_URL`. This is used for paginated `next` and `previous` URLs returned by the backend.
- If `VITE_API_BASE_URL` ends with `/api`, `apiUrl("/api/...")` avoids producing duplicate `/api/api/...` paths.
- `src/api/users.js` re-exports the API client helpers and keeps profile-specific helpers such as `getCurrentUserProfile(token)`.

Backend calls:

- `src/routes/AppRouter.jsx` pings `GET /` every 40 seconds inside `AuthLayout`.
- `src/components/CatalogMetadataBadges.jsx` calls `GET /api/catalog/metadata/`.
- `src/pages/playground/components/MainContent.jsx` calls `GET /api/categories`.
- `src/pages/playground/components/ClothesSection.jsx` calls `GET /api/products/` and paginated `next`/`previous` URLs through `apiFetch()`.
- `src/pages/playground/components/ChatInputBar.jsx` calls `GET /api/users/me` and `POST /api/image_generations/`.
- `src/pages/profile/components/PastImageGenerationSection.jsx` calls `GET /api/users/me/generations/`.

Profile calls:

- `GET /users/me`
- `PATCH /users/{user.id}/`
- `PATCH /users/{user.id}/base_image/`

Because both `/api/...` endpoints and `/users/...` endpoints exist, preserve endpoint paths unless the backend contract changes. Set `VITE_API_BASE_URL` to the backend origin or API base expected by the environment.

## API Data Shapes Used By The UI

The UI assumes these response shapes.

Categories:

```js
[
  { id: string, name: string }
]
```

Products paginated response:

```js
{
  results: [
    {
      id: string,
      title: string,
      price: number,
      url: string,
      image_url: string,
      category_id: string
    }
  ],
  next: string | null,
  previous: string | null
}
```

Catalog metadata response:

```js
{
  product_count: number,
  last_data_fetched: string | null
}
```

Current user profile:

```js
{
  name: string | null,
  info_prompt: string | null,
  email: string,
  role: string,
  tokens: number,
  base_image_path: string | null
}
```

Image generation create request:

```js
{
  custom_prompt: string,
  input_products: Product[]
}
```

Image generation response:

```js
{
  id: string,
  image: string,
  task?: {
    custom_prompt: string,
    products: Product[]
  },
  created_at?: string
}
```

Past generations expect `task.custom_prompt`, `task.products`, `image`, and `created_at`.

## Main User Flows

Landing:

- `src/pages/landing/LandingPage.jsx`
- Uses `Navbar`, `HeroBanner`, `InfoCards`, `InfoBanner`, `SuggestionBox`, and `Footer`.
- Hero promotes virtual try-on and links to `/playground`.
- `HeroBanner` shows catalog product count and "Last data fetched" badges through `CatalogMetadataBadges`.
- Public brand/product imagery is served from `public/`.

Playground:

- `src/pages/playground/PlaygroundPage.jsx`
- Uses `Navbar` and `MainContent`.
- Protected route.
- Desktop layout uses `react-resizable-panels`: clothing browser on the left and try-on canvas on the right.
- Mobile layout stacks clothes section above playground section.
- Shows catalog product count and freshness badges above the playground split/stack layout.

Profile:

- `src/pages/profile/ProfilePage.jsx`
- Uses `Navbar`, `ProfileImageForm`, `ProfileDetailsForm`, and `PastImageGenerationSection`.
- Protected route.
- Users can upload a base image, edit name/info prompt, view role/tokens, and see past generations.

## Source Map

Top-level:

- `index.html`: root document, favicon, app mount at `#root`.
- `vite.config.js`: React plugin, Tailwind plugin, `@` alias to `src`.
- `eslint.config.js`: ESLint flat config for JS/JSX, React Hooks, React Refresh.
- `vercel.json`: SPA rewrite.
- `README.md`: project-specific setup, commands, environment, and deploy-scope notes.

Source:

- `src/main.jsx`: active entry point; mounts `AppRouter`.
- `src/routes/AppRouter.jsx`: router, auth layout, protected route, backend keepalive ping.
- `src/index.css`: imports Google fonts and Tailwind; defines `anton-regular`, `outfit-regular`, `bbh-bartle-regular`.
- `src/api/env.js`: centralized env-driven API URL builder and `apiFetch()`.
- `src/api/users.js`: profile-focused user API helper.
- `src/auth/AuthProvider.jsx`: auth context provider component.
- `src/auth/AuthContext.js`: auth context and `useAuth()` hook.
- `src/auth/supabaseAuth.js`: Supabase client setup.
- `src/layout/Navbar.jsx`: logo, nav links, mobile menu, login/logout button.
- `src/layout/LoginButton.jsx`: auth-dependent login/logout button.
- `src/layout/Footer.jsx`: footer logo, links, contact/social links.

Pages:

- `src/pages/landing/LandingPage.jsx`: public landing page.
- `src/pages/landing/components/`: landing-only hero, info cards, rotating info banner, and suggestion CTA.
- `src/pages/playground/PlaygroundPage.jsx`: protected playground shell.
- `src/pages/playground/components/`: product filters, product list/cards, split playground content, chat input, canvas, and generation cards.
- `src/pages/profile/ProfilePage.jsx`: protected profile page.
- `src/pages/profile/components/`: profile details, base-image upload, and past image generation history.

Assets/data:

- `public/`: logo, brand images, landing illustrations, no-results image, favicon.
- `categories_data.csv`: category names.
- `api_category_rows.csv`: category ID/name rows.
- `api_products_data.csv`: product rows for backend import shape.
- `product_warehouse.json`: large product warehouse data.
- `trial.py`: utility script that maps category names to IDs and writes `api_products_data.csv`.

## Styling And UI Conventions

- Most UI is composed with Tailwind utility classes directly in JSX.
- Fonts are loaded from Google Fonts in `src/index.css`.
- Common font utility classes:
  - `outfit-regular`
  - `anton-regular`
  - `bbh-bartle-regular`
- Visual style is mostly black/white/gray, rounded borders, and card-like sections.
- Font Awesome icons are used for user/logout, profile actions, filters, pagination, select state, and footer links.
- Product and generation image URLs are loaded directly in `<img>` tags.
- `index.html` sets `user-select: none` on the root, so text selection is disabled across the app.

## State Management

- There is no global state library.
- Auth state is React context through `AuthProvider`.
- Product selection is local state in `MainContent` and passed into clothes/playground children.
- Product filters and pagination are local to `ClothesSection`.
- Generated images from the current session are owned by `MainContent` and shared across mobile and desktop `PlaygroundSection` layouts.
- Profile forms fetch their own data using auth token from context.

## Current Constraints And Known Issues

- Backend path usage is inconsistent: some calls use `/api/...`, while profile helper calls use `/users/...`.
- `ChatInputBar` checks role on submit, blocks non-super-user generation in the UI, and shows inline guardrail notifications.
- `ProfileDetailsForm` does not handle non-OK responses on profile save.
- `ProfileImageForm` displays "Max 5MB" but does not enforce file size client-side.
- `Navbar` uses `<a href>` instead of router links.
- `Footer` has empty `href` values for some internal links.
- `SuggestionBox` contact button has no click behavior.

## Development Guidance For Agents

- Prefer using the existing Tailwind utility style unless introducing a broader design cleanup.
- Keep frontend changes aligned with the current route structure in `src/routes/AppRouter.jsx`.
- Use `useAuth()` for authenticated backend calls.
- Include `Authorization: Bearer ${token}` for protected backend endpoints.
- Be careful changing OAuth redirect behavior; Supabase redirect settings and deployed URLs must match.
- Before changing backend endpoint paths, confirm whether `VITE_API_BASE_URL` should include `/api` for the target environment.
- Do not read or expose `.env` secret values. Only document variable names.
- Do not edit generated/build folders such as `dist/` unless the task explicitly asks for deployment artifacts.
- Use `@` for cross-folder imports such as `@/api`, `@/auth`, `@/layout`, and route-level page imports.
- Use relative imports inside a page's own `components` folder.
- Run `npm run lint` after code changes when practical.
- Run `npm run build` before deployment-facing changes when practical.

## Deployment Notes

The root `.github/workflows/deploy.yml` GitHub Actions workflow does not deploy
the web app. It only rebuilds `scraping-agent` and `data-ingestor` on the VPS.
Keep frontend deployment changes aligned with `vercel.json`, Supabase redirect
settings, and `VITE_API_BASE_URL`.

## Git/Workspace Notes

- The repo may be part of a larger workspace with sibling projects such as `data-ingestor`.
- At the time this context was created, there were existing uncommitted changes in sibling paths outside `web-app`. They were not touched.
- For this app, create project docs and source changes inside the `web-app` root unless the user explicitly asks for cross-project changes.
