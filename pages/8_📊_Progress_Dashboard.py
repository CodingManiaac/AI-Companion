"""
Progress Dashboard Page – AI Study Companion
Visualize learning statistics with Plotly charts and metric cards.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header, render_empty_state
from database.db import get_user_stats

require_auth()
user = get_current_user()

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "📊 Progress Dashboard",
    "Track your learning journey with detailed statistics and visualizations"
)

# ── Load Stats ─────────────────────────────────────────────
stats = get_user_stats(user["id"])

# ── Metric Cards Row ───────────────────────────────────────
col1, col2, col3, col4, col5, col6 = st.columns(6)

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
            <div class="metric-label">Quizzes</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card green">
            <div class="metric-icon">📈</div>
            <div class="metric-value">{stats['avg_score']}%</div>
            <div class="metric-label">Avg Score</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card cyan">
            <div class="metric-icon">🃏</div>
            <div class="metric-value">{stats['total_flashcards']}</div>
            <div class="metric-label">Flashcards</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="metric-card rose">
            <div class="metric-icon">💬</div>
            <div class="metric-value">{stats['total_questions']}</div>
            <div class="metric-label">Questions Asked</div>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
        <div class="metric-card amber">
            <div class="metric-icon">🔥</div>
            <div class="metric-value">{stats['study_streak']}</div>
            <div class="metric-label">Day Streak</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Check if there's enough data for charts
has_quiz_data = bool(stats.get("recent_quizzes"))
has_doc_data = bool(stats.get("docs_by_date"))

if not has_quiz_data and not has_doc_data:
    render_empty_state(
        "📊",
        "Not enough data yet",
        "Start uploading documents, taking quizzes, and asking questions to see your progress charts here!"
    )
    st.stop()

# ── Plotly Chart Styling ───────────────────────────────────
chart_layout = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E2E8F0", family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="rgba(148, 163, 184, 0.1)"),
    yaxis=dict(gridcolor="rgba(148, 163, 184, 0.1)"),
)

# ── Charts Row 1 ───────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📈 Quiz Score Trend")
    if has_quiz_data:
        quizzes = stats["recent_quizzes"]
        quizzes.reverse()  # Oldest first for trend

        df_quiz = pd.DataFrame(quizzes)
        df_quiz["percentage"] = (df_quiz["score"] / df_quiz["total_questions"] * 100).round(1)
        df_quiz["date"] = pd.to_datetime(df_quiz["date"])
        df_quiz["quiz_num"] = range(1, len(df_quiz) + 1)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_quiz["quiz_num"],
            y=df_quiz["percentage"],
            mode="lines+markers",
            line=dict(color="#7C3AED", width=3),
            marker=dict(size=8, color="#A78BFA"),
            fill="tozeroy",
            fillcolor="rgba(124, 58, 237, 0.1)",
            name="Score %",
        ))
        fig.update_layout(
            **chart_layout,
            xaxis_title="Quiz #",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 105], gridcolor="rgba(148, 163, 184, 0.1)"),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        render_empty_state("📈", "No quiz data", "Take quizzes to see your score trend.")

with col2:
    st.markdown("#### 📊 Score Distribution")
    if has_quiz_data:
        quizzes = stats["recent_quizzes"]
        percentages = [(q["score"] / q["total_questions"] * 100) for q in quizzes]

        # Create bins
        bins = {"0-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0}
        for p in percentages:
            if p < 40:
                bins["0-40%"] += 1
            elif p < 60:
                bins["40-60%"] += 1
            elif p < 80:
                bins["60-80%"] += 1
            else:
                bins["80-100%"] += 1

        fig = go.Figure(data=[go.Bar(
            x=list(bins.keys()),
            y=list(bins.values()),
            marker_color=["#EF4444", "#F59E0B", "#3B82F6", "#10B981"],
            text=list(bins.values()),
            textposition="auto",
        )])
        fig.update_layout(
            **chart_layout,
            xaxis_title="Score Range",
            yaxis_title="Count",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        render_empty_state("📊", "No data", "Complete quizzes to see distribution.")

# ── Charts Row 2 ───────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 Documents Uploaded Over Time")
    if has_doc_data:
        df_docs = pd.DataFrame(stats["docs_by_date"])
        df_docs["upload_day"] = pd.to_datetime(df_docs["upload_day"])
        df_docs["cumulative"] = df_docs["count"].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_docs["upload_day"],
            y=df_docs["count"],
            marker_color="#06B6D4",
            name="Uploaded",
        ))
        fig.add_trace(go.Scatter(
            x=df_docs["upload_day"],
            y=df_docs["cumulative"],
            mode="lines+markers",
            line=dict(color="#F59E0B", width=2),
            marker=dict(size=6),
            name="Cumulative",
            yaxis="y2",
        ))
        fig.update_layout(
            **chart_layout,
            yaxis_title="Uploaded",
            yaxis2=dict(
                title="Cumulative",
                overlaying="y",
                side="right",
                gridcolor="rgba(0,0,0,0)",
                color="#F59E0B",
            ),
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        render_empty_state("📄", "No uploads", "Upload documents to see this chart.")

with col2:
    st.markdown("#### 🏆 Learning Activity Summary")
    # Pie/donut chart of activity types
    activities = {
        "Documents Uploaded": stats["total_docs"],
        "Quizzes Taken": stats["total_quizzes"],
        "Flashcards Created": stats["total_flashcards"],
        "Questions Asked": stats["total_questions"],
        "Study Plans": stats["total_plans"],
    }
    # Filter out zeros
    activities = {k: v for k, v in activities.items() if v > 0}

    if activities:
        fig = go.Figure(data=[go.Pie(
            labels=list(activities.keys()),
            values=list(activities.values()),
            hole=0.45,
            marker=dict(colors=["#7C3AED", "#3B82F6", "#06B6D4", "#F59E0B", "#10B981"]),
            textinfo="label+value",
            textfont=dict(size=12),
        )])
        fig.update_layout(
            **chart_layout,
            height=350,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        render_empty_state("🏆", "No activity", "Start using the app to see your activity breakdown.")

# ── Recent Activity Feed ───────────────────────────────────
st.divider()
st.markdown("#### 🕐 Recent Quiz Results")

if has_quiz_data:
    for q in stats["recent_quizzes"][:5]:
        pct = round((q["score"] / q["total_questions"]) * 100)
        date_str = str(q.get("date", ""))[:16]
        badge_color = "success" if pct >= 80 else ("info" if pct >= 60 else ("warning" if pct >= 40 else "danger"))
        st.markdown(f"""
            🧪 Quiz on {date_str} — Score: **{q['score']}/{q['total_questions']}**
            <span class="badge badge-{badge_color}">{pct}%</span>
        """, unsafe_allow_html=True)
else:
    st.caption("No recent quizzes. Take a quiz to see results here!")
