import streamlit as st
from workflow.graph import build_graph

st.set_page_config(page_title="Enterprise AI Studio")

st.title("Multi-Agent AI Workflow Studio v2")

workflow = build_graph()

task = st.text_area("Enter Task")

if st.button("Run"):
    state = {"task": task}

    result = workflow.invoke(state)

    st.subheader("Plan")
    st.write(result.get("plan"))

    st.subheader("Context (RAG)")
    st.write(result.get("context"))

    st.subheader("Final Output")
    st.write(result.get("final"))