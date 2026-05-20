# import streamlit as st
# from workflow.graph import build_graph

# st.set_page_config(page_title="Enterprise AI Studio")

# st.title("Multi-Agent AI Workflow Studio v2")

# workflow = build_graph()

# task = st.text_area("Enter Task")

# if st.button("Run"):
#     state = {"task": task}

#     result = workflow.invoke(state)

#     st.subheader("Plan")
#     st.write(result.get("plan"))

#     st.subheader("Context (RAG)")
#     st.write(result.get("context"))

#     st.subheader("Final Output")
#     st.write(result.get("final"))

import streamlit as st
from workflow.graph import build_graph
import pdfplumber
import docx
import io

st.set_page_config(
    page_title="Enterprise AI Studio",
    page_icon="🤖",
    layout="wide"
)

st.title("Multi-Agent AI Workflow Studio")

# ── Cache graph so it doesn't rebuild on every interaction ───────────────────
@st.cache_resource
def load_graph():
    return build_graph()

workflow = load_graph()


# ── File text extractor ───────────────────────────────────────────────────────
def extract_text(uploaded_file) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    name = uploaded_file.name.lower()
    raw  = uploaded_file.read()

    if name.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            ).strip()

    elif name.endswith(".docx"):
        doc = docx.Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    elif name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore").strip()

    else:
        st.error(f"Unsupported file type: {uploaded_file.name}")
        return ""


# ── Layout: two columns ───────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 Input")

    # File upload
    uploaded_files = st.file_uploader(
        "Upload files (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    file_context = ""
    if uploaded_files:
        with st.spinner("Extracting text from files..."):
            extracted = []
            for f in uploaded_files:
                text = extract_text(f)
                if text:
                    extracted.append(f"--- {f.name} ---\n{text}")
                    st.success(f"✅ {f.name} ({len(text):,} chars extracted)")
                else:
                    st.warning(f"⚠️ {f.name} — no text found")

            file_context = "\n\n".join(extracted)

        # Preview extracted text
        with st.expander("📄 Preview extracted text"):
            st.text(file_context[:3000] + ("..." if len(file_context) > 3000 else ""))

    # Task input
    task = st.text_area(
        "Enter your task or question",
        placeholder="e.g. Summarise the uploaded document and list key action items.",
        height=150,
    )

    # Combine file context + task
    full_task = f"{task}\n\nDocument Context:\n{file_context}" if file_context else task

    run = st.button("🚀 Run Workflow", use_container_width=True, type="primary")


# ── Run workflow and show results ─────────────────────────────────────────────
with col2:
    st.subheader("📤 Output")

    if run:
        if not task.strip():
            st.warning("Please enter a task before running.")
        else:
            with st.spinner("Running multi-agent workflow..."):
                try:
                    result = workflow.invoke({"task": full_task})
                except Exception as e:
                    st.error(f"Workflow error: {e}")
                    st.stop()

            # ── Error state ───────────────────────────────────────────────────
            if result.get("error"):
                st.error(f"Agent error: {result['error']}")

            else:
                # ── Plan ──────────────────────────────────────────────────────
                with st.expander("🗂 Plan", expanded=True):
                    st.write(result.get("plan") or "No plan returned.")

                # ── RAG Context ───────────────────────────────────────────────
                with st.expander("🔍 Context (RAG)", expanded=False):
                    st.write(result.get("context") or "No context returned.")

                # ── Final Output ──────────────────────────────────────────────
                st.subheader("✅ Final Output")
                final = result.get("final") or "No output returned."
                st.write(final)

                # ── Download result ───────────────────────────────────────────
                st.download_button(
                    label="⬇️ Download Result",
                    data=final,
                    file_name="workflow_result.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
    else:
        st.info("Upload files and enter a task, then click **Run Workflow**.")