# 🧠 Sentinel — Personal AI Engineering Intelligence Agent

Sentinel is a production-grade, Telegram-first AI Chief of Staff built specifically for an employed Data & AI Engineer (Syed at zig-zag.ai). It monitors the firehose of AI/ML developments, filters noise, checks claims against verified evidence, and delivers high-signal decision briefs and learning actions directly to Telegram under a hard **$0 operating budget**.

---

## 🚀 Key Features

1. **Hard $0 Budget Guard**:
   - Zero paid API calls. All providers operate strictly within free tiers (Google Gemini Free, Groq Free, and local Ollama fallback).
   - Invariant enforced at database check constraint and API gateway pre-flight.

2. **Work-First Intelligence & Confidentiality**:
   - Registered work stack (Python, SQL, vLLM, PyTorch, Airflow, dbt) receives top priority scoring.
   - Strict Secret & PII scanner prevents employer credentials, connection strings, or code from leaking to LLMs.
   - Work Impact Log (`/win`) captures measurable wins with before/after metrics for appraisals and 1on1s.

3. **Trust & Epistemic Verification Layer**:
   - Epistemic markers: `[✅ Verified fact]`, `[📣 Source claim]`, `[🧩 Inference]`, `[🎯 Recommendation]`, `[❓ Uncertainty]`.
   - Hype detector flags sensational claims lacking reproducible benchmark citations.
   - Contradiction detector catches conflicting context sizes or benchmark results.

4. **Dual-Track Living Roadmap & Spaced Repetition**:
   - Parallel tracks for AI Engineering and Data Engineering.
   - 3-dimensional confidence tracking: Theory, Practice, and Production.
   - Spaced Repetition (`/quiz`) reinforces concepts with prove-it artifacts.

5. **Pragmatic Engineering Commands**:
   - `/today` / `/digest`: Morning intelligence brief (< 3 minute read).
   - `/important`: Critical 🔥 MUST KNOW items from past 7 days.
   - `/why <topic>`: 10-point engineering decision breakdown.
   - `/compare <A> <B>`: Evidence-grounded model comparison with decision guide.
   - `/implement <tech>`: $0 local test path, cloud path, copy-paste code.
   - `/hardware` & `/fit <model>`: VRAM fit calculator (FP16 vs INT8 vs Q4).

---

## 🛠️ Quickstart

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Telegram bot token and free API keys (Gemini / Groq)
```

### 2. Run Tests
```bash
pytest -v tests/
```

### 3. Run FastAPI Web Service
```bash
uvicorn sentinel.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics
```
