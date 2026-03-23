#!/usr/bin/env python3
"""
autoeval/view_results.py — Generate and open a visualisation dashboard.

Reads results.tsv and scores/*.json, writes dashboard.html, opens in browser.
Run anytime: python autoeval/view_results.py
"""

import csv
import glob
import json
import os
import webbrowser

BASE         = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(BASE, "results.tsv")
SCORES_DIR   = os.path.join(BASE, "scores")
DASHBOARD    = os.path.join(BASE, "dashboard.html")

MAX_SCORE    = 4410  # 9 plans × 49 requirements × 10 pts
MAX_PER_TEST = {     # 9 plans × req_count × 10
    "test_1": 360, "test_2": 360, "test_3": 450, "test_4": 360,
    "test_5": 360, "test_6": 360, "test_7": 360, "test_8": 450,
    "test_9": 450, "test_10": 450, "test_11": 450,
}
TEST_LABELS = {
    "test_1":  "T1: Legibility",
    "test_2":  "T2: Tone",
    "test_3":  "T3: Linear Flow",
    "test_4":  "T4: Ordering",
    "test_5":  "T5: Deliverables",
    "test_6":  "T6: Commit Conds",
    "test_7":  "T7: Actionability",
    "test_8":  "T8: Example I/O",
    "test_9":  "T9: Granularity",
    "test_10": "T10: Dependencies",
    "test_11": "T11: Retrieval",
}


