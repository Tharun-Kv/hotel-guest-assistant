# Evaluation

| Scenario | Input | Expected result | Actual result | Pass/Fail |
| --- | --- | --- | --- | --- |
| Check-in FAQ | `What time is check-in?` | Grounded check-in answer | Automated API test | Pass |
| Pool amenity | `Does the hotel have a pool?` | Grounded pool details | Automated intent/API test | Pass |
| Breakfast FAQ | `Is breakfast included?` | Grounded breakfast answer | Automated API test | Pass |
| Room fit | `Which room is good for 3 people?` | Smallest suitable capacity | Automated service/API test | Pass |
| Missing dates | `Are rooms available for 3 guests?` | Date clarification | Automated orchestration test | Pass |
| Invalid range | Equal check-in/check-out | HTTP 422 | Automated API test | Pass |
| Availability | Future dates + 3 guests | Structured room cards payload | Automated API test | Pass |
| Unsupported request | `Do you have a helicopter?` | Safe fallback | Automated API test | Pass |
| Assistant identity | `Who are you?` / `What can you do?` | Direct capabilities response without RAG fallback | Automated API test | Pass |
| Follow-up | Room question then breakfast | Grounded breakfast response | Automated API test | Pass |
| AI unavailable | No API key | No crash; deterministic fallback | Automated orchestration test | Pass |
| Capacity edge | 6 guests | No suitable published room | Automated service test | Pass |
| Booking overlap | Conflicting reservation dates | Booked room excluded | Automated availability test | Pass |
| RAG ingestion | Approved text about late checkout | Retrieved chunk carries source metadata | RAG unit test | Pass |
| Live inventory update | Mark a room as maintenance | Next availability search excludes that room | Admin API contract test | Pass |
| Frontend loading | Send a quick-action question | Staged connecting/checking/preparing indicator with timer icon | Production UI smoke check | Pass |
| Frontend API failure | Stop the backend before sending | Friendly error with retry/dismiss actions; no stack trace | Production UI smoke check | Pass |

The integration tests exercise the frontend-facing JSON contracts for chat and availability as an end-to-end contract flow: the payloads match the exact requests produced by `frontend/lib/api.ts`, then the FastAPI route, orchestrator, hotel repository, and response schema are exercised together. A browser smoke check consists of starting both apps, asking a quick-action question, submitting valid dates, and confirming room cards appear without exposing an error payload.
