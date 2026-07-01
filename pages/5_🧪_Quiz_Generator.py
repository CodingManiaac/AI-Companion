"""
Quiz Generator Page – AI Study Companion
Generate MCQ quizzes from study materials, take them interactively, and track scores.
"""

import streamlit as st
import json
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header, render_empty_state, generate_download_html
from utils.ai_engine import generate_quiz
from database.db import (
    get_user_documents, get_document_by_id,
    save_quiz_result, get_user_quiz_results
)

require_auth()
user = get_current_user()

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "🧪 Quiz Generator",
    "Test your knowledge with AI-generated quizzes from your study materials"
)

# ── Document Selection ─────────────────────────────────────
documents = get_user_documents(user["id"])

if not documents:
    render_empty_state(
        "📄",
        "No documents uploaded",
        "Upload your PDF study materials first to generate quizzes."
    )
    if st.button("📄 Go to Upload"):
        st.switch_page("pages/2_📄_Upload_Documents.py")
    st.stop()

tab_generate, tab_history = st.tabs(["📝 Take a Quiz", "📊 Quiz History"])

with tab_generate:
    doc_options = {d["file_name"]: d["id"] for d in documents}
    selected_doc_name = st.selectbox("📚 Select a document", options=list(doc_options.keys()), key="quiz_doc")
    selected_doc_id = doc_options[selected_doc_name]

    num_questions = st.slider("Number of questions", min_value=3, max_value=20, value=5, step=1)

    # Generate Quiz
    if st.button("✨ Generate Quiz", use_container_width=True):
        doc = get_document_by_id(selected_doc_id)
        if not doc or not doc.get("text_content"):
            st.error("❌ No text content found for this document.")
        else:
            with st.spinner("🤖 AI is creating your quiz..."):
                quiz_data = generate_quiz(doc["text_content"], num_questions)
                if quiz_data:
                    st.session_state["quiz_data"] = quiz_data
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_score"] = None
                    st.session_state["quiz_doc_id"] = selected_doc_id
                    st.rerun()
                else:
                    st.error("❌ Failed to generate quiz. Please try again.")

    # Display Quiz
    if st.session_state.get("quiz_data") and not st.session_state.get("quiz_submitted"):
        quiz_data = st.session_state["quiz_data"]
        st.divider()
        st.markdown(f"### 📝 Quiz — {len(quiz_data)} Questions")
        st.caption("Select the best answer for each question, then submit.")

        with st.form("quiz_form"):
            for i, q in enumerate(quiz_data):
                st.markdown(f"**Q{i + 1}. {q['question']}**")
                options = q.get("options", [])
                if options:
                    answer = st.radio(
                        f"Select answer for Q{i + 1}",
                        options=options,
                        key=f"q_{i}",
                        label_visibility="collapsed"
                    )
                st.markdown("---")

            submitted = st.form_submit_button("📤 Submit Quiz", use_container_width=True)

            if submitted:
                # Calculate score
                score = 0
                answers = {}
                for i, q in enumerate(quiz_data):
                    selected = st.session_state.get(f"q_{i}", "")
                    correct_letter = q.get("correct_answer", "")
                    # Extract the letter from the selected option
                    selected_letter = selected[0] if selected else ""
                    is_correct = selected_letter.upper() == correct_letter.upper()
                    if is_correct:
                        score += 1
                    answers[i] = {
                        "selected": selected,
                        "correct_letter": correct_letter,
                        "is_correct": is_correct,
                    }

                st.session_state["quiz_submitted"] = True
                st.session_state["quiz_answers"] = answers
                st.session_state["quiz_score"] = score

                # Save to database
                save_quiz_result(
                    user["id"],
                    st.session_state.get("quiz_doc_id"),
                    score,
                    len(quiz_data),
                    quiz_data
                )
                st.rerun()

    # Show Results
    if st.session_state.get("quiz_submitted") and st.session_state.get("quiz_data"):
        quiz_data = st.session_state["quiz_data"]
        score = st.session_state["quiz_score"]
        total = len(quiz_data)
        percentage = round((score / total) * 100) if total > 0 else 0
        answers = st.session_state["quiz_answers"]

        # Score card
        if percentage >= 80:
            grade_emoji = "🏆"
            grade_text = "Excellent!"
            grade_color = "#10B981"
        elif percentage >= 60:
            grade_emoji = "👍"
            grade_text = "Good Job!"
            grade_color = "#3B82F6"
        elif percentage >= 40:
            grade_emoji = "📖"
            grade_text = "Keep Studying"
            grade_color = "#F59E0B"
        else:
            grade_emoji = "💪"
            grade_text = "Need More Practice"
            grade_color = "#EF4444"

        st.markdown(f"""
            <div class="quiz-score-card">
                <div style="font-size: 3rem;">{grade_emoji}</div>
                <div class="score-value">{score}/{total}</div>
                <div class="score-label">{percentage}% — {grade_text}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Detailed results
        st.markdown("### 📋 Detailed Results")
        for i, q in enumerate(quiz_data):
            ans = answers.get(i, {})
            is_correct = ans.get("is_correct", False)
            icon = "✅" if is_correct else "❌"
            selected = ans.get("selected", "No answer")
            correct_letter = q.get("correct_answer", "")

            st.markdown(f"**{icon} Q{i + 1}. {q['question']}**")

            for opt in q.get("options", []):
                opt_letter = opt[0].upper()
                if opt_letter == correct_letter.upper():
                    st.markdown(f"&emsp; 🟢 {opt}")
                elif opt == selected and not is_correct:
                    st.markdown(f"&emsp; 🔴 ~~{opt}~~")
                else:
                    st.markdown(f"&emsp; ⚪ {opt}")

            if q.get("explanation"):
                st.caption(f"💡 {q['explanation']}")
            st.markdown("---")

        # Download quiz
        results_html = f"<h2>Score: {score}/{total} ({percentage}%)</h2>"
        for i, q in enumerate(quiz_data):
            ans = answers.get(i, {})
            is_correct = ans.get("is_correct", False)
            icon = "✅" if is_correct else "❌"
            results_html += f'<div class="question"><strong>{icon} Q{i+1}. {q["question"]}</strong></div>'
            for opt in q.get("options", []):
                opt_letter = opt[0].upper()
                correct_letter = q.get("correct_answer", "").upper()
                if opt_letter == correct_letter:
                    results_html += f'<p class="correct">🟢 {opt}</p>'
                else:
                    results_html += f'<p>⚪ {opt}</p>'
            if q.get("explanation"):
                results_html += f'<div class="answer">💡 {q["explanation"]}</div>'

        download_html = generate_download_html("Quiz Results", results_html)
        st.download_button(
            "📥 Download Quiz Results",
            data=download_html,
            file_name="quiz_results.html",
            mime="text/html",
            use_container_width=True,
        )

        # Retake button
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state["quiz_data"] = None
            st.session_state["quiz_submitted"] = False
            st.session_state["quiz_answers"] = {}
            st.session_state["quiz_score"] = None
            st.rerun()

with tab_history:
    st.markdown("### 📊 Your Quiz History")
    results = get_user_quiz_results(user["id"])

    if not results:
        render_empty_state("🧪", "No quizzes taken yet", "Generate and complete a quiz to see your history here.")
    else:
        for r in results:
            pct = round((r["score"] / r["total_questions"]) * 100) if r["total_questions"] > 0 else 0
            date_str = str(r.get("date", ""))[:10]
            doc_name = r.get("file_name", "Unknown document")

            col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
            with col1:
                st.markdown(f"📄 **{doc_name}** — {date_str}")
            with col2:
                st.markdown(f"Score: **{r['score']}/{r['total_questions']}**")
            with col3:
                if pct >= 80:
                    st.markdown(f"🟢 **{pct}%**")
                elif pct >= 60:
                    st.markdown(f"🔵 **{pct}%**")
                elif pct >= 40:
                    st.markdown(f"🟡 **{pct}%**")
                else:
                    st.markdown(f"🔴 **{pct}%**")
            st.divider()
