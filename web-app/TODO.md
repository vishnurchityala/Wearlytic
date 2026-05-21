# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [ ] Show catalog stats and freshness badges in the web app.
  - Display the total number of products cataloged on the landing page and playground page.
  - Add a "Last data fetched" badge in the web app using `last_data_fetched` from the backend catalog metadata API.
  - Consume the backend catalog metadata response backed by `CatalogMetadata` rows for `total_products` and `last_fetched`, normalized as `product_count` and `last_data_fetched`.
  - Handle loading, empty, and unavailable metadata states gracefully.
