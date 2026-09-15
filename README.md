# AI-Powered Hotel Guest Assistant

A full-stack interview assignment for grounded hotel questions, room recommendations, and deterministic availability checks. The design deliberately separates optional AI interpretation from hotel facts and booking logic.

## Problem and outcome

Guests should not have to wait for the front desk to learn a check-in time, amenity, policy, suitable room, or availability for a stay. The application offers chat for concierge questions and a structured date search for booking questions. All published facts originate in one JSON knowledge base; a model never guesses availability.

## Features

- Grounded FAQ, amenity, policy, and room-capacity answers
- Deterministic validation, capacity ranking, interval overlap, and availability results
- Hybrid local/optional OpenAI JSON intent and entity extraction
- Retrieval-augmented answers from scraped or manually approved hotel sources
- Operator console at `/admin` for knowledge ingestion and live inventory updates
- Bounded session conversation memory and follow-up support
- Responsive Next.js UI with quick actions, room cards, loading, and retryable errors
- Pydantic contracts, safe error responses, limited CORS, request IDs, and structured logs
- pytest unit and API integration tests

## Architecture

```text
Browser -> Next.js -> FastAPI route -> service / orchestrator
                                         |             |
                                Hotel JSON tool   availability tool
                                         |             |
                                  grounded facts deterministic result
                                         \             /
                                   structured API response
```

Routes own HTTP concerns, services own business rules, and repositories isolate storage. `HotelRepository` reads the current JSON source; `ConversationRepository` is a bounded in-memory seam that can be replaced with Redis or PostgreSQL. See [architecture.md](docs/architecture.md).

## Technology

- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, Pydantic v1-compatible schemas
- AI: Gemini API preferred, with optional OpenAI fallback; server-side only
- Testing: pytest with FastAPI TestClient/httpx-compatible requests
- Data: JSON behind repository interfaces

## Layout

```text
frontend/                 Next.js UI, hook, API client, typed components
backend/app/api/          FastAPI routes
backend/app/schemas/      Pydantic contracts
backend/app/services/     business and conversation services
backend/app/ai/           hybrid intent and guarded extraction
backend/app/tools/        controlled hotel/availability boundaries
backend/app/repositories/ JSON and memory abstractions
backend/app/data/         hotel knowledge base and bookings
backend/tests/            unit and API integration tests
docs/                     architecture, product, AI, evaluation
```

## AI safety and grounding

When configured, Gemini can classify an ambiguous intent or extract user-stated availability fields into a small JSON object. OpenAI remains supported as a fallback. The application validates every value afterward. The model cannot see booking records, call arbitrary application state, or make the final inventory decision.

Hotel data is retrieved before an answer is formed. Python owns dates, party size, room ranking, conflict checks, availability, and policy/amenity retrieval. Unsupported questions receive an honest fallback. Clear questions work without an API key. Details: [ai-decisions.md](docs/ai-decisions.md).

## Data structures and complexity

| Need | Structure / rule | Complexity |
| --- | --- | --- |
| Room and FAQ lookup | dictionary/hash map keyed by ID/category | O(1) average |
| Rooms, FAQs, messages, results | ordered lists | O(n) traversal |
| Supported intents and term groups | sets | O(1) average membership |
| Recommended room | filter then sort by capacity and price | O(n log n) |
| Booking conflicts | scan a room's booking records | O(n) |

Two half-open stays conflict when `existing_check_in < requested_check_out` and `existing_check_out > requested_check_in`. This correctly permits one guest to check in on another guest's checkout date.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | health/version check |
| `GET` | `/api/hotel` | public hotel knowledge data |
| `POST` | `/api/chat` | grounded chat reply and optional availability payload |
| `POST` | `/api/availability` | deterministic availability lookup |
| `POST` | `/api/conversation` | create/update bounded conversation history |
| `POST` | `/api/knowledge/search` | inspect retrieved source chunks |
| `POST` | `/api/admin/knowledge/ingest` | scrape a public page or index approved text |
| `GET` | `/api/admin/inventory` | view the current live inventory snapshot |
| `PUT` | `/api/admin/inventory` | atomically replace rooms, statuses, prices, and bookings |

