# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [x] Show image generation credit and super-user guardrail notifications.
  - Check the current user's role before submitting an image generation request.
  - Explain when generation is limited to Super Users and confirm credits were not charged.
  - Surface backend guardrail errors instead of treating failed generation responses as images.

- [x] Unify playground image generation state across mobile and desktop layouts.
  - `MainContent` renders separate mobile and desktop `PlaygroundSection` instances, and each `PlaygroundSection` currently owns its own `imageGenerations` state.
  - Move `imageGenerations` and `setImageGenerations` up to a single shared owner, or introduce a focused playground context provider around both layouts.
  - Ensure generated images persist when the viewport switches between mobile and desktop layouts.
  - Keep `TryoutCanvas` and `ChatInputBar` consuming the same generation list in both layouts.

- [x] Show catalog stats and freshness badges in the web app.
  - Display the total number of products cataloged on the landing page and playground page.
  - Add a "Last data fetched" badge in the web app using `last_data_fetched` from the backend catalog metadata API.
  - Consume the backend catalog metadata response backed by `CatalogMetadata` rows for `total_products` and `last_fetched`, normalized as `product_count` and `last_data_fetched`.
  - Handle loading, empty, and unavailable metadata states gracefully.
