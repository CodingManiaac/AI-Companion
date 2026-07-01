"""
Home Page – AI Study Companion
Landing page with hero section, feature cards, and quick-action buttons.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.helpers import render_feature_card
from database.db import get_user_stats

require_auth()
user = get_current_user()

# ── Hero Section ───────────────────────────────────────────
st.markdown(f"""
    <div class="hero-section">
        <h1>Welcome back, {user['name']}! 👋</h1>
        <p>
            Your AI-powered study companion is ready to help you learn smarter, not harder.
            Upload your study materials and let AI do the heavy lifting — summaries, quizzes,
            flashcards, and personalized study plans, all in one place.
        </p>
    </div>
""", unsafe_allow_html=True)

# ── Quick Stats Row ────────────────────────────────────────
stats = get_user_stats(user["id"])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class="metric-card purple">
            <div class="metric-icon">📄</div>
            <div class="metric-value">{stats['total_docs']}</div>
            <div class="metric-label">Documents</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="metric-card blue">
            <div class="metric-icon">🧪</div>
            <div class="metric-value">{stats['total_quizzes']}</div>
            <div class="metric-label">Quizzes Taken</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="metric-card green">
            <div class="metric-icon">🃏</div>
            <div class="metric-value">{stats['total_flashcards']}</div>
            <div class="metric-label">Flashcards</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class="metric-card amber">
            <div class="metric-icon">🔥</div>
            <div class="metric-value">{stats['study_streak']}</div>
            <div class="metric-label">Day Streak</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Features Grid ─────────────────────────────────────────
st.markdown("""
    <div class="section-header">
        <h2>✨ What Can I Do For You?</h2>
        <p>Explore powerful AI-driven study tools designed to boost your learning</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    render_feature_card(
        "📄",
        "Upload & Manage",
        "Upload PDF study materials and build your personal knowledge base."
    )
with col2:
    render_feature_card(
        "📝",
        "AI Summaries",
        "Generate concise summaries, key points, and chapter breakdowns instantly."
    )
with col3:
    render_feature_card(
        "❓",
        "Ask Questions",
        "Chat with your documents using RAG-powered AI for accurate answers."
    )

col4, col5, col6 = st.columns(3)
with col4:
    render_feature_card(
        "🧪",
        "Quiz Generator",
        "Auto-generate MCQ quizzes from your notes and test your knowledge."
    )
with col5:
    render_feature_card(
        "🃏",
        "Flashcards",
        "Create interactive flashcards for quick revision and memorization."
    )
with col6:
    render_feature_card(
        "📅",
        "Study Planner",
        "Get AI-generated personalized study schedules based on your goals."
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Actions ──────────────────────────────────────────
st.markdown("""
    <div class="section-header">
        <h2>🚀 Quick Actions</h2>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📄 Upload Documents", use_container_width=True):
        st.switch_page("pages/2_📄_Upload_Documents.py")
with col2:
    if st.button("🧪 Take a Quiz", use_container_width=True):
        st.switch_page("pages/5_🧪_Quiz_Generator.py")
with col3:
    if st.button("🃏 Study Flashcards", use_container_width=True):
        st.switch_page("pages/6_🃏_Flashcards.py")
with col4:
    if st.button("📊 View Progress", use_container_width=True):
        st.switch_page("pages/8_📊_Progress_Dashboard.py")

# ── Footer ─────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; border-top: 1px solid rgba(148, 163, 184, 0.15);">
        <p style="color: #64748B; font-size: 0.85rem;">
            🎓 AI Study Companion • Powered by Google Gemini • Built with Streamlit
        </p>
    </div>
""", unsafe_allow_html=True)