Chat body:

```json
{
  "message": "What time is check-in?",
  "conversation_id": "optional-session-id",
  "conversation": [{ "role": "user", "content": "Hello" }]
}
```

## Setup

### Backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

macOS/Linux activation is `source .venv/bin/activate`. Swagger is available at `http://localhost:8000/docs`.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Environment

Backend `.env`:

```dotenv
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
ADMIN_API_TOKEN=
ENVIRONMENT=development
MAX_MESSAGE_LENGTH=1000
MAX_CONVERSATION_HISTORY=8
MAX_GUESTS=10
CORS_ORIGINS=http://localhost:3000
```

Set `GEMINI_API_KEY` to use Gemini. If it is empty, the app falls back to OpenAI when `OPENAI_API_KEY` is configured, then to deterministic local behavior. Only `NEXT_PUBLIC_API_URL` appears in the frontend environment. Never place an API key in a public variable. `.env` is ignored; `.env.example` is committed.

## RAG and live hotel operations

Open `http://localhost:3000/admin` to manage the local hotel. In development, the admin token may be blank. Outside development, set `ADMIN_API_TOKEN` and send it as `X-Admin-Token`.

The ingestion form accepts a public HTTP(S) hotel page or approved pasted content. The backend strips non-content HTML, chunks the text, stores source metadata, and ranks matching chunks with a deterministic TF-IDF-style lexical scorer. Gemini receives only the retrieved chunks and must answer from them; if the model is unavailable, the UI still receives a grounded excerpt with its source.

Availability is intentionally separate from RAG. The live inventory snapshot at `backend/app/data/live_inventory.json` contains room status, live prices, and booking intervals. Saving the snapshot through the admin console atomically replaces it, and the next `/api/availability` or chat availability request reads the new values. Retrieved prose can explain a policy, but it can never claim a room is available.

## Verify

```powershell
cd backend
pytest -q

cd ..\frontend
npm run build
```

The test suite covers FAQs, amenities, capacity selection, invalid dates, missing availability input, fallback behavior, follow-ups, AI unavailability, capacity limits, and booking overlap. API integration tests use the exact JSON contracts consumed by the frontend.

## cURL

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What time is check-in?"}'

curl -X POST http://localhost:8000/api/availability \
  -H "Content-Type: application/json" \
  -d '{"check_in":"2026-10-10","check_out":"2026-10-12","adults":3}'

curl -X POST http://localhost:8000/api/admin/knowledge/ingest \
  -H "Content-Type: application/json" \
  -d '{"url":"https://hotel.example.com/amenities","hotel_id":"default"}'

curl -X PUT http://localhost:8000/api/admin/inventory \
  -H "Content-Type: application/json" \
  -d '{"hotel_id":"default","rooms":[{"room_id":"DLX001","status":"available","price_per_night":249}],"bookings":[]}'
```

## Decisions, failures, and security

[product-decisions.md](docs/product-decisions.md) documents the guest journey and UX choices. [evaluation.md](docs/evaluation.md) records the core backend, RAG, inventory, and frontend scenarios.

The backend returns friendly error envelopes and hides stack traces. Request IDs and JSON logs avoid secrets and full guest content. CORS defaults to the local frontend origin rather than wildcard credentials. Availability remains usable when OpenAI is absent or unavailable.

## AI tools used during development

OpenAI Codex was used to scaffold, implement, review, and test the application. Gemini is an optional server-side runtime provider for intent classification, availability extraction, and grounded answer phrasing; it is not required for deterministic hotel questions or availability checks. No provider key is included in the repository.

## Production improvements

Before release, move JSON data and the local retrieval index to PostgreSQL plus a hosted vector store as the corpus grows; connect actual inventory APIs; use Redis for sessions and caching; add authentication, rate limits, tracing/metrics, secrets management, prompt/model versioning, evaluation gates, CI/CD, cloud deployment, monitoring, and human handoff.

## Development tools

FastAPI/Pydantic provide the typed API, Next.js/TypeScript/Tailwind provide the UI, pytest verifies behavior, and OpenAI is the constrained optional interpretation adapter.
