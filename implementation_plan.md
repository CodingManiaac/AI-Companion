# AI Study Companion – Implementation Plan

## Overview

Build a fully functional AI-powered study companion web app using **Streamlit** (multipage), **SQLite**, **Google Gemini API** (via `google-genai` SDK), **FAISS**, and supporting libraries. The app enables students to upload PDFs, generate AI summaries, take quizzes, create flashcards, ask questions via RAG, plan study schedules, and track progress — all behind a user authentication wall.

---

## User Review Required

> [!IMPORTANT]
> **Gemini API Key**: You will need a valid Google Gemini API key. The app reads it from a `.env` file (`GEMINI_API_KEY=your_key`). Do you already have one, or should I include instructions for obtaining one from [Google AI Studio](https://aistudio.google.com/)?

> [!IMPORTANT]
> **SDK Choice**: Research shows `google-generativeai` is deprecated in favor of `google-genai`. I will use the **newer `google-genai` SDK** for both text generation and embeddings (`text-embedding-004` model, `gemini-2.0-flash` for generation). This is the current best practice.

> [!WARNING]
> **No LangChain**: To keep dependencies minimal and the code self-contained (as implied by your spec), I will use FAISS directly via `faiss-cpu` and call the Gemini embedding API directly — no LangChain dependency. This gives you full control over the RAG pipeline.

---

## Open Questions

1. **Dark mode**: Should dark mode be a toggle in the sidebar, or should the app follow the system theme? I'll default to a **sidebar toggle** that switches a CSS class.
2. **PDF storage**: Should uploaded PDFs be stored as files on disk (in `/uploads`), or only their extracted text in the database? I'll default to **both** (file on disk + extracted text in DB) for maximum flexibility.
3. **Quiz PDF download**: The spec mentions "Download quizzes as PDF". I'll use a simple HTML-to-PDF approach via `pdfkit` or generate a downloadable markdown. Since `pdfkit` requires `wkhtmltopdf` system dependency, I'll instead generate a **styled HTML download** that can be printed to PDF. Is that acceptable?

---

## Tech Stack & Versions

| Component | Package | Purpose |
|---|---|---|
| Frontend | `streamlit` | Multipage UI framework |
| Database | `sqlite3` (stdlib) | User data, quiz results, flashcards |
| AI Generation | `google-genai` | Summaries, quizzes, flashcards, Q&A, study plans |
| Embeddings | `google-genai` (`text-embedding-004`) | Document vectorization for RAG |
| Vector Store | `faiss-cpu` | Similarity search |
| PDF Parsing | `pdfplumber` | Text extraction from PDFs |
| Auth | `bcrypt` | Password hashing |
| Charts | `plotly` | Progress dashboard visualizations |
| Config | `python-dotenv` | Environment variable management |
| Data | `pandas` | Data manipulation |
| Misc | `numpy` | FAISS vector operations |

---

## Project Structure

```
c:\AI Companion\
├── app.py                    # Main entry point with navigation
├── requirements.txt          # Python dependencies
├── .env.example              # Template for API keys
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── README.md                 # Project documentation
├── database/
│   ├── __init__.py
│   └── db.py                 # SQLite init, CRUD operations
├── uploads/                  # Uploaded PDF storage (gitignored)
├── vectorstore/              # FAISS index storage (gitignored)
├── utils/
│   ├── __init__.py
│   ├── auth.py               # Authentication helpers
│   ├── pdf_processor.py      # PDF text extraction & chunking
│   ├── ai_engine.py          # Gemini API wrapper (summaries, Q&A, quizzes, etc.)
│   ├── vector_store.py       # FAISS index management
│   └── helpers.py            # Shared UI helpers, dark mode, etc.
├── pages/
│   ├── 1_🏠_Home.py
│   ├── 2_📄_Upload_Documents.py
│   ├── 3_📝_AI_Summary.py
│   ├── 4_❓_Ask_Questions.py
│   ├── 5_🧪_Quiz_Generator.py
│   ├── 6_🃏_Flashcards.py
│   ├── 7_📅_Study_Planner.py
│   ├── 8_📊_Progress_Dashboard.py
│   └── 9_📬_Contact.py
├── assets/
│   └── style.css             # Custom CSS for premium look
└── docs/
    ├── SRS.md                # Software Requirement Specification
    ├── architecture.md       # System Architecture Diagram (Mermaid)
    ├── er_diagram.md         # Database ER Diagram (Mermaid)
    ├── workflow.md           # Workflow Diagram (Mermaid)
    └── api_docs.md           # API Documentation
```

---

## Proposed Changes

### 1. Foundation & Configuration

#### [NEW] [requirements.txt](file:///c:/AI Companion/requirements.txt)
All dependencies with pinned versions:
- `streamlit`, `google-genai`, `faiss-cpu`, `pdfplumber`, `bcrypt`, `plotly`, `pandas`, `numpy`, `python-dotenv`

#### [NEW] [.env.example](file:///c:/AI Companion/.env.example)
Template: `GEMINI_API_KEY=your_api_key_here`

#### [NEW] [config.toml](file:///c:/AI Companion/.streamlit/config.toml)
Streamlit theme config with dark primary colors, custom font, wide layout

#### [NEW] [style.css](file:///c:/AI Companion/assets/style.css)
Premium CSS with:
- CSS custom properties for light/dark theme tokens
- Glassmorphism card styles
- Gradient headers and buttons
- Smooth transitions and micro-animations
- Responsive breakpoints
- Custom sidebar styling
- Card hover effects
- Quiz/flashcard component styles

---

### 2. Database Layer

#### [NEW] [db.py](file:///c:/AI Companion/database/db.py)
SQLite database manager with these tables and operations:

**Tables:**
- `users` (id, name, email, password_hash, created_at)
- `documents` (id, user_id FK, file_name, file_path, text_content, upload_date)
- `quiz_results` (id, user_id FK, document_id FK, score, total_questions, quiz_data JSON, date)
- `flashcards` (id, user_id FK, document_id FK, question, answer, created_at)
- `study_plans` (id, user_id FK, plan_data JSON, created_at)
- `chat_history` (id, user_id FK, document_id FK, question, answer, timestamp)
- `contact_messages` (id, name, email, message, created_at)

**CRUD Functions:**
- `init_db()` — create tables if not exist
- `create_user()`, `get_user_by_email()`, `update_user()`
- `save_document()`, `get_user_documents()`, `get_document_by_id()`, `delete_document()`
- `save_quiz_result()`, `get_user_quiz_results()`
- `save_flashcard()`, `get_user_flashcards()`, `delete_flashcard()`
- `save_study_plan()`, `get_user_study_plans()`
- `save_chat_message()`, `get_chat_history()`
- `save_contact_message()`
- `get_user_stats()` — aggregated stats for dashboard

---

### 3. Utility Modules

#### [NEW] [auth.py](file:///c:/AI Companion/utils/auth.py)
- `hash_password(password)` → bcrypt hash
- `verify_password(password, hash)` → bool
- `register_user(name, email, password)` → success/error
- `login_user(email, password)` → user dict or None
- `require_auth()` → decorator/guard that checks `st.session_state` and shows login if unauthenticated
- `logout()` → clear session state

#### [NEW] [pdf_processor.py](file:///c:/AI Companion/utils/pdf_processor.py)
- `extract_text(file_path)` → full text string using pdfplumber
- `chunk_text(text, chunk_size=1000, overlap=200)` → list of text chunks for embedding
- `extract_pages(file_path)` → list of (page_num, text) tuples

#### [NEW] [ai_engine.py](file:///c:/AI Companion/utils/ai_engine.py)
Gemini API wrapper using `google-genai`:
- `get_client()` → cached genai.Client
- `generate_summary(text)` → concise summary
- `generate_key_points(text)` → bullet point key points
- `generate_chapter_summary(text, chapter_info)` → per-chapter summary
- `answer_question(question, context)` → RAG answer
- `generate_quiz(text, num_questions=5)` → JSON array of MCQs with options and correct answer
- `generate_flashcards(text, num_cards=10)` → JSON array of {question, answer}
- `generate_study_plan(subjects, exam_date, daily_hours)` → structured study schedule
- All functions return structured Python objects (parsed from JSON responses)

#### [NEW] [vector_store.py](file:///c:/AI Companion/utils/vector_store.py)
FAISS integration (no LangChain):
- `get_embeddings(texts)` → numpy array using `google-genai` embed_content
- `create_index(chunks, user_id, doc_id)` → build and save FAISS index
- `load_index(user_id, doc_id)` → load from disk
- `search(query, user_id, doc_id, k=5)` → list of relevant chunks
- Index saved per user per document in `vectorstore/{user_id}/{doc_id}/`

#### [NEW] [helpers.py](file:///c:/AI Companion/utils/helpers.py)
- `load_css()` → inject custom CSS
- `init_session_state()` → initialize all session state keys
- `sidebar_nav()` → render sidebar with user info, dark mode toggle
- `show_metric_card(title, value, icon, color)` → styled metric card
- `download_as_html(content, filename)` → generate downloadable HTML

---

### 4. Page Implementations

#### [NEW] [app.py](file:///c:/AI Companion/app.py)
Main entry point:
- Set page config (wide layout, custom icon)
- Initialize database
- Load CSS
- Initialize session state
- Render login/register forms if not authenticated
- Configure `st.navigation()` with all pages
- Show sidebar with user profile, navigation, dark mode toggle, logout

#### [NEW] [1_🏠_Home.py](file:///c:/AI Companion/pages/1_🏠_Home.py)
Landing page with:
- Hero section with gradient background and tagline
- Feature cards grid (6 cards with icons for each feature)
- Call-to-action buttons ("Upload Documents", "Start Quiz", etc.)
- Animated statistics counters
- Modern responsive layout

#### [NEW] [2_📄_Upload_Documents.py](file:///c:/AI Companion/pages/2_📄_Upload_Documents.py)
- `st.file_uploader` for PDF files (multiple)
- Upload progress bar
- Extract text using pdfplumber
- Save file to `uploads/` and metadata + text to DB
- Build FAISS index for uploaded document
- Display uploaded documents list with search/filter
- Delete document functionality
- Show document preview (first page text)

#### [NEW] [3_📝_AI_Summary.py](file:///c:/AI Companion/pages/3_📝_AI_Summary.py)
- Document selector dropdown
- Three summary modes: Concise Summary, Key Points, Chapter-wise
- Generate button with loading spinner
- Display formatted summary with markdown
- Download summary as HTML
- History of generated summaries

#### [NEW] [4_❓_Ask_Questions.py](file:///c:/AI Companion/pages/4_❓_Ask_Questions.py)
- Document selector
- Chat-style interface using `st.chat_message`
- User types question → search FAISS for relevant chunks → send to Gemini with context → display answer
- Chat history persistence (saved to DB)
- Clear chat button
- Show source chunks used for the answer

#### [NEW] [5_🧪_Quiz_Generator.py](file:///c:/AI Companion/pages/5_🧪_Quiz_Generator.py)
- Document selector
- Number of questions slider (5-20)
- Generate quiz button
- Display MCQs with radio buttons for each
- Submit quiz → calculate score → show results with correct/incorrect indicators
- Save score to DB
- Download quiz as HTML

#### [NEW] [6_🃏_Flashcards.py](file:///c:/AI Companion/pages/6_🃏_Flashcards.py)
- Document selector
- Generate flashcards button (number selector)
- Interactive card flip animation (CSS-based)
- Navigation: Previous / Next with card counter
- Save/delete individual flashcards
- Browse saved flashcards
- Download all flashcards

#### [NEW] [7_📅_Study_Planner.py](file:///c:/AI Companion/pages/7_📅_Study_Planner.py)
- Input form: subjects (multi-input), exam date (date picker), daily study hours (slider)
- Generate plan button
- Display AI-generated schedule in a table/calendar view
- Save plan for future reference
- View saved plans

#### [NEW] [8_📊_Progress_Dashboard.py](file:///c:/AI Companion/pages/8_📊_Progress_Dashboard.py)
- Metric cards row: PDFs uploaded, quizzes completed, avg score, study streak
- Plotly charts:
  - Quiz score trend line chart
  - Quiz scores distribution bar chart
  - Documents uploaded over time
  - Subject-wise performance (if data available)
- Recent activity feed
- Learning statistics summary

#### [NEW] [9_📬_Contact.py](file:///c:/AI Companion/pages/9_📬_Contact.py)
- Contact form (name, email, subject, message)
- Feedback form (rating, comments)
- Save to database
- Success confirmation with animation

---

### 5. Documentation

#### [NEW] [README.md](file:///c:/AI Companion/README.md)
Complete project documentation with setup instructions, features, screenshots placeholders, deployment guide

#### [NEW] [SRS.md](file:///c:/AI Companion/docs/SRS.md)
Software Requirements Specification covering functional/non-functional requirements, use cases

#### [NEW] [architecture.md](file:///c:/AI Companion/docs/architecture.md)
System architecture diagram using Mermaid showing component interactions

#### [NEW] [er_diagram.md](file:///c:/AI Companion/docs/er_diagram.md)
Database ER diagram using Mermaid

#### [NEW] [workflow.md](file:///c:/AI Companion/docs/workflow.md)
User workflow diagrams using Mermaid

#### [NEW] [api_docs.md](file:///c:/AI Companion/docs/api_docs.md)
Internal API documentation for all utility functions

---

## Verification Plan

### Automated Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Verify database initialization
python -c "from database.db import init_db; init_db(); print('DB OK')"

# Run the app
streamlit run app.py
```

### Manual Verification
1. **Auth flow**: Register a new user → login → verify session persists across pages → logout
2. **Upload**: Upload a sample PDF → verify text extraction → verify FAISS index creation
3. **Summary**: Select uploaded doc → generate all 3 summary types → download
4. **RAG Q&A**: Ask questions about uploaded document → verify relevant answers
5. **Quiz**: Generate quiz → answer questions → submit → verify score saved
6. **Flashcards**: Generate → flip cards → save → browse saved
7. **Study Planner**: Enter subjects/date → generate plan → save
8. **Dashboard**: Verify all metrics and charts render with real data
9. **Contact**: Submit form → verify saved to DB
10. **Dark Mode**: Toggle → verify all components render correctly in both themes
