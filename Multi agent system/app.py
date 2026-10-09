"""
NEXUS - Research Intelligence console (Streamlit UI for the multi-agent pipeline).

Run with:
    .\\.venv\\Scripts\\python.exe -m streamlit run app.py
"""

import html
import os
import re
import time
from urllib.parse import urlparse

import streamlit as st

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NEXUS · Research Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

AGENTS = [
    {"key": "search", "icon": "⌕", "name": "Search Agent", "role": "Scans the web for fresh, reliable sources"},
    {"key": "reader", "icon": "▤", "name": "Reader Agent", "role": "Opens the best source and extracts depth"},
    {"key": "writer", "icon": "✎", "name": "Writer", "role": "Synthesises a structured research report"},
    {"key": "critic", "icon": "◎", "name": "Critic", "role": "Scores the report and flags weak spots"},
]

SUGGESTIONS = [
    "What's happening in the tech industry this week",
    "Latest breakthroughs in AI agents",
    "Indian stock market outlook",
    "State of electric vehicles in 2026",
]


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #070A13;
  --panel: rgba(17, 22, 40, 0.72);
  --panel-solid: #0F1424;
  --line: rgba(148, 163, 255, 0.14);
  --line-strong: rgba(148, 163, 255, 0.28);
  --text: #E6E9F5;
  --muted: #8B93B5;
  --faint: #5B6388;
  --accent: #7C83FF;
  --accent-2: #22D3EE;
  --good: #34D399;
  --warn: #FBBF24;
  --bad: #F87171;
}

html, body, [class*="css"], .stMarkdown, button, input, textarea {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif !important;
}

/* ---------- App background ---------- */
.stApp {
  background:
    radial-gradient(900px 500px at 12% -10%, rgba(124, 131, 255, 0.22), transparent 60%),
    radial-gradient(700px 420px at 95% 5%, rgba(34, 211, 238, 0.12), transparent 60%),
    radial-gradient(800px 600px at 50% 120%, rgba(168, 85, 247, 0.10), transparent 60%),
    var(--bg);
}
.stApp::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    linear-gradient(rgba(148,163,255,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148,163,255,0.035) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: radial-gradient(ellipse at 50% 0%, black 30%, transparent 75%);
}
.block-container { padding-top: 1.4rem; padding-bottom: 4rem; max-width: 1180px; position: relative; z-index: 1; }

/* ---------- Hide default Streamlit chrome ---------- */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbarActions"],
.stDeployButton, [data-testid="stMainMenu"], [data-testid="InputInstructions"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; }

/* ---------- Top bar ---------- */
.topbar { display: flex; align-items: center; justify-content: space-between;
  padding: 10px 4px 22px 4px; border-bottom: 1px solid var(--line); margin-bottom: 38px; }
.brand { display: flex; align-items: center; gap: 12px; }
.logo { width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center;
  font-size: 18px; color: white; font-weight: 800;
  background: linear-gradient(135deg, #7C83FF 0%, #A855F7 50%, #22D3EE 100%);
  box-shadow: 0 8px 24px -6px rgba(124,131,255,.6), inset 0 1px 0 rgba(255,255,255,.35); }
.brand-name { font-weight: 800; letter-spacing: .18em; font-size: .95rem; color: var(--text); }
.brand-sub { font-family: 'JetBrains Mono', monospace; font-size: .68rem; color: var(--muted);
  letter-spacing: .12em; text-transform: uppercase; margin-top: 1px; }
.top-right { display: flex; gap: 10px; align-items: center; }
.badge { font-family: 'JetBrains Mono', monospace; font-size: .72rem; color: var(--muted);
  border: 1px solid var(--line); background: rgba(15,20,36,.6); padding: 6px 12px; border-radius: 999px;
  display: inline-flex; align-items: center; gap: 8px; }
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--good);
  box-shadow: 0 0 0 0 rgba(52,211,153,.6); animation: ping 2s infinite; }
@keyframes ping { 0% { box-shadow: 0 0 0 0 rgba(52,211,153,.55);} 70% { box-shadow: 0 0 0 8px rgba(52,211,153,0);} 100% { box-shadow: 0 0 0 0 rgba(52,211,153,0);} }

/* ---------- Hero ---------- */
.hero { text-align: center; margin: 6px auto 26px auto; max-width: 980px; }
.kicker { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: .72rem; letter-spacing: .2em;
  text-transform: uppercase; color: var(--accent); border: 1px solid var(--line-strong);
  background: rgba(124,131,255,.08); padding: 6px 14px; border-radius: 999px; margin-bottom: 18px; }
