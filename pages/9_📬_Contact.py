"""
Contact Page – AI Study Companion
Contact form and feedback submission.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header
from database.db import save_contact_message

require_auth()
user = get_current_user()

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "📬 Contact & Feedback",
    "Get in touch or share your feedback to help us improve"
)

tab_contact, tab_feedback = st.tabs(["📧 Contact Us", "⭐ Feedback"])

with tab_contact:
    st.markdown("### 📧 Send a Message")
    st.caption("Have a question or need help? Fill out the form below.")

    with st.form("contact_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name", value=user.get("name", ""), placeholder="John Doe")
        with col2:
            email = st.text_input("Your Email", value=user.get("email", ""), placeholder="you@example.com")

        subject = st.text_input("Subject", placeholder="e.g., Feature request, Bug report, Question")
        message = st.text_area(
            "Message",
            placeholder="Tell us what's on your mind...",
            height=150
        )

        submitted = st.form_submit_button("📤 Send Message", use_container_width=True)

        if submitted:
            if not name or not email or not message:
                st.error("❌ Please fill in all required fields (Name, Email, Message).")
            else:
                save_contact_message(name, email, subject, message, message_type="contact")
                st.success("✅ Thank you! Your message has been sent successfully.")
                st.balloons()

with tab_feedback:
    st.markdown("### ⭐ Share Your Feedback")
    st.caption("Your feedback helps us improve the AI Study Companion experience.")

    with st.form("feedback_form", clear_on_submit=True):
        # Rating
        rating = st.select_slider(
            "How would you rate your experience?",
            options=["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"],
            value="⭐⭐⭐ Good"
        )

        # Feature feedback
        favorite_feature = st.selectbox(
            "What's your favorite feature?",
            options=[
                "PDF Upload & Management",
                "AI Summaries",
                "Ask Questions (RAG)",
                "Quiz Generator",
                "Flashcards",
                "Study Planner",
                "Progress Dashboard",
                "Other"
            ]
        )

        # What could be improved
        improvements = st.text_area(
            "What could we improve?",
            placeholder="Share your suggestions for improvement...",
            height=120
        )

        # General comments
        comments = st.text_area(
            "Additional Comments (optional)",
            placeholder="Any other thoughts or feedback...",
            height=80
        )

        submitted = st.form_submit_button("📤 Submit Feedback", use_container_width=True)

        if submitted:
            feedback_message = (
                f"Rating: {rating}\n"
                f"Favorite Feature: {favorite_feature}\n"
                f"Improvements: {improvements}\n"
                f"Comments: {comments}"
            )
            save_contact_message(
                user.get("name", "Anonymous"),
                user.get("email", ""),
                f"Feedback - {rating}",
                feedback_message,
                message_type="feedback"
            )
            st.success("✅ Thank you for your feedback! We appreciate it.")
            st.balloons()

# ── Info Section ───────────────────────────────────────────
st.divider()
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #94A3B8;">
        <h4 style="color: #E2E8F0;">🎓 AI Study Companion</h4>
        <p>Built with ❤️ using Streamlit & Google Gemini</p>
        <p style="font-size: 0.85rem;">
            📧 support@aistudycompanion.com &nbsp;&nbsp;|&nbsp;&nbsp;
            📱 Follow us on social media &nbsp;&nbsp;|&nbsp;&nbsp;
            📖 Documentation
        </p>
    </div>
""", unsafe_allow_html=True)
