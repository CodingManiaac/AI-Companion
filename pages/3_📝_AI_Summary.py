"""
AI Summary Page – AI Study Companion
Generate concise summaries, key points, and chapter-wise breakdowns from uploaded PDFs.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header, render_empty_state, generate_download_html
from utils.ai_engine import generate_summary, generate_key_points, generate_chapter_summary
from database.db import get_user_documents, get_document_by_id

require_auth()
user = get_current_user()

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "📝 AI Summary Generator",
    "Generate intelligent summaries from your study materials using Gemini AI"
)

# ── Document Selection ─────────────────────────────────────
documents = get_user_documents(user["id"])

if not documents:
    render_empty_state(
        "📄",
        "No documents uploaded",
        "Upload your PDF study materials first to generate summaries."
    )
    if st.button("📄 Go to Upload"):
        st.switch_page("pages/2_📄_Upload_Documents.py")
    st.stop()

doc_options = {f"{d['file_name']} (uploaded {str(d['upload_date'])[:10]})": d["id"] for d in documents}
selected_doc_label = st.selectbox("📚 Select a document", options=list(doc_options.keys()))
selected_doc_id = doc_options[selected_doc_label]

# Load document text
doc = get_document_by_id(selected_doc_id)
if not doc or not doc.get("text_content"):
    st.error("❌ No text content found for this document.")
    st.stop()

text_content = doc["text_content"]
st.info(f"📊 Document: **{doc['file_name']}** — {len(text_content):,} characters")

st.divider()

# ── Summary Generation ─────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Concise Summary", "🎯 Key Points", "📖 Chapter-wise Summary"])

with tab1:
    st.markdown("#### 📋 Concise Summary")
    st.caption("Generate a clear, condensed summary of the entire document.")

    if st.button("✨ Generate Summary", key="gen_summary", use_container_width=True):
        with st.spinner("🤖 AI is analyzing your document..."):
            summary = generate_summary(text_content)
            st.session_state["last_summary"] = summary

    if st.session_state.get("last_summary"):
        st.markdown(st.session_state["last_summary"])
        st.divider()

        # Download option
        html_content = st.session_state["last_summary"].replace("\n", "<br>")
        download_html = generate_download_html(f"Summary - {doc['file_name']}", html_content)
        st.download_button(
            "📥 Download Summary",
            data=download_html,
            file_name=f"summary_{doc['file_name'].replace('.pdf', '')}.html",
            mime="text/html",
            use_container_width=True,
        )

with tab2:
    st.markdown("#### 🎯 Key Points")
    st.caption("Extract the most important takeaways as numbered bullet points.")

    if st.button("✨ Extract Key Points", key="gen_keypoints", use_container_width=True):
        with st.spinner("🤖 Extracting key points..."):
            key_points = generate_key_points(text_content)
            st.session_state["last_key_points"] = key_points

    if st.session_state.get("last_key_points"):
        st.markdown(st.session_state["last_key_points"])
        st.divider()

        html_content = st.session_state["last_key_points"].replace("\n", "<br>")
        download_html = generate_download_html(f"Key Points - {doc['file_name']}", html_content)
        st.download_button(
            "📥 Download Key Points",
            data=download_html,
            file_name=f"keypoints_{doc['file_name'].replace('.pdf', '')}.html",
            mime="text/html",
            use_container_width=True,
        )

with tab3:
    st.markdown("#### 📖 Chapter-wise Summary")
    st.caption("Get a structured breakdown with summaries for each section/chapter.")

    if st.button("✨ Generate Chapter Summary", key="gen_chapters", use_container_width=True):
        with st.spinner("🤖 Analyzing document structure..."):
            chapter_summary = generate_chapter_summary(text_content)
            st.session_state["last_chapter_summary"] = chapter_summary

    if st.session_state.get("last_chapter_summary"):
        st.markdown(st.session_state["last_chapter_summary"])
        st.divider()

        html_content = st.session_state["last_chapter_summary"].replace("\n", "<br>")
        download_html = generate_download_html(f"Chapter Summary - {doc['file_name']}", html_content)
        st.download_button(
            "📥 Download Chapter Summary",
            data=download_html,
            file_name=f"chapters_{doc['file_name'].replace('.pdf', '')}.html",
            mime="text/html",
            use_container_width=True,
        )
