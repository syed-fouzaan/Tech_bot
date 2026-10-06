# 🛡️ Sentinel — Personal AI & Data Engineering Intelligence Agent

[![Tests](https://img.shields.io/badge/Tests-38%20Passed-brightgreen)](tests/)
[![Operating Budget](https://img.shields.io/badge/Operating%20Budget-$0.00%20Hard%20Cap-blue)](render.yaml)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](requirements.txt)
[![Telegram](https://img.shields.io/badge/Telegram-@Syed__Marwan__bot-2CA5E0?logo=telegram)](https://t.me/Syed_Marwan_bot)

Sentinel is an autonomous, work-first AI & Data Engineering Intelligence Agent engineered with strict adherence to a **hard $0 / ₹0 operating budget**. It monitors arXiv, Hugging Face Hub, GitHub Releases, RSS engineering blogs, and Hacker News to deliver high-signal briefings, automated dependency risk analysis, local hardware fit assessments, spaced repetition learning, and executable AI lab benchmarks.

---

## ⚡ Key Highlights & Power Add-ons

1. **🛡️ Dependency Impact Radar (`/deps`)**:
   - Continuously monitors your day-job pinned dependencies (`vllm`, `apache-airflow`, `dbt-core`, `transformers`, `duckdb`).
   - Automatically cross-references CVE security advisories and breaking release notes.
   - Command: `/deps` or `/deps add <pkg==version>`.

2. **🧪 Personal AI Lab (`/lab`)**:
   - Generates immediately executable 45-minute benchmark scripts calibrated for constrained local hardware (**RTX 4060 8GB VRAM**).
   - Supports AWQ vs FP16 memory tests, vLLM PagedAttention continuous batching simulations, and custom micro-labs.
   - Command: `/lab <topic>` (e.g. `/lab awq` or `/lab vllm`).

3. **📊 Web Radar Dashboard**:
   - Interactive visual dashboard running alongside the API at `/dashboard`.
   - Real-time display of recent high-signal items, hype scores, epistemic confidence markers, and radar stats.

4. **🗺️ Living Dual-Track Roadmap (`/roadmap`)**:
   - Balances **Track A (Immediate Work Acceleration)** with **Track B (Long-Horizon Mastery)**.
   - Features Prove-It artifacts and active-recall spaced-repetition SRS quiz generation (`/quiz`).

5. **🔒 Zero-Trust Security & Invariant Enforcement**:
   - Scans and redacts PII and confidential company identifiers (`zig-zag.ai`).
   - Circuit breakers and quota ledgers guarantee that API costs never exceed **$0.00**.

---

## 🚀 Telegram Commands

| Command | Action |
| :--- | :--- |
| `/start` | Initializes your session and registers user allowlist |
| `/today` | Generates your live AI Engineering Daily Brief |
| `/important` | Lists MUST-KNOW developments from the past 7 days |
| `/why <tech>` | Senior Staff Engineer advisory on whether a technology matters for your stack |
| `/compare <a <b>` | Head-to-head comparison of two models/frameworks |
| `/implement <tech>` | Actionable step-by-step implementation guide |
| `/deps` | Checks pinned dependencies against breaking releases and CVEs |
| `/lab <topic>` | Synthesizes an executable local Python benchmark script |
| `/roadmap` | Displays your living progression and next recommended nodes |
| `/quiz` | Spaced-repetition active-recall quiz question |
| `/hardware` | Details registered local GPU and compute limits |
| `/fit <model>` | Computes VRAM fit, context ceiling, and quantization compatibility |
| `/win <title>` | Logs a business impact win in STAR format |
| `/help` | Complete command directory |

---

## 🌐 Deploying to Render (Free Tier)

This repository includes a native [`render.yaml`](render.yaml) Blueprint configuration.

### Method 1: Render Blueprint (Recommended)
1. Fork or push this repository to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → **Blueprint**.
4. Connect this GitHub repository (`Tech_bot`).
5. Render will automatically detect [`render.yaml`](render.yaml) and configure:
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn sentinel.app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
6. Fill in your environment variables in the Render UI:
   - `TELEGRAM_BOT_TOKEN`: Your token from @BotFather
   - `ALLOWED_TELEGRAM_USER_IDS`: `[1389004693]`
   - `GEMINI_API_KEY`: Google AI Studio Free Tier Key
   - `GROQ_API_KEY`: Groq Free Tier Key
7. Click **Apply**. Render will build and deploy your service!

### Method 2: Manual Web Service
1. Click **New +** → **Web Service**.
2. Set **Root Directory** to `.` (or leave empty).
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn sentinel.app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Advanced**, add `/health` to **Health Check Path**.
6. Add the environment variables from `.env.example`.

---

## ⏱️ 24/7 Keep-Alive with UptimeRobot

Render's free tier automatically spins down web services after 15 minutes of inactivity. You can use **UptimeRobot** for free to keep your bot active 24/7 and receive uptime alerts:

1. Sign up for free at [uptimerobot.com](https://uptimerobot.com).
2. Click **Add New Monitor**.
3. Configure the monitor:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Sentinel Bot`
   - **URL (or IP)**: `https://<YOUR-RENDER-SERVICE-NAME>.onrender.com/health`
   - **Monitoring Interval**: `5 minutes`
4. Click **Create Monitor**.

> **Result**: UptimeRobot will ping `/health` every 5 minutes. This ensures Render's free container stays warm and responsive 24 hours a day with 0 cost!

---

## 💻 Local Development & Testing

### 1. Clone & Setup
```bash
git clone https://github.com/syed-fouzaan/Tech_bot.git
cd Tech_bot
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp sentinel/.env.example sentinel/.env
```

### 2. Run Local Bot (Polling Mode)
```bash
python sentinel/run_bot.py
```

### 3. Run FastAPI Web Server & Dashboard
```bash
uvicorn sentinel.app.main:app --reload --port 8000
```
- Health Check: `http://localhost:8000/health`
- Web Radar Dashboard: `http://localhost:8000/dashboard`
- API Docs: `http://localhost:8000/docs`

### 4. Run Test Suite
```bash
cd sentinel
python -m pytest -v tests/
```

---

## 🔒 Security & Confidentiality
- Never commit `.env` or production API tokens.
- All outbound and logged text passes through `sentinel.app.core.security` PII and credential filters.
- Zero paid API calls: Database constraints reject any transaction with `cost > 0.00`.
