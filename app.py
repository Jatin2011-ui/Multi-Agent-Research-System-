import streamlit as st
import os
import json

# Page config
st.set_page_config(
    page_title="ResearchMind - Multi-Agent Research",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
    --bg:#0d0f14; --bg2:#13161e; --bg3:#1a1f2c; --border:#252b3b;
    --accent:#4f8ef7; --accent2:#7b5cf0; --green:#22c55e;
    --amber:#f59e0b; --red:#ef4444; --text:#e2e8f0; --muted:#64748b;
}
html,body,.stApp{background:var(--bg)!important;color:var(--text)!important;font-family:'Space Grotesk',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:2rem 2.5rem 4rem!important;max-width:1280px;}
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border);}
.stTextInput>div>div>input{background:var(--bg3)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text)!important;font-family:'Space Grotesk',sans-serif!important;font-size:0.95rem!important;}
.stTextInput>div>div>input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(79,142,247,0.18)!important;}
.stButton>button{background:linear-gradient(135deg,var(--accent),var(--accent2))!important;color:#fff!important;border:none!important;border-radius:8px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;font-size:0.95rem!important;padding:0.55rem 1.6rem!important;transition:opacity .2s,transform .1s!important;}
.stButton>button:hover{opacity:.88;transform:translateY(-1px);}
.stButton>button[disabled]{opacity:.45!important;cursor:not-allowed!important;}
.r-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:1rem;}
.r-card.accent-left{border-left:3px solid var(--accent);}
.r-card.green-left{border-left:3px solid var(--green);}
.r-card.amber-left{border-left:3px solid var(--amber);}
.r-card.purple-left{border-left:3px solid var(--accent2);}
.r-card.red-left{border-left:3px solid var(--red);}
.step-row{display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:1.2rem;}
.step-pill{display:inline-flex;align-items:center;gap:.4rem;padding:.28rem .85rem;border-radius:999px;font-size:.78rem;font-weight:600;letter-spacing:.04em;border:1px solid transparent;}
.step-pill.waiting{background:var(--bg3);border-color:var(--border);color:var(--muted);}
.step-pill.running{background:rgba(79,142,247,.12);border-color:var(--accent);color:var(--accent);}
.step-pill.done{background:rgba(34,197,94,.12);border-color:var(--green);color:var(--green);}
.step-pill.error{background:rgba(239,68,68,.12);border-color:var(--red);color:var(--red);}
.section-label{font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem;}
.content-box{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:1rem 1.2rem;font-size:.88rem;line-height:1.7;color:var(--text);white-space:pre-wrap;max-height:340px;overflow-y:auto;font-family:'JetBrains Mono',monospace;}
.report-box{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:1.2rem 1.4rem;font-size:.92rem;line-height:1.8;color:var(--text);white-space:pre-wrap;max-height:500px;overflow-y:auto;}
.log-box{background:#080a0f;border:1px solid var(--border);border-radius:8px;padding:1rem 1.2rem;font-size:.8rem;line-height:1.6;color:#94a3b8;white-space:pre-wrap;max-height:260px;overflow-y:auto;font-family:'JetBrains Mono',monospace;}
.hero{padding:1.6rem 0 1.2rem;}
.hero-title{font-size:2.1rem;font-weight:700;background:linear-gradient(120deg,var(--text) 0%,var(--accent) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.25rem;}
.hero-sub{font-size:.95rem;color:var(--muted);}
.stExpander{border:1px solid var(--border)!important;border-radius:8px!important;background:var(--bg2)!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg2);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px;}
</style>
""", unsafe_allow_html=True)

# Session state defaults
for k, v in {
    "running": False,
    "results": None,
    "error": None,
    "step": 0,
    "log_lines": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Sidebar
with st.sidebar:
    st.markdown("### Configuration")
    st.markdown("---")
    groq_key = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password", placeholder="gsk_...", help="Required for Groq-powered agents")  # FIXED: Google → Groq
    tavily_key = st.text_input("Tavily API Key", value=os.getenv("TAVILY_API_KEY", ""), type="password", placeholder="tvly-...", help="Required for web search")
    st.markdown("---")
    st.markdown("### Pipeline Stages")
    st.markdown("""
<div style='font-size:.82rem;color:#64748b;line-height:2;'>
1. <b style='color:#e2e8f0'>Search Agent</b> - finds web sources<br>
2. <b style='color:#e2e8f0'>Reader Agent</b> - scrapes top URL<br>
3. <b style='color:#e2e8f0'>Writer Chain</b> - drafts the report<br>
4. <b style='color:#e2e8f0'>Critic Chain</b> - reviews and scores
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Clear Results", use_container_width=True):
        st.session_state.results = None
        st.session_state.error = None
        st.session_state.step = 0
        st.session_state.log_lines = []
        st.rerun()

# Hero
st.markdown("""
<div class='hero'>
  <div class='hero-title'>ResearchMind</div>
  <div class='hero-sub'>Multi-agent pipeline: Search - Read - Write - Critique</div>
</div>
""", unsafe_allow_html=True)

# Topic input + run button
col_in, col_btn = st.columns([5, 1], gap="small")
with col_in:
    topic = st.text_input("topic", placeholder="e.g. Quantum error correction breakthroughs 2024", label_visibility="collapsed", disabled=st.session_state.running)
with col_btn:
    run_clicked = st.button(
        "Run" if not st.session_state.running else "Running...",
        use_container_width=True,
        disabled=st.session_state.running or not topic.strip(),
    )

# Step pills
STEPS = [("Search", "Search"), ("Reader", "Reader"), ("Writer", "Writer"), ("Critic", "Critic")]

def render_pills(current_step, has_error):
    pills = ""
    for i, (icon, label) in enumerate(STEPS, start=1):
        if current_step == 0:
            s = "waiting"
        elif has_error and i == current_step:
            s = "error"
        elif i < current_step:
            s = "done"
        elif i == current_step:
            s = "running"
        else:
            s = "waiting"
        pills += f"<span class='step-pill {s}'>{icon} {label}</span>"
    st.markdown(f"<div class='step-row'>{pills}</div>", unsafe_allow_html=True)

render_pills(st.session_state.step, bool(st.session_state.error))

# Pipeline runner
def run_pipeline(topic, groq_key, tkey):   # FIXED: gkey → groq_key
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key  # FIXED: GOOGLE_API_KEY → GROQ_API_KEY
    if tkey:
        os.environ["TAVILY_API_KEY"] = tkey

    try:
        from pipeline import run_research_pipeline
    except ImportError as e:
        st.session_state.error = (
            f"Could not import pipeline.py: {e}\n\n"
            "Make sure all dependencies are installed:\n"
            "  pip install langchain langchain-groq langchain-community tavily-python"  # FIXED: updated install command
        )
        st.session_state.running = False
        st.session_state.step = 0
        return

    log_lines = st.session_state.log_lines

    def on_progress(step, message):
        st.session_state.step = step
        log_lines.append(message)

    try:
        result = run_research_pipeline(topic, progress_callback=on_progress)
        st.session_state.results = result
        st.session_state.step = 5
        st.session_state.error = None
    except Exception as e:
        st.session_state.error = str(e)
    finally:
        st.session_state.running = False

# Trigger
if run_clicked and topic.strip():
    st.session_state.running = True
    st.session_state.results = None
    st.session_state.error = None
    st.session_state.step = 1
    st.session_state.log_lines = []
    st.rerun()

if st.session_state.running:
    with st.spinner("Pipeline running - this may take 30-90 seconds..."):
        run_pipeline(topic, groq_key, tavily_key)  # FIXED: google_key → groq_key
    st.rerun()

# Error banner
if st.session_state.error:
    st.markdown(f"""
<div class='r-card red-left'>
  <div style='font-weight:700;color:#ef4444;margin-bottom:.4rem;'>Pipeline Error</div>
  <div style='font-size:.88rem;font-family:"JetBrains Mono",monospace;color:#fca5a5;white-space:pre-wrap;'>{st.session_state.error}</div>
</div>
""", unsafe_allow_html=True)

# Results
if st.session_state.results:
    res = st.session_state.results
    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#252b3b,transparent);margin:1.2rem 0;'></div>", unsafe_allow_html=True)

    sr  = res.get("search_results", "")
    sc  = res.get("scraped_content", "")
    rpt = res.get("report", "")

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(f"<div class='r-card accent-left'><div class='section-label'>Search Results</div><div style='font-size:1.6rem;font-weight:700;color:#4f8ef7;'>{len(sr.split()) if sr else 0}</div><div style='font-size:.78rem;color:#64748b;'>words retrieved</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='r-card green-left'><div class='section-label'>Scraped Content</div><div style='font-size:1.6rem;font-weight:700;color:#22c55e;'>{len(sc.split()) if sc else 0}</div><div style='font-size:.78rem;color:#64748b;'>words scraped</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='r-card purple-left'><div class='section-label'>Final Report</div><div style='font-size:1.6rem;font-weight:700;color:#7b5cf0;'>{len(rpt.split()) if rpt else 0}</div><div style='font-size:.78rem;color:#64748b;'>words in report</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_report, tab_critic, tab_search, tab_scraped, tab_log = st.tabs([
        "Report", "Critic Feedback", "Search Results", "Scraped Content", "Run Log"
    ])

    with tab_report:
        st.markdown(f"<div class='report-box'>{rpt or 'No report generated.'}</div>", unsafe_allow_html=True)
        if rpt:
            st.download_button("Download Report (.txt)", data=rpt, file_name=f"report_{topic[:40].replace(' ','_')}.txt", mime="text/plain")

    with tab_critic:
        feedback = res.get("feedback", "No feedback generated.")
        st.markdown(f"<div class='r-card amber-left' style='margin-bottom:0;'><div class='section-label'>Critic Assessment</div><div style='white-space:pre-wrap;font-size:.9rem;line-height:1.75;'>{feedback}</div></div>", unsafe_allow_html=True)

    with tab_search:
        st.markdown(f"<div class='content-box'>{sr or 'No search results.'}</div>", unsafe_allow_html=True)

    with tab_scraped:
        st.markdown(f"<div class='content-box'>{sc or 'No scraped content.'}</div>", unsafe_allow_html=True)

    with tab_log:
        log_text = "\n".join(st.session_state.log_lines) or "No log output."
        st.markdown(f"<div class='log-box'>{log_text}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Export full pipeline state (JSON)"):
        safe_res = {k: str(v) for k, v in res.items()}
        st.download_button("Download .json", data=json.dumps(safe_res, indent=2), file_name=f"pipeline_state_{topic[:40].replace(' ','_')}.json", mime="application/json")

# Idle / empty state
if not st.session_state.running and not st.session_state.results and not st.session_state.error:
    st.markdown("""
<div style='text-align:center;padding:3.5rem 1rem 2rem;color:#334155;'>
  <div style='font-size:3rem;margin-bottom:.8rem;'>🧠</div>
  <div style='font-size:1rem;font-weight:600;color:#475569;margin-bottom:.4rem;'>Ready to research</div>
  <div style='font-size:.85rem;color:#334155;'>Enter a topic above and hit Run to start the pipeline.</div>
</div>
""", unsafe_allow_html=True)