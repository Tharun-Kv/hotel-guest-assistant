# AI decisions

## Appropriate AI responsibilities

When configured, Gemini (with optional OpenAI fallback) is used only for ambiguous natural-language intent classification, incomplete availability entity extraction, and grounded answer phrasing over retrieved chunks. Structured calls request a small JSON object with a fixed schema. Recent bounded conversation context is supplied only for interpretation.

## Deterministic responsibilities

Python code validates dates and guest counts, ranks room capacities, checks interval overlap, retrieves hotel facts, applies booking conflicts, and builds the availability result. The model never receives booking records, cannot call arbitrary application code, and has no authority to override a service result.

## Hallucination prevention and grounding

Facts are read from `app/data/hotel.json` through `HotelRepository`. Response paths select an FAQ, amenity, policy, or room record before forming an answer. Unsupported questions return a transparent fallback instead of a plausible-sounding guess. Static, obvious questions work without an API key.

## Retrieval-augmented answers

Hotel operators can ingest a public page or approved text from `/admin`. HTML is reduced to visible text, split into bounded overlapping chunks, and ranked with a local lexical scorer. Retrieved chunks retain their source URL and are the only context supplied to Gemini/OpenAI for a generated answer. Without a model, the system returns a clearly attributed retrieved excerpt instead of inventing a completion. The search index is a replaceable JSON repository for this assignment; production can use embeddings and a vector store when the documentation corpus grows.

RAG is not an availability authority. Live room status, prices, and booking intervals are maintained by `InventoryRepository` and applied by `AvailabilityService` after date and occupancy validation.

## Failure behavior

An absent key, model outage, malformed model JSON, or rate limit falls back to local classification and safe responses. Availability submitted through the structured endpoint remains fully operational because it does not depend on an AI provider. Provider keys are server-only environment variables and are never sent to Next.js.