.hero h1 { font-size: 3.1rem; line-height: 1.06; font-weight: 800; letter-spacing: -0.03em; margin: 0; color: var(--text); }
.hero h1 .grad { background: linear-gradient(90deg, #A5B4FC 0%, #C084FC 45%, #67E8F9 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p { color: var(--muted); font-size: 1.05rem; margin-top: 14px; }

/* ---------- Command console (the form) ---------- */
[data-testid="stForm"] {
  background: linear-gradient(180deg, rgba(23,29,52,.85), rgba(14,18,33,.85));
  border: 1px solid var(--line-strong) !important; border-radius: 20px; padding: 14px 14px 6px 14px;
  box-shadow: 0 30px 80px -30px rgba(124,131,255,.45), inset 0 1px 0 rgba(255,255,255,.05);
  backdrop-filter: blur(14px); max-width: 880px; margin: 0 auto;
}
[data-testid="stForm"] [data-baseweb="input"] { background: transparent !important; border: none !important; }
[data-testid="stForm"] input { font-size: 1.08rem !important; color: var(--text) !important; padding: 14px 8px !important; }
[data-testid="stForm"] input::placeholder { color: var(--faint) !important; }
[data-testid="stTextInput"] > div > div { background: transparent !important; border: none !important; box-shadow: none !important; }

/* Buttons */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 12px !important; font-weight: 600 !important; border: 1px solid var(--line-strong) !important;
  background: rgba(23,29,52,.8) !important; color: var(--text) !important; transition: all .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--accent) !important; color: white !important;
  box-shadow: 0 0 0 3px rgba(124,131,255,.15); }
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 60%, #A855F7 100%) !important; border: none !important;
  height: 52px; color: white !important; box-shadow: 0 10px 30px -10px rgba(139,92,246,.8);
}
[data-testid="stFormSubmitButton"] > button:hover { filter: brightness(1.12); transform: translateY(-1px); }

/* Suggestion pills */
.try-label { text-align: center; font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: var(--faint);
  letter-spacing: .16em; text-transform: uppercase; margin: 18px 0 6px 0; }
[data-testid="stPills"], .stPills { display: flex; justify-content: center; }
[data-testid="stPills"] > div { justify-content: center; }
[data-testid="stPills"] button { border-radius: 999px !important; background: rgba(15,20,36,.7) !important;
  border: 1px solid var(--line) !important; color: var(--muted) !important; font-size: .83rem !important; }
[data-testid="stPills"] button:hover { color: var(--text) !important; border-color: var(--accent) !important; }

/* ---------- Section headings ---------- */
.section { display: flex; align-items: center; gap: 12px; margin: 46px 0 16px 0; }
.section .label { font-family: 'JetBrains Mono', monospace; font-size: .74rem; letter-spacing: .2em;
  text-transform: uppercase; color: var(--muted); white-space: nowrap; }
.section .rule { height: 1px; flex: 1; background: linear-gradient(90deg, var(--line-strong), transparent); }
.section .meta { font-family: 'JetBrains Mono', monospace; font-size: .72rem; color: var(--faint); }

/* ---------- Agent cards ---------- */
.agent { position: relative; overflow: hidden; border-radius: 18px; padding: 18px 18px 16px 18px; min-height: 168px;
  background: var(--panel); border: 1px solid var(--line); backdrop-filter: blur(10px); transition: all .25s ease; }
