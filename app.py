"""
AI Study Companion – Main Application Entry Point.
Handles authentication UI, page configuration, and navigation.
"""

import streamlit as st
import os
from database.db import init_db
from utils.helpers import load_css, init_session_state
from utils.auth import (
    register_user, login_user, logout,
    is_authenticated, get_current_user
)

# ── Page Configuration ─────────────────────────────────────
st.set_page_config(
    page_title="AI Study Companion",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialization ─────────────────────────────────────────
init_db()
init_session_state()
load_css()

# Ensure upload and vectorstore directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)


# ── Authentication UI ──────────────────────────────────────
def show_auth_page():
    """Display the login/register interface."""
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem;">
            <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #7C3AED, #06B6D4);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-weight: 800;">🎓 AI Study Companion</h1>
            <p style="color: #94A3B8; font-size: 1.1rem; margin-top: 0.5rem;">
                Your intelligent learning assistant powered by AI
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Center the auth form
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("#### Welcome Back!")
                email = st.text_input("Email", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
                submitted = st.form_submit_button("Log In", use_container_width=True)

                if submitted:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = result
                        st.rerun()
                    else:
                        st.error(result)

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                st.markdown("#### Create Account")
                name = st.text_input("Full Name", placeholder="John Doe", key="reg_name")
                email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_password")
                password2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_password2")
                submitted = st.form_submit_button("Create Account", use_container_width=True)

                if submitted:
                    if password != password2:
                        st.error("Passwords do not match.")
                    else:
                        success, message = register_user(name, email, password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

    # Footer
    st.markdown("""
        <div style="text-align: center; padding: 3rem 0 1rem; color: #64748B; font-size: 0.85rem;">
            <p>🔒 Your data is stored locally and secured with bcrypt encryption</p>
        </div>
    """, unsafe_allow_html=True)


# ── Sidebar Navigation ────────────────────────────────────
def show_sidebar():
    """Render the sidebar with user info, navigation, and controls."""
    user = get_current_user()
    with st.sidebar:
        # App branding
        st.markdown("""
            <div style="text-align: center; padding: 0.5rem 0 1rem;">
                <h2 style="background: linear-gradient(135deg, #A78BFA, #67E8F9);
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                           font-weight: 800; font-size: 1.4rem; margin: 0;">
                    🎓 AI Study Companion
                </h2>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # User profile
        if user:
            st.markdown(f"""
                <div style="background: rgba(124, 58, 237, 0.1); border-radius: 12px;
                            padding: 1rem; margin-bottom: 1rem; border: 1px solid rgba(124, 58, 237, 0.2);">
                    <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;
                                letter-spacing: 0.05em;">Logged in as</div>
                    <div style="font-weight: 600; color: #F1F5F9; font-size: 1rem; margin-top: 0.2rem;">
                        👤 {user['name']}
                    </div>
                    <div style="font-size: 0.85rem; color: #94A3B8;">{user['email']}</div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()


# ── Main Routing ───────────────────────────────────────────
if not is_authenticated():
    show_auth_page()
else:
    show_sidebar()

    # Define pages
    pages = [
        st.Page("pages/1_🏠_Home.py", title="Home", icon="🏠"),
        st.Page("pages/2_📄_Upload_Documents.py", title="Upload Documents", icon="📄"),
        st.Page("pages/3_📝_AI_Summary.py", title="AI Summary", icon="📝"),
        st.Page("pages/4_❓_Ask_Questions.py", title="Ask Questions", icon="❓"),
        st.Page("pages/5_🧪_Quiz_Generator.py", title="Quiz Generator", icon="🧪"),
        st.Page("pages/6_🃏_Flashcards.py", title="Flashcards", icon="🃏"),
        st.Page("pages/7_📅_Study_Planner.py", title="Study Planner", icon="📅"),
        st.Page("pages/8_📊_Progress_Dashboard.py", title="Progress Dashboard", icon="📊"),
        st.Page("pages/9_📬_Contact.py", title="Contact", icon="📬"),
    ]

    pg = st.navigation(pages)
    pg.run()
