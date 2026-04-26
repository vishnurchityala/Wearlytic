# BUGS.md

## Scope

This file lists the top high-priority bugs found during a static review of the `backend` project.

Inclusion bar:

- backend startup failures,
- authentication/storage failures,
- user-facing API behavior that can silently fail or return misleading success responses.

Reviewed on: 2026-04-27.

## High-Priority Bugs

### 1. Supabase auth auto-create path contains an invalid nested-quote f-string

Affected files:

- `api/authentication.py`

What happens:

- The auth auto-create path builds the default profile image path with an f-string containing `payload["sub"]` inside a double-quoted f-string.
- This is a Python syntax error if the file is parsed as-is.

Why this is high priority:

- The backend may fail to import before serving any request.
- Every protected endpoint depends on `SupabaseJWTAuthentication`.

Fix direction:

- Use single quotes inside the expression or assign `payload["sub"]` to a local variable before formatting.
- Add at least a lightweight import/`manage.py check` test for authentication modules.

### 2. Supabase clients and storage helpers are created at import time

Affected files:

- `api/views.py`
- `api/authentication.py`
- `api/storage.py`

What happens:

- `SupabaseBucketManager.from_env("image_assets")` is called while modules import.
- `create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)` is also called at import time.
- Missing or invalid Supabase environment variables can fail startup before any route is called.

Why this is high priority:

- Local commands such as `python manage.py check`, tests, or app boot can fail even when the code path being tested does not need Supabase.
- It makes the SQLite local fallback less useful because storage credentials are still required for imports.

Fix direction:

- Lazily initialize Supabase clients when a storage/auth operation is actually needed.
- Fail with route-level errors for missing storage config instead of import-time crashes.
- Add tests that import URL/views/auth modules with mocked or absent Supabase env.

### 3. Image generation returns success-like responses for authorization and token failures

Affected files:

- `api/views.py`
- `api/serializers.py`
- `../web-app/src/pages/playground/components/ChatInputBar.jsx`

What happens:

- `image_generation_view` returns a normal DRF `Response` without an error status when a user has role `"user"`.
- The same pattern is used when tokens are exhausted.
- The frontend treats HTTP 2xx responses as successful unless the response contains a `status` field.

Why this is high priority:

- Failed image generation can look successful to the client.
- Invalid payloads can be appended to UI state.
- Token and role rules become difficult to reason about across backend and frontend.

Fix direction:

- Return explicit `403 Forbidden` for role failures.
- Return explicit `402`, `403`, or `400` for insufficient tokens depending on the chosen product contract.
- Standardize error response shapes and update the web app to handle them.
