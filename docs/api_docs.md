# Internal API Documentation

This document describes the primary functions, parameters, and return types within the AI Study Companion utility layers.

## 1. Database Module (`database/db.py`)
Provides SQLite CRUD and metrics queries.

### `init_db()`
Initialize tables: `users`, `documents`, `quiz_results`, `flashcards`, `study_plans`, `chat_history`, `contact_messages`.

### `create_user(name, email, password_hash)`
*   **Args**: `name` (str), `email` (str), `password_hash` (str)
*   **Returns**: `int` (newly created user's ID) or `None` if email is already registered.

### `get_user_stats(user_id)`
*   **Args**: `user_id` (int)
*   **Returns**: `dict` containing metrics: `total_docs`, `total_quizzes`, `avg_score`, `total_flashcards`, `study_streak`, `recent_quizzes` (list), and `docs_by_date` (list).

---

## 2. AI Engine Module (`utils/ai_engine.py`)
Handles calls to the Google Generative AI (`google-genai`) SDK.

### `generate_summary(text)`
*   **Args**: `text` (str) - Raw text extracted from document.
*   **Returns**: `str` - Markdown formatted summary.

### `generate_quiz(text, num_questions=5)`
*   **Args**: `text` (str), `num_questions` (int)
*   **Returns**: `list[dict]` - List of MCQs with keys `question`, `options`, `correct_answer`, and `explanation`.

### `get_embeddings(texts)`
*   **Args**: `texts` (list[str])
*   **Returns**: `list[list[float]]` - High-dimensional vector lists generated via model `text-embedding-004`.

---

## 3. FAISS Store Module (`utils/vector_store.py`)
Wraps FAISS index creation and querying.

### `create_index(chunks, user_id, doc_id)`
*   **Args**: `chunks` (list[str]), `user_id` (int), `doc_id` (int)
*   **Returns**: `bool` - True if index saves successfully to `/vectorstore/{user_id}/{doc_id}/index.faiss`.

### `search(query, user_id, doc_id, k=5)`
*   **Args**: `query` (str), `user_id` (int), `doc_id` (int), `k` (int)
*   **Returns**: `list[str]` - Matching chunks from `chunks.json`.
