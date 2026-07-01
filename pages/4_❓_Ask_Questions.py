"""
Ask Questions (RAG) Page – AI Study Companion
Chat-style Q&A interface using FAISS retrieval and Gemini generation.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header, render_empty_state
from utils.vector_store import search, index_exists
from utils.ai_engine import answer_question
from database.db import (
    get_user_documents, save_chat_message,
    get_chat_history, clear_chat_history
)

require_auth()
user = get_current_user()

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "❓ Ask Questions",
    "Chat with your study materials — powered by RAG (Retrieval-Augmented Generation)"
)

# ── Document Selection ─────────────────────────────────────
documents = get_user_documents(user["id"])

if not documents:
    render_empty_state(
        "📄",
        "No documents uploaded",
        "Upload your PDF study materials first to ask questions."
    )
    if st.button("📄 Go to Upload"):
        st.switch_page("pages/2_📄_Upload_Documents.py")
    st.stop()

# Filter to documents with FAISS indices
indexed_docs = [d for d in documents if index_exists(user["id"], d["id"])]

if not indexed_docs:
    render_empty_state(
        "🔍",
        "No indexed documents",
        "Your documents need to be re-uploaded or indexed. Upload PDFs with a valid Gemini API key."
    )
    st.stop()

doc_options = {d["file_name"]: d["id"] for d in indexed_docs}
selected_doc_name = st.selectbox("📚 Select a document to ask about", options=list(doc_options.keys()))
selected_doc_id = doc_options[selected_doc_name]

# Track document changes for clearing chat
if st.session_state.get("current_doc_id") != selected_doc_id:
    st.session_state["current_doc_id"] = selected_doc_id
    st.session_state["chat_messages"] = []

# Load existing chat history from database
if not st.session_state.get("chat_messages"):
    history = get_chat_history(user["id"], selected_doc_id)
    if history:
        st.session_state["chat_messages"] = [
            {"role": "user" if i % 2 == 0 else "assistant",
             "content": msg["question"] if i % 2 == 0 else msg["answer"]}
            for msg in history
            for i in range(2)
        ]
        # Flatten properly
        msgs = []
        for msg in history:
            msgs.append({"role": "user", "content": msg["question"]})
            msgs.append({"role": "assistant", "content": msg["answer"], "sources": msg.get("sources")})
        st.session_state["chat_messages"] = msgs

st.divider()

# ── Chat Controls ──────────────────────────────────────────
col1, col2 = st.columns([0.8, 0.2])
with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_chat_history(user["id"], selected_doc_id)
        st.session_state["chat_messages"] = []
        st.rerun()

# ── Chat Display ───────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.get("chat_messages"):
        st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #94A3B8;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">💬</div>
                <p>Ask any question about <strong>{}</strong></p>
                <p style="font-size: 0.85rem; color: #64748B;">
                    The AI will search your document for relevant information and provide an accurate answer.
                </p>
            </div>
        """.format(selected_doc_name), unsafe_allow_html=True)
    else:
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                # Show sources if available
                if msg.get("sources") and msg["role"] == "assistant":
                    with st.expander("📎 View source chunks"):
                        for i, source in enumerate(msg["sources"], 1):
                            st.text(f"Chunk {i}: {source[:300]}...")

# ── Chat Input ─────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about your document..."):
    # Add user message
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # Search FAISS for relevant chunks
    with st.spinner("🔍 Searching document..."):
        relevant_chunks = search(prompt, user["id"], selected_doc_id, k=5)

    if not relevant_chunks:
        answer = "I couldn't find relevant information in this document to answer your question. Please try rephrasing or asking about a topic covered in the material."
        sources = []
    else:
        # Build context from retrieved chunks
        context = "\n\n---\n\n".join(relevant_chunks)

        # Get chat history for context
        db_history = get_chat_history(user["id"], selected_doc_id, limit=10)

        # Generate answer
        with st.spinner("🤖 Generating answer..."):
            answer = answer_question(prompt, context, db_history)
        sources = relevant_chunks

    # Display assistant message
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(answer)
            if sources:
                with st.expander("📎 View source chunks"):
                    for i, source in enumerate(sources, 1):
                        st.text(f"Chunk {i}: {source[:300]}...")

    # Save to session and database
    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

    save_chat_message(
        user["id"], selected_doc_id,
        prompt, answer,
        sources=[s[:500] for s in sources[:3]]  # Save truncated sources
    )
