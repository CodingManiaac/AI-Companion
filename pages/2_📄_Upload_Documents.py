"""
Upload Documents Page – AI Study Companion
Handles PDF upload, text extraction, FAISS indexing, and document management.
"""

import streamlit as st
import os
import time
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header, render_empty_state
from utils.pdf_processor import extract_text, chunk_text, get_page_count, get_file_size_mb
from utils.vector_store import create_index, index_exists, delete_index
from database.db import (
    save_document, get_user_documents, get_document_by_id,
    delete_document, search_documents
)

require_auth()
user = get_current_user()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "📄 Upload Documents",
    "Upload your PDF study materials to get started with AI-powered learning"
)

# ── Upload Section ─────────────────────────────────────────
st.markdown("### 📤 Upload New PDFs")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload one or more PDF files. Maximum file size depends on your Streamlit configuration."
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Create a user-specific upload directory
        user_upload_dir = os.path.join(UPLOAD_DIR, str(user["id"]))
        os.makedirs(user_upload_dir, exist_ok=True)

        # Save file to disk
        file_path = os.path.join(user_upload_dir, uploaded_file.name)

        # Check if file already exists
        existing_docs = get_user_documents(user["id"])
        already_exists = any(d["file_name"] == uploaded_file.name for d in existing_docs)

        if already_exists:
            st.warning(f"⚠️ `{uploaded_file.name}` already uploaded. Skipping.")
            continue

        with st.spinner(f"Processing `{uploaded_file.name}`..."):
            # Write file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract text
            progress = st.progress(0, text="Extracting text...")
            text_content = extract_text(file_path)
            progress.progress(40, text="Text extracted. Chunking...")

            if not text_content.strip():
                st.error(f"❌ Could not extract text from `{uploaded_file.name}`. The PDF may be image-based.")
                os.remove(file_path)
                continue

            # Save to database
            doc_id = save_document(user["id"], uploaded_file.name, file_path, text_content)
            progress.progress(60, text="Saved to database. Building search index...")

            # Chunk and build FAISS index
            chunks = chunk_text(text_content)
            if chunks:
                success = create_index(chunks, user["id"], doc_id)
                if success:
                    progress.progress(100, text="✅ Done!")
                else:
                    progress.progress(100, text="⚠️ Uploaded but search index failed (API key may be missing)")
            else:
                progress.progress(100, text="✅ Uploaded (no indexable chunks)")

            time.sleep(0.5)
            progress.empty()

            page_count = get_page_count(file_path)
            file_size = get_file_size_mb(file_path)
            st.success(f"✅ **{uploaded_file.name}** uploaded successfully — {page_count} pages, {file_size} MB, {len(chunks)} chunks indexed")

    st.rerun()

st.divider()

# ── Uploaded Documents List ────────────────────────────────
st.markdown("### 📚 Your Documents")

# Search bar
search_query = st.text_input("🔍 Search documents", placeholder="Search by filename...", label_visibility="collapsed")

if search_query:
    documents = search_documents(user["id"], search_query)
else:
    documents = get_user_documents(user["id"])

if not documents:
    render_empty_state(
        "📂",
        "No documents yet",
        "Upload your first PDF above to start learning with AI!"
    )
else:
    st.caption(f"Showing {len(documents)} document(s)")

    for doc in documents:
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        with col1:
            upload_date = doc.get("upload_date", "")
            if isinstance(upload_date, str) and len(upload_date) > 10:
                upload_date = upload_date[:10]
            has_index = index_exists(user["id"], doc["id"])
            index_badge = "🟢 Indexed" if has_index else "🔴 No Index"

            st.markdown(f"""
                <div class="doc-card">
                    <div class="doc-icon">📄</div>
                    <div class="doc-info">
                        <h4>{doc['file_name']}</h4>
                        <p>📅 {upload_date} &nbsp;&nbsp; {index_badge}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            # Preview button
            if st.button("👁️ Preview", key=f"preview_{doc['id']}", use_container_width=True):
                st.session_state[f"show_preview_{doc['id']}"] = not st.session_state.get(f"show_preview_{doc['id']}", False)

        with col3:
            # Delete button
            if st.button("🗑️ Delete", key=f"delete_{doc['id']}", use_container_width=True):
                # Delete file from disk
                if os.path.exists(doc["file_path"]):
                    os.remove(doc["file_path"])
                # Delete FAISS index
                delete_index(user["id"], doc["id"])
                # Delete from database
                delete_document(doc["id"])
                st.success(f"Deleted `{doc['file_name']}`")
                st.rerun()

        # Show preview if toggled
        if st.session_state.get(f"show_preview_{doc['id']}", False):
            full_doc = get_document_by_id(doc["id"])
            if full_doc and full_doc.get("text_content"):
                with st.expander(f"📖 Preview: {doc['file_name']}", expanded=True):
                    preview_text = full_doc["text_content"][:3000]
                    st.text(preview_text + ("\n..." if len(full_doc["text_content"]) > 3000 else ""))
