"""
AI Engine for AI Study Companion.
Wraps Google Gemini API (google-genai SDK) for all AI operations:
summaries, Q&A, quiz generation, flashcards, and study planning.
"""

import json
import os
import streamlit as st
from google import genai
from google.genai import errors
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model identifiers
GENERATION_MODEL = "gemini-2.0-flash"
EMBEDDING_MODEL = "text-embedding-004"


def get_client() -> genai.Client:
    """Get or create a cached Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found. Please add it to your `.env` file.")
        st.stop()
    return genai.Client(api_key=api_key)


def _generate(prompt: str, system_instruction: str = None) -> str:
    """Internal helper: generate text content via Gemini."""
    try:
        client = get_client()
        config = {}
        if system_instruction:
            config = genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
            response = client.models.generate_content(
                model=GENERATION_MODEL,
                contents=prompt,
                config=config,
            )
        else:
            response = client.models.generate_content(
                model=GENERATION_MODEL,
                contents=prompt,
            )
        return response.text
    except errors.APIError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            st.error("⚠️ **Gemini API Quota Exceeded (429)**: You have exceeded your free tier rate limits or daily requests quota. Please wait a minute or switch to a pay-as-you-go / higher limit API key.")
        else:
            st.error(f"⚠️ **Gemini API Error**: {e.message if hasattr(e, 'message') else str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Unexpected API Error**: {str(e)}")
        st.stop()


def _generate_json(prompt: str, system_instruction: str = None) -> list | dict:
    """Internal helper: generate JSON-structured content via Gemini."""
    try:
        client = get_client()
        config = genai.types.GenerateContentConfig(
            system_instruction=system_instruction or "You are a helpful assistant. Always respond with valid JSON only, no markdown fences.",
            temperature=0.7,
            response_mime_type="application/json",
        )
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config=config,
        )
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response text
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(text)
    except errors.APIError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            st.error("⚠️ **Gemini API Quota Exceeded (429)**: You have exceeded your free tier rate limits or daily requests quota. Please wait a minute or switch to a pay-as-you-go / higher limit API key.")
        else:
            st.error(f"⚠️ **Gemini API Error**: {e.message if hasattr(e, 'message') else str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Unexpected API Error**: {str(e)}")
        st.stop()


# ── Summary Generation ─────────────────────────────────────

def generate_summary(text: str) -> str:
    """Generate a concise summary of the given text."""
    prompt = f"""Summarize the following study material in a clear, concise manner.
Focus on the most important concepts and provide a well-structured summary
that a student can use for revision.

Text:
{text[:15000]}

Provide a comprehensive summary in markdown format with clear headings and bullet points where appropriate."""

    return _generate(prompt, system_instruction="You are an expert academic tutor who creates excellent study summaries.")


def generate_key_points(text: str) -> str:
    """Extract key points from the given text."""
    prompt = f"""Extract the most important key points from the following study material.
Present them as clear, numbered bullet points that capture the essential knowledge.

Text:
{text[:15000]}

Format the output as a numbered list of key points. Each point should be concise but informative."""

    return _generate(prompt, system_instruction="You are an expert at distilling complex material into key takeaways.")


def generate_chapter_summary(text: str) -> str:
    """Generate chapter-wise or section-wise summary."""
    prompt = f"""Analyze the following study material and create a chapter-wise or section-wise summary.
Identify the major topics/sections and summarize each one separately.

Text:
{text[:15000]}

