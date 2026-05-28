import streamlit as st
from workflow.graph import build_graph
from rag.ingest import ingest_text
import pdfplumber
import docx
import pandas as pd
import io, json

st.set_page_config(
    page_title="Enterprise AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cache graph ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_graph():
    return build_graph()

workflow = load_graph()

# ── Demo prompts data ─────────────────────────────────────────────────────────
DEMO_PROMPTS = [
    {"domain": "Retail",     "icon": "🛒", "prompt": "Analyze customer purchase data and identify overdue payments"},
    {"domain": "Finance",    "icon": "💳", "prompt": "Review invoice dataset and summarize delayed collections"},
    {"domain": "HR",         "icon": "👥", "prompt": "Analyze employee attrition report and generate insights"},
    {"domain": "Operations", "icon": "🚚", "prompt": "Analyze logistics delays and summarize shipment bottlenecks"},
]

RESOURCES = [
    {"label": "LangGraph Docs",   "url": "https://langchain-ai.github.io/langgraph/"},
    {"label": "Anthropic API",    "url": "https://docs.anthropic.com"},
    {"label": "OpenAI Reference", "url": "https://platform.openai.com/docs"},
    {"label": "Streamlit Docs",   "url": "https://docs.streamlit.io"},
]

TOOL_DETAILS = {
    "🧠 Planner": {
        "badge": "LangGraph · Node 1",
        "desc": "Receives the user task and file context, then produces a structured multi-step execution plan that guides the RAG agent and Supervisor downstream.",
        "stats": {"Avg latency": "~0.8s", "Context window": "4k", "Position": "Node 1"},
        "use_cases": [
            {"domain": "Finance",    "title": "Invoice collection analysis",   "body": "Breaks 'review delayed invoice collections' into: extract dates → compute overdue days → rank by risk → draft follow-up actions.", "tags": ["XLSX input", "date parsing", "risk ranking"]},
            {"domain": "HR",         "title": "Attrition report plan",         "body": "Decomposes attrition task into: segment by department → compute 6-month trend → identify high-risk roles → generate retention recommendations.", "tags": ["CSV input", "trend analysis"]},
            {"domain": "Operations", "title": "Logistics delay breakdown",     "body": "Plans: load shipment records → group by carrier → identify delay clusters → surface bottleneck routes → recommend SLA adjustments.", "tags": ["multi-sheet XLSX", "clustering"]},
        ],
        "steps": ["Receives task string + file context from session state", "Calls LLM backend with structured system prompt to produce a numbered plan", "Writes state['plan'] and passes to RAG node via LangGraph edge", "On failure, populates state['error'] — conditional edge short-circuits to END"],
    },
    "🔍 RAG Agent": {
        "badge": "MongoDB Atlas · Node 2",
        "desc": "Queries MongoDB Atlas using the task as a search query, retrieves the top-5 relevant document chunks, and injects them as grounding context for the Supervisor.",
        "stats": {"Docs retrieved": "Top 5", "Retry on SSL": "3×", "Position": "Node 2"},
        "use_cases": [
            {"domain": "Retail",  "title": "Customer payment history lookup",  "body": "Queries the customer_payments collection to fetch overdue records, purchase frequency, and last contact date for each flagged account.", "tags": ["$text search", "MongoDB"]},
            {"domain": "Finance", "title": "Historical invoice benchmarks",    "body": "Retrieves prior-quarter invoice data to benchmark current collection delays against historical averages and flag outliers.", "tags": ["vector search", "benchmarking"]},
        ],
        "steps": ["Receives state['task'], runs $text search against the configured collection", "SSL retry wrapper reattempts up to 3× with exponential back-off", "Formats results as [source] content blocks, writes to state['context']"],
    },
    "✅ Supervisor": {
        "badge": "Final node · always exits to END",
        "desc": "Receives the plan and RAG context, synthesizes a coherent final answer, validates completeness, and formats the output for download or display.",
        "stats": {"Position": "Node 3", "Exits to": "END", "Download": ".txt"},
        "use_cases": [
            {"domain": "HR",         "title": "Attrition insight report",      "body": "Merges the planner's step list with RAG-retrieved benchmarks to produce: executive summary, risk table, and 3 recommended actions.", "tags": ["report generation", "structured output"]},
            {"domain": "Operations", "title": "Shipment bottleneck summary",   "body": "Synthesises delay clusters into a ranked bottleneck list with carrier names, avg delay hours, and SLA breach count.", "tags": ["carrier ranking", "SLA analysis"]},
        ],
        "steps": ["Receives state['plan'] and state['context'] from upstream nodes", "Calls LLM with synthesis prompt merging plan + context into final answer", "Validates response is non-empty, writes state['final']", "Always connects to END — graph terminates cleanly"],
    },
    "📂 File Extractor": {
        "badge": "Pre-processing pipeline",
        "desc": "Extracts plain text from uploaded files before passing content to the agent pipeline. Supports multi-file, multi-sheet inputs with live preview.",
        "stats": {"File types": "4", "Files per run": "∞", "Preview rows": "50"},
        "use_cases": [
            {"domain": "XLSX/XLS", "title": "Spreadsheet — all sheets",  "body": "All sheets extracted via pandas, NaN cells blanked, converted to CSV-style text. First 50 rows previewed as interactive dataframe.", "tags": ["openpyxl", "xlrd", "multi-sheet"]},
            {"domain": "PDF",      "title": "Reports and invoices",       "body": "Page-by-page text extraction using pdfplumber. Native PDFs work out of the box; scanned PDFs require OCR pre-processing.", "tags": ["pdfplumber", "page merge"]},
            {"domain": "DOCX",     "title": "Word documents",             "body": "Paragraph-level extraction via python-docx. Tables and inline text included; embedded images are skipped.", "tags": ["python-docx"]},
        ],
        "steps": ["User uploads files via st.file_uploader", "extract_text() dispatches to correct parser by file extension", "All text concatenated with --- filename --- separators", "Combined context appended to task string before invoking the graph"],
    },
    "⚙️ LLM Router": {
        "badge": "Backend-agnostic · 4 providers",
        "desc": "Single call_llm() routes to OpenAI, Anthropic Claude, Gemini, or Azure OpenAI based on the LLM_BACKEND environment variable. No code change needed to switch.",
        "stats": {"Backends": "4", "Env var switch": "1", "SDK": "OpenAI-compat"},
        "use_cases": [
            {"domain": "Recommended", "title": "Anthropic Claude (claude-sonnet)", "body": "No token expiry, fast managed inference, strong reasoning. Best default for enterprise workflow tasks.", "tags": ["ANTHROPIC_API_KEY", "no expiry"]},
            {"domain": "OpenAI",      "title": "GPT-4o",                            "body": "Strong general performance. Best for fine-tuned models and strict function-calling schemas.", "tags": ["OPENAI_API_KEY"]},
            {"domain": "Google",      "title": "Gemini 1.5 Flash",                  "body": "Best for vision tasks and large-context document analysis. Multimodal input via call_vision().", "tags": ["GEMINI_API_KEY", "multimodal"]},
        ],
        "steps": ["Reads LLM_BACKEND env var at runtime — no code change to switch providers", "Each backend shares the same call_llm(prompt) signature", "@overload type hints give correct return types per input", "Azure requires 3 env vars; all others need only their API key"],
    },
}


# ── File extractor ────────────────────────────────────────────────────────────
def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    raw  = uploaded_file.read()
    if name.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages).strip()
    elif name.endswith(".docx"):
        return "\n".join(p.text for p in docx.Document(io.BytesIO(raw)).paragraphs).strip()
    elif name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore").strip()
    elif name.endswith((".xlsx", ".xls")):
        xl = pd.ExcelFile(io.BytesIO(raw))
        return "\n\n".join(
            f"[Sheet: {s}]\n{xl.parse(s).fillna('').to_csv(index=False)}"
            for s in xl.sheet_names
        ).strip()
    else:
        st.error(f"Unsupported file type: {uploaded_file.name}")
        return ""