def load_results() -> list[dict]:
    if not os.path.exists(RESULTS_FILE):
        return []
    rows = []
    with open(RESULTS_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def load_latest_score_data() -> dict | None:
    files = sorted(glob.glob(os.path.join(SCORES_DIR, "iter*.json")))
    if not files:
        return None
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def compute_per_test_pcts(score_data: dict) -> dict[str, float]:
    """Return percentage score per test for latest iteration."""
    totals: dict[str, int] = {k: 0 for k in MAX_PER_TEST}
    num_plans = sum(1 for k in score_data if k.startswith("plan_"))
    for plan_key in [f"plan_{i}" for i in range(1, num_plans + 1)]:
        plan_scores = score_data.get(plan_key, {})
        for test_key in MAX_PER_TEST:
            test_scores = plan_scores.get(test_key, {})
            if isinstance(test_scores, dict):
                totals[test_key] += sum(int(v) for v in test_scores.values())
    return {
        k: round(100 * totals[k] / MAX_PER_TEST[k], 1)
        for k in MAX_PER_TEST
    }


def generate_html(rows: list[dict], latest_score_data: dict | None) -> str:
    # ── data for charts ────────────────────────────────────────────────────────
    iterations   = [r["iteration"] for r in rows]
    scores       = [int(r["score"]) for r in rows]
    champ_scores = [int(r["champion_score"]) for r in rows]
    statuses     = [r.get("status", "") for r in rows]
    analyses     = [r.get("analysis", "")[:120] for r in rows]
    timestamps   = [r.get("timestamp", "")[:16] for r in rows]

    latest_score = scores[-1] if scores else 0
    latest_pct   = round(100 * latest_score / MAX_SCORE, 1)
    champion     = max(champ_scores) if champ_scores else 0
    champ_pct    = round(100 * champion / MAX_SCORE, 1)

    per_test_pcts: dict[str, float] = {}
    if latest_score_data:
        per_test_pcts = compute_per_test_pcts(latest_score_data)

    bar_labels = json.dumps([TEST_LABELS[k] for k in MAX_PER_TEST])
    bar_data   = json.dumps([per_test_pcts.get(k, 0) for k in MAX_PER_TEST])
    bar_colors = json.dumps([
        "#22c55e" if per_test_pcts.get(k, 0) >= 80
        else "#f59e0b" if per_test_pcts.get(k, 0) >= 50
        else "#ef4444"
        for k in MAX_PER_TEST
    ])

    trend_labels = json.dumps(iterations)
    trend_scores = json.dumps(scores)
    trend_champs = json.dumps(champ_scores)

    # Table rows
    table_rows = ""
    for i, r in enumerate(reversed(rows)):
        status = r.get("status", "")
        badge_cls = (
            "badge-keep" if status == "keep"
            else "badge-baseline" if status == "baseline"
            else "badge-discard"
        )
        score_val  = int(r.get("score", 0))
        score_pct  = round(100 * score_val / MAX_SCORE, 1)
        analysis   = r.get("analysis", "").replace("'", "&#39;").replace('"', "&quot;")
        brief      = r.get("brief", "")
        ts         = r.get("timestamp", "")[:16]
        iteration  = r["iteration"]
        champ_val  = r.get("champion_score", "")
        row_id     = f"detail-{i}"

        table_rows += f"""
        <tr class="data-row" onclick="toggleDetail('{row_id}')">
          <td class="iter-cell">#{iteration}</td>
          <td class="ts-cell">{ts}</td>
          <td class="score-cell">
            <span class="score-num">{score_val}</span>
            <span class="score-pct">{score_pct}%</span>
            <div class="row-bar"><div class="row-bar-fill" style="width:{score_pct}%"></div></div>
          </td>
          <td class="champ-val">{champ_val}</td>
          <td><span class="badge {badge_cls}">{status}</span></td>
          <td class="brief-cell">{brief}</td>
          <td class="expand-cell"><span class="expand-icon">▸</span> <span class="preview-text">{r.get('analysis','')[:60]}…</span></td>
        </tr>
        <tr class="detail-row" id="{row_id}">
          <td colspan="7">
            <div class="analysis-panel">
              <div class="analysis-label">Analysis</div>
              <div class="analysis-body">{r.get('analysis','')}</div>
            </div>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phase-Compiler Autoeval Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f172a; color: #e2e8f0; min-height: 100vh; padding: 24px; }}
  h1   {{ font-size: 1.5rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }}
  .sub {{ color: #94a3b8; font-size: 0.875rem; margin-bottom: 28px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
           gap: 16px; margin-bottom: 28px; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 20px; }}
  .card-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
                 color: #64748b; margin-bottom: 6px; }}
  .card-value {{ font-size: 2rem; font-weight: 700; color: #f8fafc; }}
  .card-sub   {{ font-size: 0.8rem; color: #64748b; margin-top: 2px; }}
  .progress-bar {{ background: #334155; border-radius: 99px; height: 8px; margin-top: 10px; }}
  .progress-fill {{ background: linear-gradient(90deg, #6366f1, #22c55e);
                    border-radius: 99px; height: 100%; transition: width 0.6s ease; }}
  .chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 28px; }}
  .chart-card {{ background: #1e293b; border-radius: 12px; padding: 20px; }}
  .chart-title {{ font-size: 0.875rem; font-weight: 600; color: #cbd5e1; margin-bottom: 16px; }}
  table {{ width: 100%; border-collapse: collapse; background: #1e293b;
           border-radius: 12px; overflow: hidden; }}
  th {{ background: #0a0f1e; padding: 10px 16px; text-align: left;
        font-size: 0.68rem; text-transform: uppercase; color: #475569;
        letter-spacing: 0.08em; font-family: 'SF Mono', 'Fira Code', monospace; }}
  td {{ padding: 12px 16px; font-size: 0.8125rem; border-top: 1px solid #1e293b; }}
  .data-row {{ cursor: pointer; transition: background 0.15s; }}
  .data-row:hover {{ background: #243044; }}
  .data-row.open {{ background: #1a2540; }}
  .iter-cell {{ font-family: 'SF Mono', 'Fira Code', monospace; color: #475569; font-size: 0.75rem; width: 48px; }}
  .ts-cell   {{ color: #64748b; font-size: 0.75rem; font-family: 'SF Mono', 'Fira Code', monospace; white-space: nowrap; }}
  .score-cell {{ width: 160px; }}
  .score-num  {{ font-weight: 700; color: #a5b4fc; font-size: 0.9rem; margin-right: 6px; }}
  .score-pct  {{ color: #64748b; font-size: 0.7rem; }}
  .row-bar    {{ background: #0f172a; border-radius: 3px; height: 3px; margin-top: 5px; }}
  .row-bar-fill {{ background: linear-gradient(90deg, #6366f1, #22c55e); border-radius: 3px; height: 100%; }}
  .champ-val  {{ color: #64748b; font-size: 0.8rem; }}
  .brief-cell {{ color: #94a3b8; font-size: 0.75rem; font-family: 'SF Mono', 'Fira Code', monospace; }}
  .expand-cell {{ color: #475569; font-size: 0.75rem; }}
  .expand-icon {{ display: inline-block; transition: transform 0.2s; color: #6366f1; margin-right: 4px; }}
  .data-row.open .expand-icon {{ transform: rotate(90deg); }}
  .preview-text {{ color: #64748b; font-style: italic; }}
  .detail-row {{ display: none; }}
  .detail-row.open {{ display: table-row; }}
  .detail-row td {{ padding: 0; border-top: none; }}
  .analysis-panel {{ background: #0a0f1e; border-left: 2px solid #6366f1;
                     margin: 0 16px 12px; border-radius: 0 6px 6px 0; padding: 14px 18px;
                     animation: slideDown 0.2s ease; }}
  @keyframes slideDown {{ from {{ opacity: 0; transform: translateY(-6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  .analysis-label {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em;
                     color: #6366f1; font-family: 'SF Mono', 'Fira Code', monospace;
                     margin-bottom: 8px; }}
  .analysis-body {{ color: #cbd5e1; font-size: 0.825rem; line-height: 1.65;
                    white-space: pre-wrap; word-break: break-word; }}
  .badge {{ display: inline-block; padding: 3px 9px; border-radius: 4px;
            font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.06em; font-family: 'SF Mono', 'Fira Code', monospace; }}
  .badge-keep     {{ background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }}
  .badge-discard  {{ background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }}
  .badge-baseline {{ background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.25); }}
  @media (max-width: 768px) {{ .chart-row {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<h1>Phase-Compiler Autoeval</h1>
<p class="sub">Self-improving skill loop · 9 plans (3×brief) × 49 requirements × 10 pts = 4410 max</p>

<div class="grid">
  <div class="card">
    <div class="card-label">Latest Score</div>
    <div class="card-value">{latest_score}</div>
    <div class="card-sub">{latest_pct}% of {MAX_SCORE}</div>
    <div class="progress-bar"><div class="progress-fill" style="width:{latest_pct}%"></div></div>
  </div>
  <div class="card">
    <div class="card-label">Champion Score</div>
    <div class="card-value">{champion}</div>
    <div class="card-sub">{champ_pct}% of {MAX_SCORE}</div>
    <div class="progress-bar"><div class="progress-fill" style="width:{champ_pct}%"></div></div>
  </div>
  <div class="card">
    <div class="card-label">Iterations Run</div>
    <div class="card-value">{len(rows)}</div>
    <div class="card-sub">including baseline</div>
  </div>
  <div class="card">
    <div class="card-label">Improvements</div>
    <div class="card-value">{sum(1 for r in rows if r.get('status') == 'keep')}</div>
    <div class="card-sub">prompt versions kept</div>
  </div>
</div>

<div class="chart-row">
  <div class="chart-card">
    <div class="chart-title">Score over iterations</div>
    <canvas id="trendChart" height="200"></canvas>
  </div>
  <div class="chart-card">
    <div class="chart-title">Latest iteration — per-test breakdown (%)</div>
    <canvas id="barChart" height="200"></canvas>
  </div>
</div>

<div class="chart-card" style="margin-bottom:28px">
  <div class="chart-title">All iterations</div>
  <div style="overflow-x:auto">
  <table>
    <thead>
      <tr>
        <th>#</th><th>Timestamp</th><th>Score</th><th>Champion</th>
        <th>Status</th><th>Brief</th><th>Analysis — click row to expand</th>
      </tr>
    </thead>
    <tbody>{table_rows}</tbody>
  </table>
  </div>
</div>

<script>
const trendCtx = document.getElementById('trendChart').getContext('2d');
new Chart(trendCtx, {{
  type: 'line',
  data: {{
    labels: {trend_labels},
    datasets: [
      {{
        label: 'Score',
        data: {trend_scores},
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99,102,241,0.1)',
        tension: 0.3,
        fill: true,
        pointRadius: 4,
      }},
      {{
        label: 'Champion',
        data: {trend_champs},
        borderColor: '#22c55e',
        borderDash: [6, 3],
        tension: 0.3,
        fill: false,
        pointRadius: 0,
      }},
    ]
  }},
  options: {{
    responsive: true,
    scales: {{
      y: {{ min: 0, max: {MAX_SCORE}, grid: {{ color: '#334155' }},
            ticks: {{ color: '#94a3b8' }} }},
      x: {{ grid: {{ color: '#334155' }}, ticks: {{ color: '#94a3b8' }} }}
    }},
    plugins: {{ legend: {{ labels: {{ color: '#cbd5e1' }} }} }}
  }}
}});

const barCtx = document.getElementById('barChart').getContext('2d');
new Chart(barCtx, {{
  type: 'bar',
  data: {{
    labels: {bar_labels},
    datasets: [{{
      label: '% score',
      data: {bar_data},
      backgroundColor: {bar_colors},
      borderRadius: 4,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    scales: {{
      x: {{ min: 0, max: 100, grid: {{ color: '#334155' }},
            ticks: {{ color: '#94a3b8', callback: v => v + '%' }} }},
      y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }} }}
    }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});
</script>
<script>
function toggleDetail(id) {{
  const detail = document.getElementById(id);
  const dataRow = detail.previousElementSibling;
  const isOpen = detail.classList.contains('open');
  detail.classList.toggle('open', !isOpen);
  dataRow.classList.toggle('open', !isOpen);
}}
</script>
</body>
</html>"""


def main() -> None:
    rows = load_results()
    if not rows:
        print("No results yet. Run score_baseline.py first, then run.py.")
        return

    latest_score_data = load_latest_score_data()
    html = generate_html(rows, latest_score_data)

    with open(DASHBOARD, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard written to: {DASHBOARD}")
    webbrowser.open(f"file://{DASHBOARD}")


if __name__ == "__main__":
    main()
