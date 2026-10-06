"""Interactive Web Radar Dashboard served directly by FastAPI."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.db.session import get_db
from sentinel.app.models import ItemModel
from sentinel.app.domain.profile import get_default_profile
from sentinel.app.domain.roadmap import RoadmapEngine
from sentinel.app.domain.dependencies import parse_dependency_manifest

router = APIRouter(tags=["Dashboard"])
profile = get_default_profile()
roadmap_engine = RoadmapEngine()

DEFAULT_MANIFEST = """vllm==0.5.4
apache-airflow==2.9.1
dbt-core==1.7.0
transformers==4.41.0
pytorch==2.3.0
duckdb==0.10.0"""


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(session: AsyncSession = Depends(get_db)) -> str:
    # Fetch recent items
    stmt = select(ItemModel).order_by(ItemModel.importance_score.desc()).limit(10)
    res = await session.execute(stmt)
    items = list(res.scalars().all())

    roadmap_summary = roadmap_engine.get_summary()
    pinned_deps = parse_dependency_manifest(DEFAULT_MANIFEST)

    items_html = ""
    for it in items:
        badge_color = "#10b981" if it.priority == "MUST_KNOW" else ("#3b82f6" if it.priority == "SHOULD_KNOW" else "#f59e0b")
        items_html += f"""
        <div class="card item-card">
            <div class="item-header">
                <span class="badge" style="background-color: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color};">
                    {it.priority}
                </span>
                <span class="marker">{it.epistemic_marker}</span>
                <span class="time">{it.source_id.upper()}</span>
            </div>
            <h3 class="item-title">{it.title}</h3>
            <p class="item-why"><strong>Why you:</strong> {it.why_it_matters or 'Ecosystem development'}</p>
            {f'<p class="item-do"><strong>Action:</strong> {it.practical_action}</p>' if it.practical_action else ''}
            <div class="item-footer">
                <a href="{it.canonical_url}" target="_blank" class="source-link">View Source &rarr;</a>
            </div>
        </div>
        """

    deps_html = ""
    for d in pinned_deps:
        deps_html += f"""
        <div class="dep-pill">
            <span class="dep-name">{d.name}</span>
            <span class="dep-version">{d.version}</span>
            <span class="dep-status">HEALTHY</span>
        </div>
        """

    roadmap_html = ""
    for n in roadmap_summary["nodes"][:6]:
        status_color = "#10b981" if n["status"] == "completed" else ("#3b82f6" if n["status"] == "in_progress" else "#6b7280")
        roadmap_html += f"""
        <div class="roadmap-card">
            <div class="roadmap-header">
                <span class="track-tag">{n['track']}</span>
                <span class="status-dot" style="background: {status_color};"></span>
            </div>
            <h4>{n['title']}</h4>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: {int(n['theory_confidence']*100)}%;"></div>
            </div>
            <small>Theory: {int(n['theory_confidence']*100)}% | Practice: {int(n['practice_confidence']*100)}%</small>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentinel — AI Engineering Radar</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090d16;
            --surface: #111827;
            --surface-glass: rgba(17, 24, 39, 0.75);
            --border: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(99, 102, 241, 0.3);
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.2);
            --emerald: #10b981;
            --amber: #f59e0b;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
            min-height: 100vh;
            padding: 24px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        /* Top Navigation Header */
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 28px;
            background: var(--surface-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 24px;
        }}
        .brand {{ display: flex; align-items: center; gap: 14px; }}
        .brand-icon {{ font-size: 28px; }}
        .brand h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }}
        .brand p {{ font-size: 13px; color: var(--text-muted); }}
        
        .meta-badges {{ display: flex; gap: 12px; }}
        .stat-pill {{
            padding: 6px 14px;
            border-radius: 20px;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            font-size: 13px;
            font-weight: 500;
        }}
        .stat-pill.budget {{ border-color: var(--emerald); color: var(--emerald); background: rgba(16, 185, 129, 0.08); }}
        
        /* Main Grid */
        .grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
        }}
        @media (max-width: 1024px) {{ .grid {{ grid-template-columns: 1fr; }} }}

        .section-title {{
            font-size: 16px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Card Styles */
        .card {{
            background: var(--surface-glass);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
            transition: all 0.2s ease;
        }}
        .card:hover {{
            border-color: var(--border-hover);
            box-shadow: 0 4px 20px var(--accent-glow);
        }}

        /* Intelligence Feed Cards */
        .item-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
        }}
        .marker {{ font-size: 16px; }}
        .time {{ font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }}
        .item-title {{ font-size: 17px; font-weight: 600; margin-bottom: 8px; color: #fff; }}
        .item-why {{ font-size: 14px; color: #d1d5db; margin-bottom: 6px; }}
        .item-do {{ font-size: 13px; color: var(--emerald); margin-bottom: 12px; }}
        .source-link {{
            color: var(--accent);
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
        }}
        .source-link:hover {{ text-decoration: underline; }}

        /* Sidebar Panels */
        .sidebar-section {{ margin-bottom: 24px; }}
        
        /* Dependency Radar Pills */
        .dep-pill {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 14px;
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        }}
        .dep-name {{ font-weight: 600; color: #fff; }}
        .dep-version {{ color: var(--text-muted); }}
        .dep-status {{ font-size: 11px; color: var(--emerald); font-weight: 700; }}

        /* Roadmap Grid */
        .roadmap-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        .roadmap-card {{
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
        }}
        .roadmap-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
        .track-tag {{ font-size: 10px; font-weight: 700; background: var(--accent); color: #fff; padding: 2px 6px; border-radius: 4px; }}
        .status-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
        .roadmap-card h4 {{ font-size: 12px; font-weight: 600; margin-bottom: 8px; line-height: 1.3; }}
        .progress-bar-bg {{ width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-bottom: 4px; }}
        .progress-bar-fill {{ height: 100%; background: var(--emerald); border-radius: 2px; }}
        .roadmap-card small {{ font-size: 11px; color: var(--text-muted); }}

        /* Lab Launch Button */
        .lab-btn {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 8px;
        }}
        .lab-btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <span class="brand-icon">🧠</span>
                <div>
                    <h1>Sentinel AI Engineering Radar</h1>
                    <p>{profile.name} · {profile.role} at {profile.work_context.company_abstract}</p>
                </div>
            </div>
            <div class="meta-badges">
                <span class="stat-pill budget">$0.00 / ₹0 HARD BUDGET</span>
                <span class="stat-pill">{profile.hardware.get('local_gpu')}</span>
                <span class="stat-pill">IST 08:00 BRIEF</span>
            </div>
        </header>

        <div class="grid">
            <!-- Left Column: Verified Intelligence Feed -->
            <main>
                <div class="section-title">
                    <span>🔥</span>
                    <span>Verified Intelligence Feed & Daily Decisions</span>
                </div>
                {items_html if items_html else '<div class="card"><p>No items indexed yet. Trigger /internal/ingest to populate.</p></div>'}
            </main>

            <!-- Right Column: Radar Panels -->
            <aside>
                <!-- Dependency Impact Radar Panel -->
                <div class="sidebar-section">
                    <div class="section-title">
                        <span>🛡️</span>
                        <span>Dependency Impact Radar</span>
                    </div>
                    <div class="card">
                        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
                            Watching {len(pinned_deps)} pinned work packages for breaking changes & advisories:
                        </p>
                        {deps_html}
                    </div>
                </div>

                <!-- Living Roadmap Panel -->
                <div class="sidebar-section">
                    <div class="section-title">
                        <span>🗺️</span>
                        <span>Living Roadmap Progress ({roadmap_summary['progress_percent']}%)</span>
                    </div>
                    <div class="card">
                        <div class="roadmap-grid">
                            {roadmap_html}
                        </div>
                    </div>
                </div>

                <!-- Personal AI Lab Trigger Panel -->
                <div class="sidebar-section">
                    <div class="section-title">
                        <span>🧪</span>
                        <span>Personal AI Lab</span>
                    </div>
                    <div class="card">
                        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px;">
                            Generate immediately executable benchmarks calibrated for your <strong>{profile.hardware.get('local_gpu')}</strong>.
                        </p>
                        <button class="lab-btn" onclick="alert('Run `/lab awq` or `/lab vllm` in Telegram to receive the standalone benchmark code!')">
                            Launch Lab Script Generator
                        </button>
                    </div>
                </div>
            </aside>
        </div>
    </div>
</body>
</html>
"""
    return html
