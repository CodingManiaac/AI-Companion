"""
Shared UI helpers for AI Study Companion.
CSS loading, session state initialization, metric cards, and download utilities.
"""

import os
import streamlit as st


def load_css():
    """Load and inject the custom CSS stylesheet."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_session_state():
    """Initialize all session state keys with defaults."""
    defaults = {
        "authenticated": False,
        "user": None,
        "current_page": "Home",
        "dark_mode": True,
        # Quiz state
        "quiz_data": None,
        "quiz_submitted": False,
        "quiz_answers": {},
        "quiz_score": None,
        # Flashcard state
        "flashcards": [],
        "flashcard_index": 0,
        "flashcard_flipped": False,
        # Chat state
        "chat_messages": [],
        "current_doc_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_metric_card(title: str, value: str | int, icon: str, color: str = "purple"):
    """
    Render a styled metric card.

    Args:
        title: Card label text.
        value: The metric value to display.
        icon: Emoji icon.
        color: Color variant (purple, blue, green, amber, cyan, rose).
    """
    st.markdown(f"""
        <div class="metric-card {color}">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
        </div>
    """, unsafe_allow_html=True)


def render_feature_card(icon: str, title: str, description: str):
    """Render a feature showcase card."""
    st.markdown(f"""
        <div class="feature-card animate-fade-in-up">
            <span class="icon">{icon}</span>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = ""):
    """Render a styled section header with optional subtitle."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
        <div class="section-header">
            <h2>{title}</h2>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, message: str):
    """Render an empty state placeholder."""
    st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)


def render_document_card(doc: dict):
    """Render a document list item card."""
    upload_date = doc.get("upload_date", "Unknown date")
    if isinstance(upload_date, str) and len(upload_date) > 10:
        upload_date = upload_date[:10]  # Show date only

    st.markdown(f"""
        <div class="doc-card">
            <div class="doc-icon">📄</div>
            <div class="doc-info">
                <h4>{doc['file_name']}</h4>
                <p>Uploaded: {upload_date}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def generate_download_html(title: str, content: str, include_style: bool = True) -> str:
    """
    Generate a styled HTML document for download.

    Args:
        title: Document title.
        content: Markdown or HTML content.
        include_style: Whether to include CSS styling.

    Returns:
        Complete HTML string.
    """
    style = ""
    if include_style:
        style = """
        <style>
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 0 20px;
                line-height: 1.6;
                color: #1a1a1a;
            }
            h1 { color: #7C3AED; border-bottom: 2px solid #7C3AED; padding-bottom: 10px; }
            h2 { color: #5B21B6; margin-top: 2em; }
            h3 { color: #6D28D9; }
            .question { background: #F5F3FF; border-left: 4px solid #7C3AED; padding: 12px 16px; margin: 16px 0; border-radius: 0 8px 8px 0; }
            .answer { background: #ECFDF5; border-left: 4px solid #10B981; padding: 12px 16px; margin: 8px 0 16px; border-radius: 0 8px 8px 0; }
            .correct { color: #10B981; font-weight: bold; }
            .incorrect { color: #EF4444; font-weight: bold; }
            table { border-collapse: collapse; width: 100%; margin: 16px 0; }
            th, td { border: 1px solid #E2E8F0; padding: 10px 14px; text-align: left; }
            th { background: #7C3AED; color: white; }
            tr:nth-child(even) { background: #F8FAFC; }
            .header-info { color: #64748B; font-size: 0.9em; margin-bottom: 2em; }
            @media print { body { margin: 20px; } }
        </style>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AI Study Companion</title>
    {style}
</head>
<body>
    <h1>📚 {title}</h1>
    <div class="header-info">Generated by AI Study Companion</div>
    {content}
</body>
</html>"""