Format the output with clear section headings (##) and concise summaries for each section.
Include key terms and concepts for each section."""

    return _generate(prompt, system_instruction="You are an expert academic tutor who creates structured chapter-wise study summaries.")


# ── Question Answering (RAG) ──────────────────────────────

def answer_question(question: str, context: str, chat_history: list = None) -> str:
    """
    Answer a question using the provided context (retrieved from FAISS).
    Optionally includes recent chat history for conversational context.
    """
    history_text = ""
    if chat_history:
        recent = chat_history[-5:]  # Last 5 exchanges
        history_lines = []
        for msg in recent:
            history_lines.append(f"Student: {msg['question']}")
            history_lines.append(f"Tutor: {msg['answer'][:200]}...")
        history_text = f"\nRecent conversation:\n" + "\n".join(history_lines) + "\n"

    prompt = f"""You are an AI study tutor. Answer the student's question using ONLY the provided context.
If the context doesn't contain enough information to answer, say so clearly.
{history_text}
Context from study material:
{context}

Student's Question: {question}

Provide a clear, educational answer. Use examples where helpful. Format with markdown."""

    return _generate(prompt, system_instruction="You are a knowledgeable, patient study tutor. Answer questions accurately based on the provided study material context.")


# ── Quiz Generation ────────────────────────────────────────

def generate_quiz(text: str, num_questions: int = 5) -> list[dict]:
    """
    Generate multiple-choice quiz questions from the given text.

    Returns a list of dicts:
    [
        {
            "question": "...",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct_answer": "A",
            "explanation": "..."
        },
        ...
    ]
    """
    prompt = f"""Generate exactly {num_questions} multiple-choice quiz questions from the following study material.

Study Material:
{text[:15000]}

For each question, provide:
- A clear question
- Exactly 4 options labeled A, B, C, D
- The correct answer letter (A, B, C, or D)
- A brief explanation of why the correct answer is right

Return as a JSON array of objects with keys: "question", "options" (array of 4 strings prefixed with "A) ", "B) ", "C) ", "D) "), "correct_answer" (single letter), "explanation"."""

    system = "You are an expert quiz creator. Create challenging but fair questions that test understanding, not just memorization. Always return valid JSON."

    result = _generate_json(prompt, system_instruction=system)

    # Validate and normalize the result
    if isinstance(result, dict) and "questions" in result:
        result = result["questions"]

    validated = []
    for q in result[:num_questions]:
        if all(k in q for k in ("question", "options", "correct_answer")):
            # Ensure exactly 4 options
            if len(q["options"]) >= 4:
                q["options"] = q["options"][:4]
                validated.append(q)

    return validated


# ── Flashcard Generation ───────────────────────────────────

def generate_flashcards(text: str, num_cards: int = 10) -> list[dict]:
    """
    Generate flashcards from the given text.

    Returns a list of dicts:
    [
        {"question": "...", "answer": "..."},
        ...
    ]
    """
    prompt = f"""Generate exactly {num_cards} flashcards from the following study material.
Each flashcard should have a clear question on one side and a concise, informative answer on the other.
Focus on key concepts, definitions, and important facts.

Study Material:
{text[:15000]}

Return as a JSON array of objects with keys: "question" and "answer"."""

    system = "You are an expert at creating effective study flashcards. Questions should be specific and answers should be concise but complete. Always return valid JSON."

    result = _generate_json(prompt, system_instruction=system)

    if isinstance(result, dict) and "flashcards" in result:
        result = result["flashcards"]

    validated = []
    for card in result[:num_cards]:
        if "question" in card and "answer" in card:
            validated.append({
                "question": card["question"],
                "answer": card["answer"]
            })

    return validated


# ── Study Plan Generation ─────────────────────────────────

def generate_study_plan(subjects: list[str], exam_date: str, daily_hours: float) -> dict:
    """
    Generate a personalized study plan.

    Returns a dict with:
    {
        "overview": "...",
        "schedule": [
            {"day": "Day 1 - Mon Jul 7", "subject": "...", "topics": "...", "hours": 2, "tasks": ["..."]},
            ...
        ],
        "tips": ["...", "..."]
    }
    """
    from datetime import datetime, date as dt_date

    # Calculate days available
    try:
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
        today = dt_date.today()
        days_left = (exam_dt - today).days
        if days_left < 1:
            days_left = 7  # Fallback
    except ValueError:
        days_left = 14

    subjects_str = ", ".join(subjects)

    prompt = f"""Create a detailed, personalized study plan with the following parameters:
- Subjects: {subjects_str}
- Days until exam: {days_left} days
- Exam date: {exam_date}
- Available study time: {daily_hours} hours per day

Create a realistic, day-by-day study schedule that:
1. Distributes subjects evenly but prioritizes harder topics
2. Includes review sessions
3. Gets more intensive closer to the exam
4. Includes breaks and revision days
5. Limits to a maximum of 21 days of scheduling

Return as a JSON object with keys:
- "overview": A brief overview of the study strategy (string)
- "schedule": An array of day objects with keys: "day" (e.g. "Day 1 - Mon Jul 7"), "subject", "topics" (string of topics to cover), "hours" (number), "tasks" (array of specific tasks)
- "tips": An array of study tips (strings)"""

    system = "You are an expert academic coach who creates effective, realistic study plans. Always return valid JSON."

    return _generate_json(prompt, system_instruction=system)


# ── Embedding Generation ──────────────────────────────────

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using Gemini's embedding model.
    Returns a list of embedding vectors.
    """
    try:
        client = get_client()
        embeddings = []

        # Process in batches of 100 (API limit)
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
            )
            for embedding in result.embeddings:
                embeddings.append(embedding.values)

        return embeddings
    except errors.APIError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            st.error("⚠️ **Gemini API Quota Exceeded (429)**: You have exceeded your free tier rate limits or daily requests quota for embeddings. Please wait a minute and try again.")
        else:
            st.error(f"⚠️ **Gemini API Error (Embeddings)**: {e.message if hasattr(e, 'message') else str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Unexpected Embedding Error**: {str(e)}")
        st.stop()
