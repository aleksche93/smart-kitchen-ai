# Smart Kitchen AI - Technical Constraints

This directory serves as the technical guidelines for Agent Code Assist.

## 1. Database & Persistence
- **PK Standard:** UUID format must ALWAYS be strings. Do not use integer Primary Keys or custom `CHAR(32)` decorators. Use `String(36)` with `default=lambda: str(uuid.uuid4())`.
- **Anti-Pattern:** ⛔ NO BLOBS in SQLite. Binary data (e.g., receipt photos) belongs strictly in the `data/receipt_images/` physical directory, referencing the hash via `image_hash`.
- **Relational Integrity:** Implement `cascade="all, delete-orphan"` where appropriate to prevent ghost entities.

## 2. UI & Frontend Guidelines
- **UI Date Format:** "Month Day, Year" (e.g., April 07, 2026). All locale string transformations must adhere to this.
- **UI_TABLE_STANDARD:** All metadata lists (like receipts) must use 4-column responsive tables.
- **Reactivity Flow:** Store actions and composables (`useKitchenAPI.js`) must follow a "Trigger -> Refresh" pattern. When an async mutation occurs (e.g. `scanReceipt`), it must strictly trigger a refresh of the global state (e.g., `fetchFridge()`, `fetchHistory()`) on success to maintain frontend-backend sync without page reloads.
- **Theme:** Always use Tailwind Dark Mode with the project's specific palette.

## 3. Storage & Process Lifecycle
- **BINARY_STORAGE_POLICY:** Raw images are transient; only processed/cropped artifacts are persisted in `data/receipt_images/`.