.agent .row { display: flex; justify-content: space-between; align-items: center; }
.agent .ico { width: 40px; height: 40px; border-radius: 12px; display: grid; place-items: center; font-size: 19px;
  background: rgba(124,131,255,.10); border: 1px solid var(--line); color: #A5B4FC; }
.agent .idx { font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: var(--faint); letter-spacing: .12em; }
.agent .name { font-weight: 700; font-size: 1rem; margin-top: 14px; color: var(--text); }
.agent .role { font-size: .82rem; color: var(--muted); margin-top: 4px; line-height: 1.4; }
.agent .state { margin-top: 14px; font-family: 'JetBrains Mono', monospace; font-size: .72rem; letter-spacing: .08em;
  text-transform: uppercase; color: var(--faint); display: flex; align-items: center; gap: 8px; }
.agent .state .sd { width: 7px; height: 7px; border-radius: 50%; background: var(--faint); }
.agent .bar { position: absolute; left: 0; bottom: 0; height: 2px; width: 100%; background: transparent; }

.agent.running { border-color: rgba(124,131,255,.6); box-shadow: 0 0 0 1px rgba(124,131,255,.25), 0 20px 50px -20px rgba(124,131,255,.7); }
.agent.running .ico { background: rgba(124,131,255,.22); color: white; }
.agent.running .state { color: #A5B4FC; }
.agent.running .state .sd { background: var(--accent); animation: blink 1s infinite; }
.agent.running .bar { background: linear-gradient(90deg, transparent, #7C83FF, #22D3EE, transparent);
  background-size: 200% 100%; animation: sweep 1.4s linear infinite; }
@keyframes blink { 50% { opacity: .25; } }
@keyframes sweep { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

.agent.done { border-color: rgba(52,211,153,.35); }
.agent.done .ico { background: rgba(52,211,153,.12); color: var(--good); border-color: rgba(52,211,153,.3); }
.agent.done .state { color: var(--good); }
.agent.done .state .sd { background: var(--good); }
.agent.done .bar { background: linear-gradient(90deg, rgba(52,211,153,.0), rgba(52,211,153,.7), rgba(52,211,153,.0)); }

.agent.error { border-color: rgba(248,113,113,.45); }
.agent.error .state { color: var(--bad); }
.agent.error .state .sd { background: var(--bad); }

/* ---------- Notices ---------- */
.notice { border-radius: 14px; padding: 14px 18px; margin-top: 14px; font-size: .92rem;
  border: 1px solid rgba(251,191,36,.35); background: rgba(251,191,36,.08); color: #FDE68A; }
.notice.err { border-color: rgba(248,113,113,.4); background: rgba(248,113,113,.08); color: #FECACA; }
.notice b { color: white; }

/* ---------- Stat tiles ---------- */
.tile { border-radius: 18px; padding: 18px 20px; background: var(--panel); border: 1px solid var(--line);
  min-height: 118px; display: flex; align-items: center; gap: 16px; }
.tile .t-label { font-family: 'JetBrains Mono', monospace; font-size: .68rem; letter-spacing: .16em; text-transform: uppercase; color: var(--faint); }
.tile .t-value { font-size: 1.9rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; line-height: 1.1; margin-top: 4px; }
.tile .t-sub { font-size: .8rem; color: var(--muted); margin-top: 2px; }
.ring { --p: 0; width: 72px; height: 72px; border-radius: 50%; flex-shrink: 0; display: grid; place-items: center;
  background: conic-gradient(var(--ring-color, var(--accent)) calc(var(--p) * 1%), rgba(148,163,255,.1) 0); }
.ring > div { width: 58px; height: 58px; border-radius: 50%; background: var(--panel-solid); display: grid; place-items: center;
  font-weight: 800; font-size: 1.15rem; color: var(--text); }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { background: transparent; border-radius: 10px 10px 0 0; padding: 10px 16px;
  color: var(--muted); font-weight: 600; }
.stTabs [aria-selected="true"] { color: white !important; background: rgba(124,131,255,.12) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: linear-gradient(90deg, #7C83FF, #22D3EE) !important; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- Report panel ---------- */
.st-key-report_panel, .st-key-critic_panel, .st-key-raw_panel {
  background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 30px 36px !important; margin-top: 10px;
}
.st-key-report_panel h1, .st-key-report_panel h2, .st-key-report_panel h3,
.st-key-critic_panel h1, .st-key-critic_panel h2, .st-key-critic_panel h3 { color: white; letter-spacing: -0.01em; }
.st-key-report_panel h2, .st-key-report_panel h3 { border-bottom: 1px solid var(--line); padding-bottom: 6px; margin-top: 1.2em; }
.st-key-report_panel p, .st-key-report_panel li { color: #C9CEE4; line-height: 1.75; font-size: 1rem; }
.st-key-report_panel a { color: #A5B4FC; }
.st-key-report_panel strong { color: white; }

/* ---------- Source cards ---------- */
.src { display: flex; gap: 14px; align-items: center; padding: 14px 16px; border-radius: 14px; margin-bottom: 10px;
  background: var(--panel); border: 1px solid var(--line); text-decoration: none !important; transition: all .18s ease; }
.src:hover { border-color: var(--accent); transform: translateX(3px); }
.src .fav { width: 36px; height: 36px; border-radius: 10px; display: grid; place-items: center; flex-shrink: 0;
  background: rgba(124,131,255,.12); color: #A5B4FC; font-weight: 800; font-size: .95rem; text-transform: uppercase; }
.src .dom { color: white; font-weight: 600; font-size: .92rem; }
.src .u { color: var(--faint); font-family: 'JetBrains Mono', monospace; font-size: .74rem; word-break: break-all; margin-top: 2px; }
.src .arrow { margin-left: auto; color: var(--faint); }

/* ---------- Empty state ---------- */
.empty { text-align: center; padding: 56px 20px; border: 1px dashed var(--line-strong); border-radius: 20px;
  background: rgba(15,20,36,.35); }
.empty .big { font-size: 2.2rem; opacity: .5; }
.empty .h { color: var(--text); font-weight: 700; margin-top: 10px; }
.empty .s { color: var(--muted); font-size: .9rem; margin-top: 4px; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] { background: #0A0E1A; border-right: 1px solid var(--line); }
.side-title { font-family: 'JetBrains Mono', monospace; font-size: .7rem; letter-spacing: .18em; text-transform: uppercase;
  color: var(--faint); margin: 8px 0 12px 0; }
section[data-testid="stSidebar"] .stButton > button { width: 100%; text-align: left; justify-content: flex-start;
  background: transparent !important; border: 1px solid var(--line) !important; font-weight: 500 !important; }

/* ---------- Footer ---------- */
.foot { text-align: center; margin-top: 60px; font-family: 'JetBrains Mono', monospace; font-size: .7rem;
  color: var(--faint); letter-spacing: .14em; text-transform: uppercase; }

/* Expanders */
[data-testid="stExpander"] { border: 1px solid var(--line) !important; border-radius: 14px !important; background: rgba(15,20,36,.5); }

@media (max-width: 900px) {
  .hero h1 { font-size: 2.2rem; }
  .topbar .badge.model { display: none; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def to_text(output) -> str:
    if isinstance(output, str):
        return output
    if hasattr(output, "content"):
        return output.content
    return str(output)


def is_rate_limit(err: Exception) -> bool:
    msg = str(err).lower()
    return "429" in msg or "rate limit" in msg or "rate_limited" in msg


def invoke_with_retry(fn, step_name: str, notice, max_attempts: int = 5):
    """Call fn(); if the API returns 429, wait and retry with growing delays."""
    delay = 10
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as e:
            if not is_rate_limit(e) or attempt == max_attempts:
                raise
            for remaining in range(delay, 0, -1):
                notice.markdown(
                    f'<div class="notice">⏳ <b>{html.escape(step_name)}</b> hit the API rate limit — '
                    f'retrying in <b>{remaining}s</b> (attempt {attempt + 1}/{max_attempts})</div>',
                    unsafe_allow_html=True,
                )
                time.sleep(1)
            notice.empty()
            delay *= 2


def agent_card(placeholder, idx: int, agent: dict, state: str = "idle", detail: str = ""):
    labels = {"idle": "Standby", "running": "Working", "done": "Complete", "error": "Failed"}
    text = labels.get(state, state) + (f" · {detail}" if detail else "")
    placeholder.markdown(
        f'<div class="agent {state}"><div class="row"><div class="ico">{agent["icon"]}</div>'
        f'<div class="idx">0{idx}</div></div>'
        f'<div class="name">{agent["name"]}</div><div class="role">{agent["role"]}</div>'
        f'<div class="state"><span class="sd"></span>{html.escape(text)}</div><div class="bar"></div></div>',
        unsafe_allow_html=True,
    )


def section(label: str, meta: str = ""):
    meta_html = f'<span class="meta">{html.escape(meta)}</span>' if meta else ""
    st.markdown(
        f'<div class="section"><span class="label">{html.escape(label)}</span>'
        f'<span class="rule"></span>{meta_html}</div>',
        unsafe_allow_html=True,
    )


def parse_score(feedback: str):
    m = re.search(r"score\s*[:\-]?\s*\**\s*(\d+(?:\.\d+)?)\s*/\s*10", feedback, re.IGNORECASE)
    return float(m.group(1)) if m else None


def extract_urls(*texts):
    seen, urls = set(), []
    for t in texts:
        for u in re.findall(r"https?://[^\s\)\]\"'<>|]+", t or ""):
            u = u.rstrip(".,;:*")
            if u not in seen:
                seen.add(u)
                urls.append(u)
    return urls


def tile(label: str, value: str, sub: str = "", ring_pct=None, ring_color=None):
    ring = ""
    if ring_pct is not None:
        color = f"--ring-color:{ring_color};" if ring_color else ""
        ring = f'<div class="ring" style="--p:{ring_pct};{color}"><div>{value}</div></div>'
        value_html = ""
    else:
        value_html = f'<div class="t-value">{value}</div>'
    st.markdown(
        f'<div class="tile">{ring}<div><div class="t-label">{html.escape(label)}</div>'
        f'{value_html}<div class="t-sub">{html.escape(sub)}</div></div></div>',
        unsafe_allow_html=True,
    )


def use_suggestion():
    choice = st.session_state.get("suggest")
    if choice:
        st.session_state.topic_input = choice
    st.session_state.suggest = None


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
for key, default in {"result": None, "topic": "", "history": [], "timings": {}, "topic_input": ""}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# Top bar + hero
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="topbar"><div class="brand"><div class="logo">◆</div><div>'
    '<div class="brand-name">NEXUS</div><div class="brand-sub">Research Intelligence</div></div></div>'
    '<div class="top-right">'
    f'<span class="badge model">MODEL · {html.escape(MODEL_NAME)}</span>'
    '<span class="badge"><span class="dot"></span>4 AGENTS ONLINE</span>'
    '</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><div class="kicker">Autonomous multi-agent research</div>'
    '<h1>Ask anything.<br><span class="grad">Four agents take it from there.</span></h1>'
    '<p>Search, read, write and critique — a full research report in about a minute.</p></div>',
    unsafe_allow_html=True,
)

with st.form("console", border=False):
    c1, c2 = st.columns([5, 1.1], vertical_alignment="center")
    with c1:
        st.text_input(
            "Research topic",
            key="topic_input",
            placeholder="What should the agents investigate?",
            label_visibility="collapsed",
        )
    with c2:
        submitted = st.form_submit_button("Launch  ↗", width="stretch")

st.markdown('<div class="try-label">— or try —</div>', unsafe_allow_html=True)
st.pills("Suggestions", SUGGESTIONS, selection_mode="single", key="suggest",
         on_change=use_suggestion, label_visibility="collapsed")


# ---------------------------------------------------------------------------
# Agent pipeline
# ---------------------------------------------------------------------------
section("Agent pipeline", "search → read → write → critique")
cols = st.columns(4, gap="small")
slots = [col.empty() for col in cols]
for i, (slot, agent) in enumerate(zip(slots, AGENTS), 1):
    t = st.session_state.timings.get(agent["key"])
    agent_card(slot, i, agent, "done" if t is not None else "idle", f"{t:.1f}s" if t is not None else "")

notice = st.empty()


def run_pipeline(topic: str) -> dict:
    state, timings = {}, {}
    for i, (slot, agent) in enumerate(zip(slots, AGENTS), 1):
        agent_card(slot, i, agent, "idle")

    def step(idx, fn):
        agent = AGENTS[idx]
        agent_card(slots[idx], idx + 1, agent, "running")
        t0 = time.time()
        try:
            out = invoke_with_retry(fn, agent["name"], notice)
        except Exception:
            agent_card(slots[idx], idx + 1, agent, "error")
            raise
        timings[agent["key"]] = time.time() - t0
        agent_card(slots[idx], idx + 1, agent, "done", f"{timings[agent['key']]:.1f}s")
        return out

    search_agent = build_search_agent()
    res = step(0, lambda: search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    }))
    state["search_results"] = to_text(res["messages"][-1])

    reader_agent = build_reader_agent()
    res = step(1, lambda: reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    }))
    state["scraped_content"] = to_text(res["messages"][-1])

    research_combined = (
        f"Search results:\n {state['search_results']}\n\n"
        f"Detailed scraped content:\n{state['scraped_content']}"
    )
    state["report"] = to_text(step(2, lambda: writer_chain.invoke({
        "topic": topic, "research": research_combined,
    })))

    state["feedback"] = to_text(step(3, lambda: critic_chain.invoke({"report": state["report"]})))

    state["timings"] = timings
    return state


if submitted:
    topic = st.session_state.topic_input.strip()
    if not topic:
        notice.markdown('<div class="notice">Type a topic first — or pick one of the suggestions.</div>',
                        unsafe_allow_html=True)
    else:
        try:
            result = run_pipeline(topic)
            st.session_state.result = result
            st.session_state.topic = topic
            st.session_state.timings = result["timings"]
            st.session_state.history.append((topic, result))
        except Exception as e:
            if is_rate_limit(e):
                msg = ("<b>The API kept rejecting requests (rate limit)</b> even after several retries. "
                       "Wait a few minutes and launch again.")
            else:
                msg = f"<b>Pipeline failed.</b> {html.escape(str(e))[:400]}"
            notice.markdown(f'<div class="notice err">{msg}</div>', unsafe_allow_html=True)
            with st.expander("Technical details"):
                st.exception(e)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
result = st.session_state.result
section("Intelligence brief", st.session_state.topic if result else "")

if not result:
    st.markdown(
        '<div class="empty"><div class="big">◇</div><div class="h">No brief yet</div>'
        '<div class="s">Launch a topic above — your report, critic score and sources will appear here.</div></div>',
        unsafe_allow_html=True,
    )
else:
    score = parse_score(result["feedback"])
    words = len(result["report"].split())
    sources = extract_urls(result["search_results"], result["scraped_content"], result["report"])
    total_time = sum(result.get("timings", {}).values())

    t1, t2, t3, t4 = st.columns(4, gap="small")
    with t1:
        if score is not None:
            color = "#34D399" if score >= 8 else "#FBBF24" if score >= 6 else "#F87171"
            verdict = "Strong" if score >= 8 else "Decent" if score >= 6 else "Needs work"
            tile("Critic score", f"{score:g}", f"{verdict} · out of 10", ring_pct=score * 10, ring_color=color)
        else:
            tile("Critic score", "—", "not found in feedback")
    with t2:
        tile("Report length", f"{words:,}", f"words · ~{max(1, round(words / 220))} min read")
    with t3:
        tile("Sources", str(len(sources)), "links discovered")
    with t4:
        tile("Runtime", f"{total_time:.0f}s", "end-to-end")

    st.write("")
    tab_report, tab_critic, tab_sources, tab_raw = st.tabs(
        ["Report", "Critic review", f"Sources ({len(sources)})", "Raw research"]
    )

    with tab_report:
        with st.container(key="report_panel"):
            st.markdown(result["report"])
        d1, d2, _ = st.columns([1, 1, 2])
        safe = re.sub(r"[^A-Za-z0-9]+", "_", st.session_state.topic)[:40].strip("_") or "report"
        with d1:
            st.download_button("↓  Report (.md)", data=result["report"],
                               file_name=f"{safe}_report.md", mime="text/markdown", width="stretch")
        with d2:
            full = (f"# Research: {st.session_state.topic}\n\n## Final Report\n\n{result['report']}\n\n"
                    f"## Critic Feedback\n\n{result['feedback']}\n\n## Search Results\n\n{result['search_results']}\n\n"
                    f"## Scraped Content\n\n{result['scraped_content']}\n")
            st.download_button("↓  Full bundle (.md)", data=full,
                               file_name=f"{safe}_full.md", mime="text/markdown", width="stretch")

    with tab_critic:
        with st.container(key="critic_panel"):
            st.markdown(result["feedback"])

    with tab_sources:
        if sources:
            cards = []
            for u in sources:
                dom = urlparse(u).netloc.replace("www.", "") or u
                cards.append(
                    f'<a class="src" href="{html.escape(u)}" target="_blank" rel="noopener">'
                    f'<div class="fav">{html.escape(dom[:1])}</div>'
                    f'<div><div class="dom">{html.escape(dom)}</div><div class="u">{html.escape(u[:110])}</div></div>'
                    f'<div class="arrow">↗</div></a>'
                )
            st.markdown("".join(cards), unsafe_allow_html=True)
        else:
            st.caption("No links found in this run.")

    with tab_raw:
        with st.expander("Search agent output", expanded=False):
            st.markdown(result["search_results"])
        with st.expander("Reader agent output (scraped content)", expanded=False):
            st.markdown(result["scraped_content"])

st.markdown('<div class="foot">NEXUS · LangChain · Groq · Tavily</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar - session history
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand" style="margin-bottom:22px"><div class="logo">◆</div><div>'
                '<div class="brand-name">NEXUS</div><div class="brand-sub">Session</div></div></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="side-title">Recent briefs</div>', unsafe_allow_html=True)
    if st.session_state.history:
        for i, (past_topic, past_result) in enumerate(reversed(st.session_state.history)):
            if st.button(f"◇  {past_topic[:34]}", key=f"hist_{i}"):
                st.session_state.topic = past_topic
                st.session_state.result = past_result
                st.session_state.timings = past_result.get("timings", {})
                st.rerun()
        st.write("")
        if st.button("Clear history", key="clear_hist"):
            st.session_state.history = []
            st.session_state.result = None
            st.session_state.timings = {}
            st.rerun()
    else:
        st.caption("Your briefs from this session will appear here.")
