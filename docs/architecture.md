# Architecture

```text
Next.js client
    |
FastAPI routes and Pydantic validation
    |
ChatService / AvailabilityService
    |
AIOrchestrator ---- HotelSearchTool ---- HotelRepository (hotel.json)
    |
AvailabilityTool ---- booking interval checks
    |
Structured response to the client
```

Routes only translate HTTP requests and responses. Services hold application rules; repositories hide the JSON source so they can be replaced with PostgreSQL later. Tools are narrow boundaries that make grounded hotel lookups and deterministic availability explicit.

`AIOrchestrator` first uses local checks for obvious intents. If a question is ambiguous and a Gemini or OpenAI key is configured, it asks the model for a small JSON intent or availability-extraction object. Every model value is validated after extraction. The model receives no booking records and does not produce the final truth about inventory, policies, or amenities.

The RAG path is `source URL/manual text -> visible HTML extraction -> bounded chunks -> JSON lexical index -> top-k retrieval -> grounded Gemini/OpenAI answer`. Source title and URL are returned with the answer. The initial hotel JSON is indexed automatically, and an operator can re-index a page from `/admin` without changing application code.

Live inventory follows a separate path: `admin snapshot update -> atomic JSON replacement -> InventoryRepository -> AvailabilityService`. It includes statuses, live prices, and bookings. This prevents stale or semantically similar documentation from being mistaken for inventory truth.

Conversation state is stored behind `ConversationRepository`. The assignment implementation is an in-memory, lock-protected store capped at eight messages. `ConversationService` is the replacement seam for a Redis-backed production implementation.

Each request receives an `X-Request-ID`. Structured server logs include the request ID, endpoint, intent/result type, elapsed time, availability invocation, and safe error metadata. They never include API keys or full guest messages.
