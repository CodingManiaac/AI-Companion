"""
Database manager for AI Study Companion.
Handles SQLite initialization, table creation, and all CRUD operations.
"""

import sqlite3
import json
import os
from datetime import datetime, date

# Database file path (relative to project root)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "study_companion.db")


def get_connection():
    """Get a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database and create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            text_content TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Quiz results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_id INTEGER,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            quiz_data TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
        )
    """)

    # Flashcards table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
        )
    """)

    # Study plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
        )
    """)

    # Contact messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            message_type TEXT DEFAULT 'contact',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ── User CRUD ──────────────────────────────────────────────

def create_user(name: str, email: str, password_hash: str) -> int | None:
    """Create a new user. Returns user id on success, None if email exists."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None


def get_user_by_email(email: str) -> dict | None:
    """Fetch a user by email. Returns dict or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> dict | None:
    """Fetch a user by ID. Returns dict or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_user(user_id: int, name: str = None, email: str = None, password_hash: str = None):
    """Update user fields. Only non-None fields are updated."""
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    values = []
    if name is not None:
        updates.append("name = ?")
        values.append(name)
    if email is not None:
        updates.append("email = ?")
        values.append(email)
    if password_hash is not None:
        updates.append("password_hash = ?")
        values.append(password_hash)
    if updates:
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    conn.close()


# ── Document CRUD ──────────────────────────────────────────

def save_document(user_id: int, file_name: str, file_path: str, text_content: str = None) -> int:
    """Save an uploaded document record. Returns document id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, file_name, file_path, text_content) VALUES (?, ?, ?, ?)",
        (user_id, file_name, file_path, text_content)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id


def get_user_documents(user_id: int) -> list[dict]:
    """Get all documents for a user, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, file_name, file_path, upload_date FROM documents WHERE user_id = ? ORDER BY upload_date DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_document_by_id(doc_id: int) -> dict | None:
    """Get a single document by its ID, including text content."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def delete_document(doc_id: int):
    """Delete a document and its associated data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()


def search_documents(user_id: int, query: str) -> list[dict]:
    """Search documents by filename for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, file_name, file_path, upload_date FROM documents WHERE user_id = ? AND file_name LIKE ? ORDER BY upload_date DESC",
        (user_id, f"%{query}%")
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Quiz Results CRUD ──────────────────────────────────────

def save_quiz_result(user_id: int, document_id: int, score: int, total_questions: int, quiz_data: list = None) -> int:
    """Save a quiz result. quiz_data is a JSON-serializable list of question dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    quiz_json = json.dumps(quiz_data) if quiz_data else None
    cursor.execute(
        "INSERT INTO quiz_results (user_id, document_id, score, total_questions, quiz_data) VALUES (?, ?, ?, ?, ?)",
        (user_id, document_id, score, total_questions, quiz_json)
    )
    conn.commit()
    result_id = cursor.lastrowid
    conn.close()
    return result_id


def get_user_quiz_results(user_id: int, limit: int = 50) -> list[dict]:
    """Get quiz results for a user, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT qr.*, d.file_name
           FROM quiz_results qr
           LEFT JOIN documents d ON qr.document_id = d.id
           WHERE qr.user_id = ?
           ORDER BY qr.date DESC
           LIMIT ?""",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        if d.get("quiz_data"):
            d["quiz_data"] = json.loads(d["quiz_data"])
        results.append(d)
    return results


# ── Flashcard CRUD ─────────────────────────────────────────

def save_flashcard(user_id: int, document_id: int, question: str, answer: str) -> int:
    """Save a single flashcard. Returns flashcard id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO flashcards (user_id, document_id, question, answer) VALUES (?, ?, ?, ?)",
        (user_id, document_id, question, answer)
    )
    conn.commit()
    fc_id = cursor.lastrowid
    conn.close()
    return fc_id


def save_flashcards_bulk(user_id: int, document_id: int, cards: list[dict]) -> list[int]:
    """Save multiple flashcards at once. Each card must have 'question' and 'answer' keys."""
    conn = get_connection()
    cursor = conn.cursor()
    ids = []
    for card in cards:
        cursor.execute(
            "INSERT INTO flashcards (user_id, document_id, question, answer) VALUES (?, ?, ?, ?)",
            (user_id, document_id, card["question"], card["answer"])
        )
        ids.append(cursor.lastrowid)
    conn.commit()
    conn.close()
    return ids


def get_user_flashcards(user_id: int, document_id: int = None) -> list[dict]:
    """Get flashcards for a user, optionally filtered by document."""
    conn = get_connection()
    cursor = conn.cursor()
    if document_id:
        cursor.execute(
            "SELECT * FROM flashcards WHERE user_id = ? AND document_id = ? ORDER BY created_at DESC",
            (user_id, document_id)
        )
    else:
        cursor.execute(
            "SELECT f.*, d.file_name FROM flashcards f LEFT JOIN documents d ON f.document_id = d.id WHERE f.user_id = ? ORDER BY f.created_at DESC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_flashcard(flashcard_id: int):
    """Delete a single flashcard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
    conn.commit()
    conn.close()


# ── Study Plan CRUD ────────────────────────────────────────

def save_study_plan(user_id: int, plan_data: dict) -> int:
    """Save a study plan. plan_data is a JSON-serializable dict."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO study_plans (user_id, plan_data) VALUES (?, ?)",
        (user_id, json.dumps(plan_data))
    )
    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    return plan_id


