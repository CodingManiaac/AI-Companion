"""
Study Planner Page – AI Study Companion
AI-generated personalized study schedules based on subjects, exam date, and daily hours.
"""

import streamlit as st
import json
from datetime import date, timedelta
from utils.auth import require_auth, get_current_user
from utils.helpers import render_section_header, render_empty_state, generate_download_html
from utils.ai_engine import generate_study_plan
from database.db import save_study_plan, get_user_study_plans

require_auth()
user = get_current_user()

# ── Header ─────────────────────────────────────────────────
render_section_header(
    "📅 Study Planner",
    "Get an AI-generated personalized study schedule tailored to your goals"
)

tab_create, tab_saved = st.tabs(["✨ Create New Plan", "📋 Saved Plans"])

with tab_create:
    st.markdown("### 📝 Enter Your Study Details")

    with st.form("study_plan_form"):
        # Subjects input
        subjects_input = st.text_area(
            "📚 Subjects (one per line)",
            placeholder="Mathematics\nPhysics\nChemistry\nBiology",
            height=120,
            help="Enter each subject on a new line"
        )

        col1, col2 = st.columns(2)
        with col1:
            exam_date = st.date_input(
                "📅 Exam Date",
                value=date.today() + timedelta(days=14),
                min_value=date.today() + timedelta(days=1),
                help="When is your exam?"
            )
        with col2:
            daily_hours = st.slider(
                "⏰ Daily Study Hours",
                min_value=1.0,
                max_value=12.0,
                value=4.0,
                step=0.5,
                help="How many hours can you study per day?"
            )

        submitted = st.form_submit_button("✨ Generate Study Plan", use_container_width=True)

    if submitted:
        # Parse subjects
        subjects = [s.strip() for s in subjects_input.strip().split("\n") if s.strip()]
        if not subjects:
            st.error("❌ Please enter at least one subject.")
        else:
            days_until = (exam_date - date.today()).days
            st.info(f"📊 Planning for **{len(subjects)} subjects** over **{days_until} days** with **{daily_hours}h/day**")

            with st.spinner("🤖 AI is creating your personalized study plan..."):
                plan = generate_study_plan(subjects, exam_date.isoformat(), daily_hours)
                if plan:
                    st.session_state["current_plan"] = plan
                    st.session_state["plan_subjects"] = subjects
                    st.session_state["plan_exam_date"] = exam_date.isoformat()
                else:
                    st.error("❌ Failed to generate study plan. Please try again.")

    # Display generated plan
    if st.session_state.get("current_plan"):
        plan = st.session_state["current_plan"]

        st.divider()

        # Overview
        if plan.get("overview"):
            st.markdown("### 📋 Strategy Overview")
            st.markdown(plan["overview"])

        # Schedule table
        if plan.get("schedule"):
            st.markdown("### 📅 Daily Schedule")

            schedule = plan["schedule"]
            # Display as a styled table
            table_html = '<table class="plan-table"><thead><tr>'
            table_html += '<th>Day</th><th>Subject</th><th>Topics</th><th>Hours</th><th>Tasks</th>'
            table_html += '</tr></thead><tbody>'

            for entry in schedule:
                day = entry.get("day", "")
                subject = entry.get("subject", "")
                topics = entry.get("topics", "")
                hours = entry.get("hours", "")
                tasks = entry.get("tasks", [])
                tasks_str = "<br>".join(f"• {t}" for t in tasks) if isinstance(tasks, list) else str(tasks)

                table_html += f'<tr><td><strong>{day}</strong></td><td>{subject}</td>'
                table_html += f'<td>{topics}</td><td>{hours}h</td><td>{tasks_str}</td></tr>'

            table_html += '</tbody></table>'
            st.markdown(table_html, unsafe_allow_html=True)

        # Tips
        if plan.get("tips"):
            st.markdown("### 💡 Study Tips")
            for tip in plan["tips"]:
                st.markdown(f"- {tip}")

        st.divider()

        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save This Plan", use_container_width=True):
                plan_data = {
                    "subjects": st.session_state.get("plan_subjects", []),
                    "exam_date": st.session_state.get("plan_exam_date", ""),
                    "plan": plan,
                }
                save_study_plan(user["id"], plan_data)
                st.success("✅ Study plan saved!")

        with col2:
            # Download as HTML
            plan_html = f"<h2>Strategy Overview</h2><p>{plan.get('overview', '')}</p>"
            plan_html += "<h2>Schedule</h2>" + table_html if plan.get("schedule") else ""
            if plan.get("tips"):
                plan_html += "<h2>Study Tips</h2><ul>"
                for tip in plan["tips"]:
                    plan_html += f"<li>{tip}</li>"
                plan_html += "</ul>"

            download_html = generate_download_html("Study Plan", plan_html)
            st.download_button(
                "📥 Download Plan",
                data=download_html,
                file_name="study_plan.html",
                mime="text/html",
                use_container_width=True,
            )

with tab_saved:
    st.markdown("### 📋 Your Saved Plans")
    saved_plans = get_user_study_plans(user["id"])

    if not saved_plans:
        render_empty_state(
            "📅",
            "No saved plans",
            "Generate and save a study plan to view it here later."
        )
    else:
        for i, sp in enumerate(saved_plans):
            plan_data = sp.get("plan_data", {})
            subjects = plan_data.get("subjects", [])
            exam_date = plan_data.get("exam_date", "Unknown")
            created = str(sp.get("created_at", ""))[:10]

            with st.expander(f"📅 Plan for {', '.join(subjects[:3])}{'...' if len(subjects) > 3 else ''} — Exam: {exam_date} (Created: {created})"):
                plan = plan_data.get("plan", {})

                if plan.get("overview"):
                    st.markdown(f"**Overview:** {plan['overview']}")

                if plan.get("schedule"):
                    st.markdown("**Schedule:**")
                    for entry in plan["schedule"][:10]:  # Show first 10 days
                        day = entry.get("day", "")
                        subject = entry.get("subject", "")
                        hours = entry.get("hours", "")
                        st.markdown(f"- **{day}**: {subject} ({hours}h)")
                    if len(plan["schedule"]) > 10:
                        st.caption(f"...and {len(plan['schedule']) - 10} more days")

                if plan.get("tips"):
                    st.markdown("**Tips:**")
                    for tip in plan["tips"][:5]:
                        st.markdown(f"- {tip}")
