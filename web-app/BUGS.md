# BUGS.md

## Scope

This file lists the top high-priority bugs found during a static review of the `web-app` project.

Inclusion bar:

- authentication or session-state issues,
- broken backend integration paths,
- user-facing workflows that can silently fail or corrupt UI state.

Reviewed on: 2026-04-27.

## High-Priority Bugs

### 1. API endpoint paths are inconsistent and depend on a fragile `VITE_API_BASE_URL` shape

Affected files:

- `src/api/env.js`
- `src/api/users.js`
- `src/pages/profile/components/ProfileDetailsForm.jsx`
- `src/pages/profile/components/ProfileImageForm.jsx`
- `src/pages/playground/components/MainContent.jsx`
- `src/pages/playground/components/ClothesSection.jsx`
- `src/pages/playground/components/ChatInputBar.jsx`
- `src/pages/profile/components/PastImageGenerationSection.jsx`

What happens:

- Some calls use `/api/...`, for example `/api/products/` and `/api/users/me`.
- Other calls use non-API-prefixed paths, for example `/users/me`, `/users/{id}/`, and `/users/{id}/base_image/`.
- These mixed paths only work reliably if `VITE_API_BASE_URL` is configured in the exact shape expected by `apiUrl()`, usually ending in `/api`.
- If `VITE_API_BASE_URL` is a normal backend origin such as `http://localhost:8000`, profile calls go to `/users/...` instead of `/api/users/...`.

Why this is high priority:

- Profile loading, profile updates, and base-image upload can break while product/category calls still work.
- The failure depends on environment configuration, making it easy to miss locally and hit after deployment.

Fix direction:

- Standardize all frontend API paths to one convention.
- Prefer backend-relative route constants or a small typed endpoint module.
- Document one exact expected `VITE_API_BASE_URL` shape and enforce it in `apiUrl()`.

### 2. Auth state is loaded only once and does not track Supabase auth changes or token refreshes

Affected files:

- `src/auth/AuthProvider.jsx`
- `src/auth/supabaseAuth.js`
- `src/routes/AppRouter.jsx`

What happens:

- `AuthProvider` calls `supabase.auth.getSession()` only once on mount.
- It does not subscribe to `supabase.auth.onAuthStateChange`.
- Token refreshes, external sign-outs, expired sessions, and auth changes in another browser tab are not reflected in React state until a reload.

Why this is high priority:

- The UI can keep treating a user as authenticated while API calls fail with stale or invalid tokens.
- Protected routes can remain accessible in the SPA after the session has changed elsewhere.

Fix direction:

- Subscribe to `supabase.auth.onAuthStateChange`.
- Update `user`, `token`, and `loading` from auth events.
- Clean up the subscription on unmount.

### 3. Image generation errors can be treated as successful generations

Affected files:

- `src/pages/playground/components/ChatInputBar.jsx`
- `src/pages/profile/components/PastImageGenerationCard.jsx`
- `src/pages/profile/components/PastImageGenerations.jsx`

What happens:

- `ChatInputBar` treats any HTTP 2xx response from `/api/image_generations/` as a valid generation unless the JSON contains a `status` key.
- The backend can return HTTP 200 with payloads such as `{"result": "Only Super Users are Allowed to use this feature."}`.
- That payload is appended to the image-generation list even though it is not an `ImageGeneration` object.

Why this is high priority:

- Normal users can see a successful UI path for a failed generation.
- Invalid generation objects can break rendering assumptions in generation cards and history views.

Fix direction:

- Validate the response shape before appending it to state.
- Treat backend `result` error payloads as errors.
- Align backend error status codes with frontend error handling.