# ── SIDEBAR — navigation only ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⬡ Enterprise AI Studio")
    st.markdown("---")

    # Main nav
    page = st.radio(
        "Navigation",
        ["🏠  Home", "⚡  Demo Prompts", "📖  Tool Info", "📚  Resources"],
        label_visibility="collapsed",
    )

    # Tool submenu only when Tool Info is active
    selected_tool = None
    if "📖" in page:
        st.markdown("---")
        st.caption("SELECT A TOOL")
        selected_tool = st.radio(
            "Tools",
            list(TOOL_DETAILS.keys()),
            label_visibility="collapsed",
        )

    # Version + LinkedIn at bottom
    st.markdown("---")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
        <span style="width:7px;height:7px;background:#22c55e;border-radius:50%;display:inline-block"></span>
        <span style="font-size:12px;font-weight:800;color:#888">v1.0.3 · Enterprise AI Studio</span>
    </div>
    <a href="https://www.linkedin.com/in/ramu-siva" target="_blank"
       style="display:flex;align-items:center;gap:8px;text-decoration:none;
              border:1px solid #2d3148;border-radius:8px;padding:8px 10px">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="#0a66c2">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853
            0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9
            1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337
            7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063
            2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0
            0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24
            23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
        <div>
            <div style="font-size:11px;font-weight:600;color:#e2e8f0">Made by Siva R</div>
            <div style="font-size:10px;color:#666">linkedin.com/in/siva-r-28b082174/</div>
        </div>
    </a>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA — all page content rendered here, not in the sidebar
# ══════════════════════════════════════════════════════════════════════════════