def get_user_study_plans(user_id: int) -> list[dict]:
    """Get all study plans for a user, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM study_plans WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        if d.get("plan_data"):
            d["plan_data"] = json.loads(d["plan_data"])
        results.append(d)
    return results


# ── Chat History CRUD ──────────────────────────────────────

def save_chat_message(user_id: int, document_id: int, question: str, answer: str, sources: list = None) -> int:
    """Save a Q&A exchange to chat history."""
    conn = get_connection()
    cursor = conn.cursor()
    sources_json = json.dumps(sources) if sources else None
    cursor.execute(
        "INSERT INTO chat_history (user_id, document_id, question, answer, sources) VALUES (?, ?, ?, ?, ?)",
        (user_id, document_id, question, answer, sources_json)
    )
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id


def get_chat_history(user_id: int, document_id: int, limit: int = 50) -> list[dict]:
    """Get chat history for a user and document, oldest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM chat_history WHERE user_id = ? AND document_id = ? ORDER BY timestamp ASC LIMIT ?",
        (user_id, document_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        if d.get("sources"):
            d["sources"] = json.loads(d["sources"])
        results.append(d)
    return results


def clear_chat_history(user_id: int, document_id: int):
    """Clear chat history for a specific document."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM chat_history WHERE user_id = ? AND document_id = ?",
        (user_id, document_id)
    )
    conn.commit()
    conn.close()


# ── Contact Messages CRUD ─────────────────────────────────

def save_contact_message(name: str, email: str, subject: str, message: str, message_type: str = "contact") -> int:
    """Save a contact or feedback message."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contact_messages (name, email, subject, message, message_type) VALUES (?, ?, ?, ?, ?)",
        (name, email, subject, message, message_type)
    )
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id


# ── Dashboard / Stats ─────────────────────────────────────

def get_user_stats(user_id: int) -> dict:
    """Get aggregated statistics for the progress dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total documents uploaded
    cursor.execute("SELECT COUNT(*) as count FROM documents WHERE user_id = ?", (user_id,))
    total_docs = cursor.fetchone()["count"]

    # Total quizzes taken
    cursor.execute("SELECT COUNT(*) as count FROM quiz_results WHERE user_id = ?", (user_id,))
    total_quizzes = cursor.fetchone()["count"]

    # Average quiz score (percentage)
    cursor.execute(
        "SELECT AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_score FROM quiz_results WHERE user_id = ?",
        (user_id,)
    )
    avg_score_row = cursor.fetchone()
    avg_score = round(avg_score_row["avg_score"], 1) if avg_score_row["avg_score"] else 0

    # Total flashcards created
    cursor.execute("SELECT COUNT(*) as count FROM flashcards WHERE user_id = ?", (user_id,))
    total_flashcards = cursor.fetchone()["count"]

    # Total study plans
    cursor.execute("SELECT COUNT(*) as count FROM study_plans WHERE user_id = ?", (user_id,))
    total_plans = cursor.fetchone()["count"]

    # Total Q&A interactions
    cursor.execute("SELECT COUNT(*) as count FROM chat_history WHERE user_id = ?", (user_id,))
    total_questions = cursor.fetchone()["count"]

    # Study streak: count consecutive days (ending today) with any activity
    cursor.execute("""
        SELECT DISTINCT DATE(timestamp) as activity_date FROM (
            SELECT upload_date as timestamp FROM documents WHERE user_id = ?
            UNION ALL
            SELECT date as timestamp FROM quiz_results WHERE user_id = ?
            UNION ALL
            SELECT timestamp FROM chat_history WHERE user_id = ?
            UNION ALL
            SELECT created_at as timestamp FROM flashcards WHERE user_id = ?
        ) ORDER BY activity_date DESC
    """, (user_id, user_id, user_id, user_id))
    dates = [row["activity_date"] for row in cursor.fetchall()]

    streak = 0
    today = date.today().isoformat()
    if dates:
        # Check if there's activity today or yesterday to start the streak
        check_date = date.today()
        for d in dates:
            if d == check_date.isoformat():
                streak += 1
                check_date = check_date.replace(day=check_date.day) # move to previous day
                from datetime import timedelta
                check_date -= timedelta(days=1)
            else:
                # Allow today to be missing (streak continues from yesterday)
                if streak == 0 and d == (date.today() - __import__('datetime').timedelta(days=1)).isoformat():
                    streak += 1
                    check_date = date.today() - __import__('datetime').timedelta(days=2)
                else:
                    break

    # Recent quiz scores for chart
    cursor.execute(
        "SELECT score, total_questions, date, document_id FROM quiz_results WHERE user_id = ? ORDER BY date DESC LIMIT 20",
        (user_id,)
    )
    recent_quizzes = [dict(r) for r in cursor.fetchall()]

    # Documents uploaded by date for chart
    cursor.execute(
        "SELECT DATE(upload_date) as upload_day, COUNT(*) as count FROM documents WHERE user_id = ? GROUP BY upload_day ORDER BY upload_day",
        (user_id,)
    )
    docs_by_date = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "total_docs": total_docs,
        "total_quizzes": total_quizzes,
        "avg_score": avg_score,
        "total_flashcards": total_flashcards,
        "total_plans": total_plans,
        "total_questions": total_questions,
        "study_streak": streak,
        "recent_quizzes": recent_quizzes,
        "docs_by_date": docs_by_date,
    }
