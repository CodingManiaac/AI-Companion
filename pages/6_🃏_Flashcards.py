"""
Flashcards Page – AI Study Companion
Generate, browse, and study interactive flashcards from uploaded documents.
"""

import streamlit as st
import json
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header, render_empty_state, generate_download_html
from utils.ai_engine import generate_flashcards
from database.db import (
    get_user_documents, get_document_by_id,
    save_flashcards_bulk, get_user_flashcards, delete_flashcard
)

require_auth()
user = get_current_user()

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "🃏 Flashcards",
    "Create and study AI-generated flashcards for effective memorization"
)

# ── Tabs ───────────────────────────────────────────────────
tab_generate, tab_saved = st.tabs(["✨ Generate Flashcards", "📚 Saved Flashcards"])

with tab_generate:
    documents = get_user_documents(user["id"])

    if not documents:
        render_empty_state(
            "📄",
            "No documents uploaded",
            "Upload your PDF study materials first to generate flashcards."
        )
        if st.button("📄 Go to Upload", key="fc_upload"):
            st.switch_page("pages/2_📄_Upload_Documents.py")
        st.stop()

    doc_options = {d["file_name"]: d["id"] for d in documents}
    selected_doc_name = st.selectbox("📚 Select a document", options=list(doc_options.keys()), key="fc_doc")
    selected_doc_id = doc_options[selected_doc_name]

    num_cards = st.slider("Number of flashcards", min_value=5, max_value=20, value=10, step=1)

    if st.button("✨ Generate Flashcards", use_container_width=True, key="gen_fc"):
        doc = get_document_by_id(selected_doc_id)
        if not doc or not doc.get("text_content"):
            st.error("❌ No text content found for this document.")
        else:
            with st.spinner("🤖 AI is creating your flashcards..."):
                cards = generate_flashcards(doc["text_content"], num_cards)
                if cards:
                    st.session_state["flashcards"] = cards
                    st.session_state["flashcard_index"] = 0
                    st.session_state["flashcard_flipped"] = False
                    st.session_state["fc_doc_id"] = selected_doc_id
                    st.rerun()
                else:
                    st.error("❌ Failed to generate flashcards. Please try again.")

    # Display flashcards
    if st.session_state.get("flashcards"):
        cards = st.session_state["flashcards"]
        idx = st.session_state.get("flashcard_index", 0)
        flipped = st.session_state.get("flashcard_flipped", False)

        st.divider()
        st.markdown(f"### 🃏 Flashcard {idx + 1} of {len(cards)}")

        # Progress bar
        st.progress((idx + 1) / len(cards))

        current_card = cards[idx]

        # Flashcard display with flip
        if not flipped:
            st.markdown(f"""
                <div class="flashcard-container">
                    <div class="flashcard">
                        <div class="flashcard-front">
                            <div class="flashcard-label">QUESTION</div>
                            <h3>{current_card['question']}</h3>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="flashcard-container">
                    <div class="flashcard flipped">
                        <div class="flashcard-front">
                            <div class="flashcard-label">QUESTION</div>
                            <h3>{current_card['question']}</h3>
                        </div>
                        <div class="flashcard-back">
                            <div class="flashcard-label">ANSWER</div>
                            <p>{current_card['answer']}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(idx == 0)):
                st.session_state["flashcard_index"] = max(0, idx - 1)
                st.session_state["flashcard_flipped"] = False
                st.rerun()
        with col2:
            flip_label = "🔄 Show Answer" if not flipped else "🔄 Show Question"
            if st.button(flip_label, use_container_width=True):
                st.session_state["flashcard_flipped"] = not flipped
                st.rerun()
        with col3:
            if st.button("➡️ Next", use_container_width=True, disabled=(idx >= len(cards) - 1)):
                st.session_state["flashcard_index"] = min(len(cards) - 1, idx + 1)
                st.session_state["flashcard_flipped"] = False
                st.rerun()

        st.divider()

        # Save all flashcards
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save All Flashcards", use_container_width=True):
                doc_id = st.session_state.get("fc_doc_id")
                save_flashcards_bulk(user["id"], doc_id, cards)
                st.success(f"✅ Saved {len(cards)} flashcards!")

        with col2:
            # Download flashcards
            fc_html = ""
            for i, card in enumerate(cards, 1):
                fc_html += f"""
                    <div class="question"><strong>Q{i}: {card['question']}</strong></div>
                    <div class="answer">{card['answer']}</div>
                """
            download_html = generate_download_html("Flashcards", fc_html)
            st.download_button(
                "📥 Download Flashcards",
                data=download_html,
                file_name="flashcards.html",
                mime="text/html",
                use_container_width=True,
            )

with tab_saved:
    st.markdown("### 📚 Your Saved Flashcards")
    saved_cards = get_user_flashcards(user["id"])

    if not saved_cards:
        render_empty_state(
            "🃏",
            "No saved flashcards",
            "Generate flashcards from your documents and save them for later study."
        )
    else:
        st.caption(f"You have {len(saved_cards)} saved flashcard(s)")

        # Study mode for saved cards
        if st.button("📖 Study All Saved Cards", use_container_width=True):
            st.session_state["flashcards"] = [
                {"question": c["question"], "answer": c["answer"]} for c in saved_cards
            ]
            st.session_state["flashcard_index"] = 0
            st.session_state["flashcard_flipped"] = False
            st.rerun()

        st.divider()

        for card in saved_cards:
            with st.expander(f"❓ {card['question'][:80]}..."):
                st.markdown(f"**Answer:** {card['answer']}")
                doc_name = card.get("file_name", "Unknown document")
                st.caption(f"📄 From: {doc_name}")
                if st.button("🗑️ Delete", key=f"del_fc_{card['id']}"):
                    delete_flashcard(card["id"])
                    st.rerun()