# ── Page: Home ────────────────────────────────────────────────────────────────
if "🏠" in page:
    st.title("Enterprise AI Workflow Studio")
    st.caption("Orchestrate Planner · RAG · Supervisor agents on your enterprise data.")
    st.divider()

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Input")
        uploaded_files = st.file_uploader(
            "Upload files (PDF, DOCX, TXT, XLSX)",
            type=["pdf", "docx", "txt", "xlsx", "xls"],
            accept_multiple_files=True,
        )
        file_context = ""
        if uploaded_files:
            with st.spinner("Extracting content..."):
                extracted = []
                for f in uploaded_files:
                    text = extract_text(f)
                    if text:
                        ingest_text(text)
                        extracted.append(f"--- {f.name} ---\n{text}")
                        st.success(f"✅ {f.name} ({len(text):,} chars)")
                    else:
                        st.warning(f"⚠️ {f.name} — no text found")
                file_context = "\n\n".join(extracted)

            with st.expander("Preview extracted content"):
                for f in uploaded_files:
                    if f.name.lower().endswith((".xlsx", ".xls")):
                        f.seek(0)
                        xl = pd.ExcelFile(io.BytesIO(f.read()))
                        for sheet in xl.sheet_names:
                            st.caption(f"Sheet: {sheet}")
                            st.dataframe(xl.parse(sheet).fillna("").head(50), width='stretch')
                    else:
                        st.text(file_context[:3000] + ("..." if len(file_context) > 3000 else ""))

        default_task = st.session_state.pop("injected_prompt", "")
        task = st.text_area("Task or question", value=default_task,
                            placeholder="e.g. Analyze the uploaded invoice data and flag overdue accounts.",
                            height=140)

        st.caption("Quick fill:")
        chips = st.columns(2)
        for i, item in enumerate(DEMO_PROMPTS):
            with chips[i % 2]:
                if st.button(f"{item['icon']} {item['domain']}", key=f"chip_{i}", width='stretch'):
                    st.session_state["injected_prompt"] = item["prompt"]
                    st.rerun()

        full_task = f"{task}\n\nDocument Context:\n{file_context}" if file_context else task
        run = st.button("Run Workflow →", width='stretch')

    with col2:
        st.subheader("Output")
        if run:
            if not task.strip():
                st.warning("Enter a task before running.")
            else:
                with st.spinner("Running agents…"):
                    try:
                        result = workflow.invoke({"task": full_task})
                    except Exception as e:
                        st.error(f"Workflow error: {e}")
                        st.stop()

                if result.get("error"):
                    st.error(f"Agent error: {result['error']}")
                else:
                    with st.expander("🗂 Plan", expanded=True):
                        st.write(result.get("plan") or "No plan returned.")
                    with st.expander("🔍 RAG Context", expanded=False):
                        st.write(result.get("context") or "No context returned.")
                    st.subheader("Final Output")
                    final = result.get("final") or "No output returned."
                    st.write(final)
                    download_data = json.dumps(final, indent=2)
                    st.download_button("⬇️ Download Result", data=download_data,
                                       file_name="workflow_result.txt",
                                       mime="text/plain", width='stretch')
        else:
            st.info("Upload a file or pick a demo prompt, then click **Run Workflow →**")


# ── Page: Demo Prompts ────────────────────────────────────────────────────────
elif "⚡" in page:
    st.title("Demo Prompts")
    st.caption("Enterprise-ready use cases — click any card to load it into the workflow.")
    st.divider()

    for i in range(0, len(DEMO_PROMPTS), 2):
        cols = st.columns(2, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(DEMO_PROMPTS):
                item = DEMO_PROMPTS[i + j]
                with col:
                    with st.container(border=True):
                        st.markdown(f"### {item['icon']} {item['domain']}")
                        st.write(item["prompt"])
                        if st.button("Use this prompt →", key=f"demo_{i+j}", width='stretch'):
                            st.session_state["injected_prompt"] = item["prompt"]
                            st.session_state["nav_page"] = "🏠  Home"
                            st.rerun()


# ── Page: Tool Info ───────────────────────────────────────────────────────────
elif "📖" in page and selected_tool:
    t = TOOL_DETAILS[selected_tool]

    st.title(selected_tool)
    st.caption(t["badge"])
    st.write(t["desc"])
    st.divider()

    # Stats
    stat_cols = st.columns(len(t["stats"]))
    for col, (label, val) in zip(stat_cols, t["stats"].items()):
        col.metric(label, val)

    st.divider()

    # Use cases in main area
    st.subheader("Real-time use cases")
    uc_cols = st.columns(min(len(t["use_cases"]), 3), gap="medium")
    for col, uc in zip(uc_cols, t["use_cases"]):
        with col:
            with st.container(border=True):
                st.markdown(
                    f'<span style="font-size:10px;font-weight:700;letter-spacing:1px;'
                    f'text-transform:uppercase;padding:2px 8px;border-radius:4px;'
                    f'background:var(--secondary-background-color)">{uc["domain"]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{uc['title']}**")
                st.caption(uc["body"])
                st.write(" ".join(f"`{tag}`" for tag in uc["tags"]))

    st.divider()

    # How it works
    st.subheader("How it works")
    for i, step in enumerate(t["steps"], 1):
        st.markdown(f"**{i}.** {step}")


# ── Page: Resources ───────────────────────────────────────────────────────────
elif "📚" in page:
    st.title("Resources")
    st.caption("Documentation and references for the stack powering this studio.")
    st.divider()

    for r in RESOURCES:
        with st.container(border=True):
            st.markdown(f"**[↗ {r['label']}]({r['url']})**")
            st.caption(r["url"])