# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [x] Restrict image generation processing to super users.
  - Require role `super_user` before backend image generation work starts.
  - Return explicit guardrail responses for non-super users.
  - Let super users bypass credit checks and generate without being charged credits.

- [x] Add catalog metadata API for web-app product stats.
  - Expose a backend endpoint for `product_count` and `last_data_fetched` so the landing page and playground can show catalog size and freshness.
  - Add a `CatalogMetadata` table with `key`, `value`, and `updated_at` fields; store flexible values in `value` with a JSON-compatible type.
  - Seed or upsert rows for `total_products` and `last_fetched`.
  - Use `Product.objects.count()` to sync the total cataloged products value, but keep the API response field named `product_count`.
  - Use the persisted `last_fetched` metadata row as the source for `last_data_fetched`; initialize it when metadata is seeded or first requested, and refresh it when product count changes.
  - Update serializers, routes, and docs so the response is stable for web-app clients.
