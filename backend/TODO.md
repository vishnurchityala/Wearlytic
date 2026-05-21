# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [ ] Add catalog metadata API for web-app product stats.
  - Expose a backend endpoint for `product_count` and `last_data_fetched` so the landing page and playground can show catalog size and freshness.
  - Add a `CatalogMetadata` table with `key`, `value`, and `updated_at` fields; store flexible values in `value` with a JSON-compatible type.
  - Seed or upsert rows for `total_products` and `last_fetched`.
  - Use `Product.objects.count()` or an ingestion-maintained `total_products` metadata row as the source for the total cataloged products value, but keep the API response field named `product_count`.
  - Use the persisted `last_fetched` metadata row as the source for `last_data_fetched`; update it after successful data-ingestor product ingestion.
  - Update serializers/routes/tests so the response is stable for authenticated web-app clients.
