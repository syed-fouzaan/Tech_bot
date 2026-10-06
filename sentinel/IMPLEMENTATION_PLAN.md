# Implementation Plan — Sentinel: Personal AI Engineering Intelligence Agent

## 1. Executive Summary & Architecture
Sentinel is a Telegram-first, personalized AI Engineering Intelligence Agent designed for an employed Data & AI Engineer (Syed at zig-zag.ai).
- **Core Loop**: Discover → Normalize → Deduplicate → Cluster → Verify → Score & Personalize → Explain → Compare → Teach → Track.
- **Hard Constraints**:
  - **$0 Hard Budget Cap**: Enforced at application and database layer. Zero paid API dependencies.
  - **Work-First Relevance**: Current job stack (Data + AI engineering) prioritized over side projects.
  - **Employer Confidentiality**: Strict PII/Secret scanner blocks confidential tokens/keys/code. Abstracted/private-local modes.
  - **Ponytail Discipline**: Pragmatic, lean architecture using existing installed packages (`fastapi`, `uvicorn`, `httpx`, `pydantic`, `sqlalchemy`, `aiogram`, `pytest`), no speculative bloat.

## 2. Component Blueprint
1. **Core & Config (`sentinel/app/config.py`, `security.py`, `db.py`, `models.py`)**:
   - Pydantic Settings with budget guards (`DAILY_AI_BUDGET=0`, `ALLOW_PAID_PROVIDERS=false`).
   - SQLite / PostgreSQL engine support (zero-config SQLite for immediate local testing, PostgreSQL ready).
   - Secret & credential regex scanner protecting work data.
2. **Multi-Provider AI Gateway (`sentinel/app/providers/`)**:
   - `AIProvider` Protocol and `AIGateway` with quota ledger, circuit breaker, retry/fallback.
   - Adapters: Google Gemini, Groq / OpenAI-compatible free tier, Local Ollama, and Deterministic Mock fallback.
3. **Source Adapters & Ingestion Pipeline (`sentinel/app/sources/`, `pipeline/`)**:
   - Adapters for arXiv, Hugging Face Hub, GitHub releases, RSS feeds, and Hacker News.
   - Deterministic filtering, URL canonicalization, hash deduplication, story clustering.
   - Epistemic markers: `[✅ Verified]`, `[📣 Claim]`, `[🧩 Inference]`, `[🎯 Recommendation]`, `[❓ Uncertainty]`.
   - Hype detector and contradiction detector.
4. **Domain Intelligence Engines (`sentinel/app/domain/`)**:
   - Seed user profile with work stack & confidentiality levels.
   - Dual-track roadmap (AI Engineering + Data Engineering) with 3-dimensional confidence (Theory, Practice, Production).
   - Spaced Repetition (SRS) review scheduler.
   - Hardware VRAM fit calculator (conservative FP16 / INT8 / Q4 estimates).
   - Model comparison engine (`/compare`) and implementation advisor (`/implement`).
   - Work Impact Log (`/win`) with metric validation.
5. **Telegram Bot UX & Webhook API (`sentinel/app/bot/`, `main.py`)**:
   - Command handlers: `/start`, `/today`, `/digest`, `/important`, `/why`, `/compare`, `/implement`, `/learn`, `/roadmap`, `/ask`, `/search`, `/profile`, `/work`, `/win`, `/hardware`, `/quiz`, `/review`, `/help`.
   - Clean Telegram formatting and interactive inline keyboards.
   - FastAPI app exposing `/health`, `/ready`, `/metrics`, `/telegram/webhook/{secret}` with background polling mode for local development.
6. **Testing & Quality Assurance (`tests/`)**:
   - Comprehensive test suite testing gateway, security scanner, pipeline, domain logic, command handlers, and end-to-end integration.
   - Ponytail audit and review.

## 3. Implementation Steps
- [x] Step 1: Initialize directory structure and configuration with $0 budget controls.
- [x] Step 2: Implement database models, storage, and PII/secret sanitizer.
- [x] Step 3: Implement multi-provider AI Gateway with quota management and circuit breakers.
- [x] Step 4: Implement source adapters (arXiv, HuggingFace, GitHub, RSS, HN) and ingestion pipeline with deduplication and epistemic labeling.
- [x] Step 5: Implement domain services (User profile, Living Roadmap, SRS, Hardware Fit, Model Comparison, Implementation Advisor, Work Impact Log).
- [x] Step 6: Implement Telegram bot command handlers, formatters, and FastAPI webhook / polling runner.
- [x] Step 7: Build complete test suite with unit and integration tests.
- [x] Step 8: Run Ponytail audit & review to ensure zero bloat and clean delivery.
