"""
PhaseCompiler — Modal Web App
Two-agent system: Planner (coder) + Analyzer (reviewer) with debate loop.
"""
import os
import re
import modal

app = modal.App("phase-compiler")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("anthropic>=0.43.0", "fastapi[standard]>=0.115.0", "python-multipart")
    .add_local_file("SKILL.md", "/app/SKILL.md")
)

# ---------------------------------------------------------------------------
# HTML — embedded at module level (static, no runtime reads needed)
# ---------------------------------------------------------------------------
FORM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PhaseCompiler</title>
<style>
  :root {
    --bg: #0f0f11;
    --surface: #1a1a1f;
    --surface2: #242430;
    --border: #2e2e3a;
    --accent: #7c6af5;
    --accent2: #a78bfa;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --success: #34d399;
    --warn: #fbbf24;
    --error: #f87171;
    --radius: 10px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 2rem 1rem;
  }
  .container { max-width: 860px; margin: 0 auto; }
  header { text-align: center; margin-bottom: 2.5rem; }
  header h1 { font-size: 2rem; font-weight: 700; color: var(--accent2); letter-spacing: -0.5px; }
  header p { color: var(--muted); margin-top: 0.5rem; font-size: 0.95rem; }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.75rem;
    margin-bottom: 1.25rem;
  }
  .card h2 {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
  }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  @media (max-width: 600px) { .grid-2 { grid-template-columns: 1fr; } }
  .field { margin-bottom: 1rem; }
  .field:last-child { margin-bottom: 0; }
  label {
    display: block;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text);
    margin-bottom: 0.4rem;
  }
  label .req { color: var(--accent); margin-left: 2px; }
  label .hint {
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--muted);
    margin-left: 0.5rem;
  }
  input[type=text], input[type=number], input[type=password], select, textarea {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-size: 0.9rem;
    font-family: inherit;
    padding: 0.6rem 0.8rem;
    outline: none;
    transition: border-color 0.15s;
  }
  input:focus, select:focus, textarea:focus { border-color: var(--accent); }
  input::placeholder, textarea::placeholder { color: #6b6b80 !important; opacity: 1; }
  input::-webkit-input-placeholder, textarea::-webkit-input-placeholder { color: #6b6b80 !important; opacity: 1; }
  input::-moz-placeholder, textarea::-moz-placeholder { color: #6b6b80 !important; opacity: 1; }
  .prefilled { color: #6b6b80 !important; }
  select option { background: var(--surface2); }
  textarea { resize: vertical; min-height: 80px; }
  details { margin-bottom: 1.25rem; }
  details .card { margin-bottom: 0; }
  summary {
    cursor: pointer;
    user-select: none;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--muted);
    padding: 0.6rem 0;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  summary::before { content: "▶"; font-size: 0.65rem; transition: transform 0.2s; }
  details[open] summary::before { transform: rotate(90deg); }
  .submit-row { text-align: center; margin-top: 1.5rem; }
  .btn {
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.9rem 2.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, transform 0.1s;
  }
  .btn:hover { background: var(--accent2); }
  .btn:active { transform: scale(0.98); }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-sm {
    padding: 0.5rem 1.25rem;
    font-size: 0.85rem;
    border-radius: 6px;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    cursor: pointer;
    font-weight: 500;
    transition: border-color 0.15s;
  }
  .btn-sm:hover { border-color: var(--accent); }

  /* Loading overlay */
  #loading {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15,15,17,0.92);
    backdrop-filter: blur(6px);
    z-index: 100;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    text-align: center;
    padding: 2rem;
  }
  .spinner {
    width: 48px; height: 48px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  #loadingTitle { font-size: 1.2rem; font-weight: 600; color: var(--accent2); }
  #statusMsg { color: var(--muted); font-size: 0.9rem; max-width: 420px; }
  #debateLog { max-width: 480px; width: 100%; }
  .debate-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    margin-top: 0.5rem;
    font-size: 0.82rem;
    color: var(--muted);
    text-align: left;
  }
  .debate-item.approved { border-color: var(--success); color: var(--success); }
  .debate-item.rejected { border-color: var(--warn); color: var(--warn); }

  /* Results */
  #results { display: none; }
  .results-header { text-align: center; margin-bottom: 2rem; }
  .results-header h2 { font-size: 1.5rem; color: var(--accent2); }
  .results-header p { color: var(--muted); font-size: 0.9rem; margin-top: 0.4rem; }
  .phase-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
  }
  .phase-card:hover { border-color: #3a3a4a; }
  .phase-num {
    position: absolute;
    top: -12px;
    left: 1.25rem;
    background: var(--accent);
    color: #fff;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 100px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .phase-card h3 { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.75rem; padding-top: 0.25rem; }
  .phase-section { margin-bottom: 0.85rem; }
  .phase-section:last-child { margin-bottom: 0; }
  .phase-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--muted);
    margin-bottom: 0.3rem;
  }
  .phase-value { font-size: 0.88rem; color: var(--text); line-height: 1.5; }
  .task-list { list-style: none; }
  .task-list li {
    padding: 0.3rem 0;
    font-size: 0.88rem;
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
  }
  .task-list li::before { content: "☐"; color: var(--accent); flex-shrink: 0; }
  .commit-badge {
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 6px;
    padding: 0.4rem 0.7rem;
    font-size: 0.82rem;
    color: var(--success);
  }
  .io-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  @media (max-width: 600px) { .io-grid { grid-template-columns: 1fr; } }
  .io-box {
    background: var(--surface2);
    border-radius: 6px;
    padding: 0.6rem 0.8rem;
    font-size: 0.82rem;
    color: var(--muted);
  }
  .io-box strong { display: block; color: var(--text); margin-bottom: 0.3rem; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .meta-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
  }
  .meta-chip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 0.3rem 0.9rem;
    font-size: 0.8rem;
    color: var(--muted);
  }
  .meta-chip span { color: var(--text); font-weight: 500; }
  .json-section { margin-top: 1.5rem; }
  .json-toggle {
    cursor: pointer;
    font-size: 0.85rem;
    color: var(--muted);
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    user-select: none;
    margin-bottom: 0.75rem;
  }
  .json-toggle:hover { color: var(--text); }
  pre {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    overflow-x: auto;
    font-size: 0.78rem;
    line-height: 1.6;
    color: var(--text);
    display: none;
  }
  pre.shown { display: block; }
  .action-row { display: flex; gap: 0.75rem; margin-top: 1rem; justify-content: center; flex-wrap: wrap; }
  .error-card {
    background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: var(--radius);
    padding: 1.25rem;
    color: var(--error);
    margin-bottom: 1.25rem;
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>⚙️ PhaseCompiler</h1>
    <p>Turn a project idea into a dependency-ordered, phase-by-phase execution roadmap</p>
  </header>

  <form id="planForm">

    <!-- API Key -->
    <div class="card">
      <h2>Anthropic API Key</h2>
      <div class="field">
        <label for="api_key">API Key <span class="req">*</span> <span class="hint">Used only for this request, never stored</span></label>
        <input type="password" id="api_key" name="api_key" placeholder="sk-ant-..." required>
      </div>
    </div>

    <!-- Required fields -->
    <div class="card">
      <h2>Project Details <span style="color:var(--muted);font-weight:400;text-transform:none;font-size:0.85rem">(required)</span></h2>

      <div class="field">
        <label for="name">Project Name <span class="req">*</span></label>
        <input type="text" id="name" name="name" placeholder="e.g. TaskTracker CLI" maxlength="50" value="TaskFlow" class="prefilled" required>
      </div>

      <div class="field">
        <label for="description">Description <span class="req">*</span> <span class="hint">What does it do? Max 1000 chars</span></label>
        <textarea id="description" name="description" placeholder="A CLI tool for managing personal tasks with priorities, tags, and due dates." maxlength="1000" rows="3" class="prefilled" required>A CLI tool for managing personal tasks. Tasks have a title, optional due date, and priority (low/medium/high). Everything persists to a local JSON file between sessions.</textarea>
      </div>

      <div class="field">
        <label for="done">Definition of Done <span class="req">*</span> <span class="hint">One condition per line</span></label>
        <textarea id="done" name="done" placeholder="Users can create, list, complete and delete tasks&#10;Tasks persist between sessions&#10;Filters by tag and due date work correctly" rows="3" class="prefilled" required>Users can add, list, complete, and delete tasks from the terminal
Tasks persist between sessions via a local JSON file
Tasks can be filtered by priority</textarea>
      </div>

      <div class="field">
        <label for="mvp">MVP Features <span class="req">*</span> <span class="hint">Core features only — one per line</span></label>
        <textarea id="mvp" name="mvp" placeholder="Add / list / complete / delete tasks&#10;Task persistence via JSON file&#10;Due date and priority support" rows="3" class="prefilled" required>Add, list, complete, and delete tasks
Persist tasks to a JSON file</textarea>
      </div>

      <div class="grid-2">
        <div class="field">
          <label for="language">Language <span class="req">*</span></label>
          <input type="text" id="language" name="language" value="python" placeholder="python, typescript, rust…" class="prefilled" required>
        </div>
        <div class="field">
          <label for="main_user">Main User <span class="req">*</span></label>
          <input type="text" id="main_user" name="main_user" value="Just Myself" placeholder="Myself, small team…" class="prefilled" required>
        </div>
      </div>

      <div class="grid-2">
        <div class="field">
          <label for="runtime">Runtime <span class="req">*</span></label>
          <select id="runtime" name="runtime">
            <option value="cli" selected>CLI</option>
            <option value="web">Web</option>
            <option value="mobile">Mobile</option>
            <option value="desktop">Desktop</option>
            <option value="library">Library / SDK</option>
          </select>
        </div>
        <div class="field">
          <label for="starting_point">Starting Point <span class="req">*</span></label>
          <select id="starting_point" name="starting_point">
            <option value="nothing" selected>Nothing (from scratch)</option>
            <option value="existing">Existing codebase</option>
            <option value="prototype">Prototype</option>
            <option value="mvp">MVP already done</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label for="phase_count">Number of Phases <span class="req">*</span> <span class="hint">6–12</span></label>
        <input type="number" id="phase_count" name="phase_count" value="6" min="6" max="12" required>
      </div>
    </div>

    <!-- Optional fields -->
    <details>
      <summary>Optional Settings</summary>
      <div class="card" style="margin-top:0.5rem">

        <div class="grid-2">
          <div class="field">
            <label for="architecture">Architecture</label>
            <select id="architecture" name="architecture">
              <option value="other" selected>Other / Not sure</option>
              <option value="microservices">Microservices</option>
              <option value="event_driven">Event-driven</option>
              <option value="serverless">Serverless</option>
            </select>
          </div>
          <div class="field">
            <label for="scaling_strategy">Scaling Strategy</label>
            <select id="scaling_strategy" name="scaling_strategy">
              <option value="none" selected>None</option>
              <option value="vertical">Vertical</option>
              <option value="horizontal">Horizontal</option>
              <option value="serverless">Serverless</option>
              <option value="auto">Auto-scaling</option>
            </select>
          </div>
        </div>

        <div class="field">
          <label for="expected_scale">Expected Scale <span class="hint">e.g. "single user", "10k DAU"</span></label>
          <input type="text" id="expected_scale" name="expected_scale" placeholder="Single user, local only">
        </div>

        <div class="field">
          <label for="architecture_notes">Architecture Notes <span class="hint">Frameworks, patterns, extra context</span></label>
          <textarea id="architecture_notes" name="architecture_notes" placeholder="Using FastAPI + SQLite, deployed on a single VPS…" rows="2"></textarea>
        </div>

        <div class="field">
          <label for="constraints">Constraints <span class="hint">One per line — budget, time, team, technical limits</span></label>
          <textarea id="constraints" name="constraints" placeholder="Solo developer&#10;1-week timeline&#10;No external APIs" rows="2"></textarea>
        </div>

        <div class="field">
          <label for="avoid">Avoid <span class="hint">One per line — tools, patterns, practices to skip</span></label>
          <textarea id="avoid" name="avoid" placeholder="Docker&#10;ORM frameworks&#10;TypeScript" rows="2"></textarea>
        </div>

      </div>
    </details>

    <!-- Human-action cost tips -->
    <details style="margin-bottom:1.25rem">
      <summary style="color:var(--accent2)">💡 Tips to reduce costs further</summary>
      <div style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:1.1rem 1.25rem;margin-top:0.5rem;font-size:0.85rem;line-height:1.7">
        <p style="color:var(--muted);font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.75rem">These require your action — the app cannot do them automatically</p>
        <ul style="list-style:none;display:flex;flex-direction:column;gap:0.5rem">
          <li>📝 <strong>Be specific in descriptions.</strong> Vague text forces Claude to ask more questions or make assumptions, inflating output. "A FastAPI backend with JWT auth and PostgreSQL" costs less than "a backend app".</li>
          <li>🔢 <strong>Use fewer phases for simpler projects.</strong> Each phase = more output tokens. Use 6–7 for small projects, 10–12 only for complex ones.</li>
          <li>✂️ <strong>Trim the MVP list.</strong> The planner includes every MVP feature in every relevant phase. Fewer MVP items → shorter plan → fewer tokens.</li>
          <li>🔁 <strong>Avoid debate rounds.</strong> If the Analyzer rejects the plan, both agents run again. Write clear "done" conditions and specific descriptions to get approval in round 1.</li>
          <li>🌐 <strong>Leave optional fields blank if unused.</strong> Architecture notes, constraints, and avoid lists all add to the input prompt. Skip them if you don't need them.</li>
        </ul>
        <p style="margin-top:0.9rem;font-size:0.78rem;color:var(--muted)">Already handled automatically: <span style="color:var(--text)">prompt caching on system prompts</span> (saves ~90% on repeat calls), <span style="color:var(--text)">cheapest model (Haiku 4.5)</span>, and <span style="color:var(--text)">reduced max_tokens</span> for the analyzer (1024 vs 16000).</p>
      </div>
    </details>

    <div class="submit-row">
      <div style="margin-bottom:1rem">
        <button type="button" class="btn-sm" id="estimateBtn">📊 Estimate tokens first</button>
        <div id="estimateResult" style="display:none;margin-top:0.75rem;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:0.9rem 1.1rem;font-size:0.88rem;text-align:left;max-width:420px;margin-left:auto;margin-right:auto"></div>
      </div>
      <button type="submit" class="btn" id="submitBtn">Generate Roadmap →</button>
    </div>
  </form>

  <!-- Loading overlay -->
  <div id="loading">
    <div class="spinner"></div>
    <div id="loadingTitle">Agents at work…</div>
    <div id="statusMsg">Initialising</div>
    <div id="debateLog"></div>
  </div>

  <!-- Results -->
  <div id="results"></div>
</div>

<script>
const form = document.getElementById('planForm');
document.querySelectorAll('.prefilled').forEach(el => {
  el.addEventListener('input', () => el.classList.remove('prefilled'), { once: true });
});
const loading = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const statusMsg = document.getElementById('statusMsg');
const debateLog = document.getElementById('debateLog');
const submitBtn = document.getElementById('submitBtn');

function showLoading() {
  form.style.display = 'none';
  loading.style.display = 'flex';
  resultsDiv.style.display = 'none';
}

function addDebateItem(text, cls) {
  const d = document.createElement('div');
  d.className = 'debate-item ' + (cls || '');
  d.textContent = text;
  debateLog.appendChild(d);
}

function renderResults(data) {
  loading.style.display = 'none';
  resultsDiv.style.display = 'block';

  const plan = data.plan;
  const proj = plan.project || {};
  const phases = plan.phases || [];
  const rounds = data.rounds || 1;
  const log = data.debate_log || [];
  const tu = data.token_usage || {};

  let html = '<div class="results-header">';
  html += '<h2>✅ ' + escHtml(proj.name || 'Your Roadmap') + '</h2>';
  html += '<p>' + escHtml(proj.description || '') + '</p>';
  html += '</div>';

  html += '<div class="meta-row">';
  html += '<div class="meta-chip">Language: <span>' + escHtml(proj.language || '—') + '</span></div>';
  html += '<div class="meta-chip">Runtime: <span>' + escHtml(proj.runtime || '—') + '</span></div>';
  html += '<div class="meta-chip">Phases: <span>' + phases.length + '</span></div>';
  const agentRounds = rounds === 1 ? '1 (approved first try ✨)' : rounds + ' rounds of debate';
  html += '<div class="meta-chip">Agent rounds: <span>' + agentRounds + '</span></div>';
  html += '</div>';

  // Token usage card
  if (tu.input_tokens !== undefined) {
    const inp = tu.input_tokens;
    const out = tu.output_tokens;
    const est = tu.estimated_input;
    const fmt = n => n.toLocaleString();
    const cacheRead = tu.cache_read_input_tokens || 0;
    const cacheWrite = tu.cache_creation_input_tokens || 0;
    const inpCost = (inp / 1e6 * 1).toFixed(5);
    const outCost = (out / 1e6 * 5).toFixed(5);
    const cacheWriteCost = (cacheWrite / 1e6 * 1.25).toFixed(5);
    const cacheReadCost = (cacheRead / 1e6 * 0.1).toFixed(5);
    const totalCost = ((inp / 1e6 * 1) + (out / 1e6 * 5) + (cacheWrite / 1e6 * 1.25) + (cacheRead / 1e6 * 0.1)).toFixed(5);
    const savedVsNoCaching = cacheRead > 0 ? ((cacheRead / 1e6) * (1 - 0.1)).toFixed(5) : null;
    html += '<div class="card" style="margin-bottom:1.25rem">';
    html += '<h2>💰 Token Usage  <span style="font-weight:400;color:var(--muted);text-transform:none;font-size:0.8rem">(Haiku 4.5 · $1/1M input · $5/1M output · cache read $0.10/1M)</span></h2>';
    html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-bottom:0.75rem">';
    html += '<div class="io-box"><strong>Input tokens</strong>' + fmt(inp) + '<br><span style="color:var(--success);font-size:0.78rem">$' + inpCost + '</span></div>';
    html += '<div class="io-box"><strong>Output tokens</strong>' + fmt(out) + '<br><span style="color:var(--success);font-size:0.78rem">$' + outCost + '</span></div>';
    html += '<div class="io-box"><strong>Total cost</strong><span style="font-size:1.1rem;font-weight:600;color:var(--accent2)">$' + totalCost + '</span></div>';
    html += '</div>';
    if (cacheRead > 0 || cacheWrite > 0) {
      html += '<div style="font-size:0.78rem;color:var(--muted);margin-top:0.4rem;display:flex;gap:1rem;flex-wrap:wrap">';
      if (cacheWrite > 0) html += '<span>Cache written: <span style="color:var(--text)">' + fmt(cacheWrite) + ' tokens</span> ($' + cacheWriteCost + ')</span>';
      if (cacheRead > 0)  html += '<span>Cache read: <span style="color:var(--text)">' + fmt(cacheRead) + ' tokens</span> ($' + cacheReadCost + ')</span>';
      if (savedVsNoCaching) html += '<span style="color:var(--success)">💾 Saved ~$' + savedVsNoCaching + ' vs no caching</span>';
      html += '</div>';
    }
    if (est) {
      const accuracy = Math.round(Math.abs(inp - est) / est * 100);
      html += '<div style="font-size:0.78rem;color:var(--muted);margin-top:0.3rem">Pre-flight estimate: <span style="color:var(--text)">' + fmt(est) + ' input tokens</span> · actual was ' + accuracy + '% off</div>';
    }
    html += '</div>';
  }

  phases.forEach(function(p) {
    html += '<div class="phase-card">';
    html += '<div class="phase-num">Phase ' + p.id + '</div>';
    html += '<h3>' + escHtml(p.title) + '</h3>';

    html += '<div class="phase-section"><div class="phase-label">Deliverable</div>';
    html += '<div class="phase-value">' + escHtml(p.deliverable) + '</div></div>';

    html += '<div class="phase-section"><div class="phase-label">Tasks</div>';
    html += '<ul class="task-list">';
    (p.tasks || []).forEach(function(t) {
      html += '<li>' + escHtml(t) + '</li>';
    });
    html += '</ul></div>';

    html += '<div class="phase-section"><div class="phase-label">Commit Condition</div>';
    html += '<div class="commit-badge">' + escHtml(p.commit_condition) + '</div></div>';

    html += '<div class="phase-section"><div class="phase-label">Example I/O</div>';
    html += '<div class="io-grid">';
    html += '<div class="io-box"><strong>Input</strong>' + escHtml(p.example_input) + '</div>';
    html += '<div class="io-box"><strong>Output</strong>' + escHtml(p.example_output) + '</div>';
    html += '</div></div>';

    html += '</div>';
  });

  // Debate log
  if (log.length > 1) {
    html += '<div class="card" style="margin-top:0.5rem"><h2>Agent Debate Log</h2>';
    log.forEach(function(r) {
      const cls = r.approved ? 'commit-badge' : 'error-card';
      const icon = r.approved ? '✅' : '🔄';
      html += '<div style="margin-bottom:0.75rem;font-size:0.85rem">';
      html += '<strong>Round ' + r.round + ':</strong> ' + icon + ' ' + (r.approved ? 'Approved' : 'Needs revision');
      if (!r.approved && r.feedback) {
        html += '<div style="color:var(--muted);margin-top:0.3rem;font-size:0.8rem">' + escHtml(r.feedback.substring(0, 300)) + (r.feedback.length > 300 ? '…' : '') + '</div>';
      }
      html += '</div>';
    });
    html += '</div>';
  }

  // JSON section
  html += '<div class="json-section">';
  html += '<div class="json-toggle" onclick="toggleJson()">▶ Show raw JSON</div>';
  html += '<pre id="jsonPre">' + escHtml(JSON.stringify(plan, null, 2)) + '</pre>';
  html += '</div>';

  html += '<div class="action-row">';
  html += '<button class="btn-sm" onclick="downloadJson()">⬇ Download plan.json</button>';
  html += '<button class="btn-sm" onclick="startOver()">← Plan another project</button>';
  html += '</div>';

  resultsDiv.innerHTML = html;
  window._planData = plan;
}

function escHtml(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function toggleJson() {
  const pre = document.getElementById('jsonPre');
  const tog = document.querySelector('.json-toggle');
  if (pre.classList.toggle('shown')) {
    tog.textContent = '▼ Hide raw JSON';
  } else {
    tog.textContent = '▶ Show raw JSON';
  }
}

function downloadJson() {
  const blob = new Blob([JSON.stringify(window._planData, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'plan.json';
  a.click();
}

function startOver() {
  resultsDiv.style.display = 'none';
  debateLog.innerHTML = '';
  form.style.display = 'block';
  submitBtn.disabled = false;
}

document.getElementById('estimateBtn').addEventListener('click', async function() {
  const btn = this;
  const box = document.getElementById('estimateResult');
  const apiKey = document.getElementById('api_key').value.trim();
  if (!apiKey) { box.style.display='block'; box.innerHTML='<span style="color:var(--error)">Enter your API key first.</span>'; return; }
  btn.disabled = true;
  btn.textContent = '⏳ Counting tokens…';
  box.style.display = 'none';
  try {
    const resp = await fetch('/estimate', { method: 'POST', body: new FormData(form) });
    const data = await resp.json();
    if (data.error) { box.innerHTML = '<span style="color:var(--error)">' + escHtml(data.error) + '</span>'; }
    else {
      const inp = data.input_tokens;
      const inpCost = (inp / 1e6 * 1).toFixed(5);
      // Output is unknown pre-flight; give a rough range based on phase_count
      const phases = parseInt(document.getElementById('phase_count').value) || 7;
      const estOut = phases * 600;
      const outCost = (estOut / 1e6 * 5).toFixed(5);
      const totalLow = (inp / 1e6 * 1 + estOut / 1e6 * 5).toFixed(5);
      box.innerHTML =
        '<div style="color:var(--muted);font-size:0.75rem;margin-bottom:0.5rem">ESTIMATED COST — Round 1 (Haiku 4.5 · $1/1M in · $5/1M out)</div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem">' +
        '<div><div style="color:var(--muted);font-size:0.72rem">Input tokens</div><div style="font-weight:600">' + inp.toLocaleString() + '</div><div style="color:var(--success);font-size:0.8rem">$' + inpCost + '</div></div>' +
        '<div><div style="color:var(--muted);font-size:0.72rem">Output (est.)</div><div style="font-weight:600">~' + estOut.toLocaleString() + '</div><div style="color:var(--success);font-size:0.8rem">~$' + outCost + '</div></div>' +
        '<div><div style="color:var(--muted);font-size:0.72rem">Total est.</div><div style="font-weight:600;color:var(--accent2)">~$' + totalLow + '</div><div style="font-size:0.72rem;color:var(--muted)">per round</div></div>' +
        '</div>' +
        '<div style="font-size:0.75rem;color:var(--success);margin-top:0.5rem">💾 Prompt caching enabled — debate rounds 2+ are ~90% cheaper on input</div>';
    }
    box.style.display = 'block';
  } catch(e) {
    box.innerHTML = '<span style="color:var(--error)">Request failed: ' + escHtml(e.message) + '</span>';
    box.style.display = 'block';
  }
  btn.disabled = false;
  btn.textContent = '📊 Estimate tokens first';
});

form.addEventListener('submit', async function(e) {
  e.preventDefault();
  submitBtn.disabled = true;
  showLoading();
  statusMsg.textContent = 'Connecting to agents…';
  debateLog.innerHTML = '';

  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      body: new FormData(form)
    });

    if (!resp.ok) {
      const txt = await resp.text();
      throw new Error('Server error ' + resp.status + ': ' + txt);
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream: true});
      const lines = buffer.split('\\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === 'status') {
            statusMsg.textContent = data.msg;
          } else if (data.type === 'debate') {
            addDebateItem(data.msg, data.approved ? 'approved' : 'rejected');
          } else if (data.type === 'result') {
            renderResults(data);
          } else if (data.type === 'error') {
            loading.style.display = 'none';
            form.style.display = 'block';
            resultsDiv.innerHTML = '<div class="error-card"><strong>Error:</strong> ' + escHtml(data.msg) + '</div>';
            resultsDiv.style.display = 'block';
            submitBtn.disabled = false;
          }
        } catch(pe) {}
      }
    }
  } catch(err) {
    loading.style.display = 'none';
    form.style.display = 'block';
    resultsDiv.innerHTML = '<div class="error-card"><strong>Request failed:</strong> ' + escHtml(err.message) + '</div>';
    resultsDiv.style.display = 'block';
    submitBtn.disabled = false;
  }
});
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Modal function
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    timeout=600,
    min_containers=1,
)
@modal.asgi_app()
def web():
    import os
    import json
    import re
    import asyncio
    import anthropic
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, StreamingResponse

    fast_app = FastAPI(title="PhaseCompiler")

    with open("/app/SKILL.md") as f:
        SKILL_MD = f.read()

    # ------------------------------------------------------------------
    # Agent system prompts
    # ------------------------------------------------------------------

    PLANNER_SYS = """You are the Planner Agent in a two-agent PhaseCompiler system.

Your role: Generate a complete, structured project execution plan based on the user's specification.

You must follow the PhaseCompiler skill specification below EXACTLY:

---
""" + SKILL_MD + """
---

CRITICAL OUTPUT RULES:
- Output ONLY raw JSON. No markdown code fences, no explanations, no preamble.
- The JSON must have a "project" key (with project metadata) and a "phases" key (array of phases).
- Each phase must have: id (int), title (string), deliverable (string), tasks (array of strings),
  commit_condition (string), example_input (string), example_output (string).
- tasks must have exactly 3-5 items.
- The phase count must match the requested phase_count exactly.
- No "TBD" stubs. Every field must be specific and actionable."""

    ANALYZER_SYS = """You are the Analyzer Agent in a two-agent PhaseCompiler system.

Your role: Critically review a generated project plan and determine if it meets quality standards.

Evaluate strictly for:
1. Sequential dependencies — each phase must build on the previous one
2. Concrete deliverables — must be tangible (working code, tests, docs), not vague
3. Actionable tasks — 3-5 per phase, specific steps
4. Testable commit conditions — must be objectively verifiable
5. MVP checkpoint — core MVP must be delivered before scaling/optimisations appear
6. No placeholder stubs — no "TBD" or generic filler text
7. Phase count — must match the requested count
8. Specificity — phases must be project-specific, not generic templates

If the plan is high quality, respond with:
{"approved": true, "feedback": ""}

If the plan has issues that must be fixed, respond with:
{"approved": false, "feedback": "Specific issues found:\\n1. ...\\n2. ..."}

Respond with ONLY valid JSON. No markdown, no preamble."""

    # ------------------------------------------------------------------
    # Agent functions (synchronous — run in thread)
    # ------------------------------------------------------------------

    def _planner_prompt(spec: dict, feedback: str = "") -> str:
        prompt = f"Generate a PhaseCompiler plan for this project:\n\n{json.dumps(spec, indent=2)}"
        if feedback:
            prompt += (
                f"\n\nThe Analyzer Agent reviewed your previous plan and found issues. "
                f"You MUST fix ALL of them:\n{feedback}"
            )
        return prompt

    # Cache-annotated system prompt blocks — Haiku charges $1/1M input;
    # prompt caching writes at 1.25x but reads at 0.1x, saving ~90% on
    # repeated planner/analyzer calls (e.g. debate rounds 2+).
    PLANNER_SYS_CACHED = [{"type": "text", "text": PLANNER_SYS, "cache_control": {"type": "ephemeral"}}]
    ANALYZER_SYS_CACHED = [{"type": "text", "text": ANALYZER_SYS, "cache_control": {"type": "ephemeral"}}]

    MODEL = "claude-haiku-4-5"

    def _extract_json(raw: str) -> dict:
        """Find the first balanced {...} in raw text and parse it as JSON.
        Handles any leading prose or trailing text the model adds."""
        start = raw.find('{')
        if start == -1:
            raise ValueError(f"No JSON object found in model output. Got: {raw[:400]!r}")
        depth = 0
        for i, ch in enumerate(raw[start:], start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return json.loads(raw[start:i + 1])
        raise ValueError(f"Unclosed JSON in model output. Got: {raw[:400]!r}")

    def count_planner_tokens(api_key: str, spec: dict) -> int:
        """Pre-flight estimate: how many input tokens will the planner consume?"""
        client = anthropic.Anthropic(api_key=api_key)
        result = client.messages.count_tokens(
            model=MODEL,
            system=PLANNER_SYS_CACHED,
            messages=[{"role": "user", "content": _planner_prompt(spec)}],
        )
        return result.input_tokens

    def run_planner(api_key: str, spec: dict, feedback: str = "") -> tuple:
        """Returns (plan_dict, usage_dict).
        Prefills the assistant with '{' so the model must start its response
        as a JSON object, then uses _extract_json to handle any trailing text."""
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model=MODEL,
            max_tokens=16000,
            system=PLANNER_SYS_CACHED,
            messages=[
                {"role": "user", "content": _planner_prompt(spec, feedback)},
                {"role": "assistant", "content": "{"},  # prefill
            ],
        ) as stream:
            response = stream.get_final_message()

        text_block = next((b for b in response.content if b.type == "text"), None)
        if not text_block:
            raise ValueError("Model returned no text block")
        raw = "{" + text_block.text  # reattach the prefilled '{'
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
        }
        return _extract_json(raw), usage

    def run_analyzer(api_key: str, plan: dict, spec: dict) -> tuple:
        """Returns (review_dict, usage_dict)."""
        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            f"Review this PhaseCompiler plan against the original requirements.\n\n"
            f"Original requirements:\n{json.dumps(spec, indent=2)}\n\n"
            f"Generated plan:\n{json.dumps(plan, indent=2)}"
        )
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=ANALYZER_SYS_CACHED,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "{"},  # prefill
            ],
        )
        text_block = next((b for b in response.content if b.type == "text"), None)
        if not text_block:
            raise ValueError("Model returned no text block")
        raw = "{" + text_block.text
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
        }
        return _extract_json(raw), usage

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @fast_app.get("/")
    async def index():
        return HTMLResponse(FORM_HTML)

    @fast_app.post("/estimate")
    async def estimate(request: Request):
        from fastapi.responses import JSONResponse
        form_data = await request.form()
        api_key = str(form_data.get("api_key", "")).strip()
        if not api_key:
            return JSONResponse({"error": "Missing API key"}, status_code=400)

        def parse_lines(val: str) -> list:
            return [l.strip() for l in str(val).splitlines() if l.strip()]

        spec = {
            "name": str(form_data.get("name", "")).strip(),
            "description": str(form_data.get("description", "")).strip(),
            "done": parse_lines(str(form_data.get("done", ""))),
            "main_user": str(form_data.get("main_user", "Just Myself")).strip() or "Just Myself",
            "language": str(form_data.get("language", "python")).strip() or "python",
            "runtime": str(form_data.get("runtime", "cli")),
            "phase_count": int(str(form_data.get("phase_count", "7")) or "7"),
            "starting_point": str(form_data.get("starting_point", "nothing")),
            "mvp": parse_lines(str(form_data.get("mvp", ""))),
        }

        try:
            tokens = await asyncio.to_thread(count_planner_tokens, api_key, spec)
            return JSONResponse({"input_tokens": tokens})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @fast_app.post("/generate")
    async def generate(request: Request):
        form_data = await request.form()

        api_key = str(form_data.get("api_key", "")).strip()
        if not api_key:
            return HTMLResponse("Missing API key", status_code=400)

        def parse_lines(val: str) -> list:
            return [l.strip() for l in str(val).splitlines() if l.strip()]

        spec = {
            "name": str(form_data.get("name", "")).strip(),
            "description": str(form_data.get("description", "")).strip(),
            "done": parse_lines(str(form_data.get("done", ""))),
            "main_user": str(form_data.get("main_user", "Just Myself")).strip() or "Just Myself",
            "language": str(form_data.get("language", "python")).strip() or "python",
            "runtime": str(form_data.get("runtime", "cli")),
            "phase_count": int(str(form_data.get("phase_count", "7")) or "7"),
            "starting_point": str(form_data.get("starting_point", "nothing")),
            "mvp": parse_lines(str(form_data.get("mvp", ""))),
            "architecture": str(form_data.get("architecture", "other")),
            "scaling_strategy": str(form_data.get("scaling_strategy", "none")),
            "constraints": parse_lines(str(form_data.get("constraints", ""))),
            "architecture_notes": str(form_data.get("architecture_notes", "")).strip(),
            "expected_scale": str(form_data.get("expected_scale", "")).strip(),
            "avoid": parse_lines(str(form_data.get("avoid", ""))),
        }

        async def event_stream():
            try:
                total_input = 0
                total_output = 0
                total_cache_read = 0
                total_cache_write = 0

                # Pre-flight token estimate for the planner call
                estimated = await asyncio.to_thread(count_planner_tokens, api_key, spec)
                yield f"data: {json.dumps({'type': 'status', 'msg': f'📊 Estimated input tokens: ~{estimated:,} — generating roadmap…'})}\n\n"

                # Round 1: Planner generates the initial plan
                yield f"data: {json.dumps({'type': 'status', 'msg': '🤔 Planner agent is designing your roadmap…'})}\n\n"
                plan, p_usage = await asyncio.to_thread(run_planner, api_key, spec, "")
                total_input += p_usage["input_tokens"]
                total_output += p_usage["output_tokens"]
                total_cache_read += p_usage["cache_read_input_tokens"]
                total_cache_write += p_usage["cache_creation_input_tokens"]

                # Round 1: Analyzer reviews
                yield f"data: {json.dumps({'type': 'status', 'msg': '🔍 Analyzer agent is reviewing the plan…'})}\n\n"
                review, a_usage = await asyncio.to_thread(run_analyzer, api_key, plan, spec)
                total_input += a_usage["input_tokens"]
                total_output += a_usage["output_tokens"]
                total_cache_read += a_usage["cache_read_input_tokens"]
                total_cache_write += a_usage["cache_creation_input_tokens"]

                rounds = 1
                debate_log = [{
                    "round": rounds,
                    "approved": review["approved"],
                    "feedback": review.get("feedback", ""),
                }]

                # Debate loop (max 3 rounds total)
                while not review["approved"] and rounds < 3:
                    feedback = review.get("feedback", "")
                    rounds += 1
                    yield f"data: {json.dumps({'type': 'debate', 'msg': f'⚖️ Agents debating — Planner revising (round {rounds})…', 'approved': False})}\n\n"
                    plan, p_usage = await asyncio.to_thread(run_planner, api_key, spec, feedback)
                    total_input += p_usage["input_tokens"]
                    total_output += p_usage["output_tokens"]
                    total_cache_read += p_usage["cache_read_input_tokens"]
                    total_cache_write += p_usage["cache_creation_input_tokens"]

                    yield f"data: {json.dumps({'type': 'status', 'msg': f'🔍 Analyzer reviewing revision {rounds - 1}…'})}\n\n"
                    review, a_usage = await asyncio.to_thread(run_analyzer, api_key, plan, spec)
                    total_input += a_usage["input_tokens"]
                    total_output += a_usage["output_tokens"]
                    total_cache_read += a_usage["cache_read_input_tokens"]
                    total_cache_write += a_usage["cache_creation_input_tokens"]
                    debate_log.append({
                        "round": rounds,
                        "approved": review["approved"],
                        "feedback": review.get("feedback", ""),
                    })

                if review["approved"]:
                    yield f"data: {json.dumps({'type': 'debate', 'msg': f'✅ Plan approved after {rounds} round(s)', 'approved': True})}\n\n"

                token_usage = {
                    "input_tokens": total_input,
                    "output_tokens": total_output,
                    "cache_read_input_tokens": total_cache_read,
                    "cache_creation_input_tokens": total_cache_write,
                    "estimated_input": estimated,
                }
                yield f"data: {json.dumps({'type': 'result', 'plan': plan, 'rounds': rounds, 'debate_log': debate_log, 'token_usage': token_usage})}\n\n"

            except json.JSONDecodeError as e:
                yield f"data: {json.dumps({'type': 'error', 'msg': f'JSON parse error from model: {e}. Try again.'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'msg': str(e)})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return fast_app
