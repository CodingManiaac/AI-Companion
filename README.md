# AI Study Companion – Intelligent Learning Assistant

AI Study Companion is a comprehensive learning management web application built using **Python**, **Streamlit**, **SQLite**, **FAISS**, and the **Google Gemini API** (utilizing the modern `google-genai` SDK).

The app allows students to upload PDF materials, auto-generate key takeaways, ask questions dynamically from uploaded notes, take self-testing MCQ quizzes, study flashcards with flip card animations, plan schedules, and visualize learning progress.

---

## 🌟 Core Features
1. **User Authentication**: Secure signup and login with password hashing via `bcrypt`.
2. **Document Manager**: PDF text extractor parsing via `pdfplumber` and file metadata tracking.
3. **AI Summary Generator**: Three output modes (Concise, Key Takeaways, Chapter Breakdown) with HTML download.
4. **Chat with PDF (RAG)**: Context-aware AI questions using local similarity indices created with FAISS.
5. **MCQ Quiz Engine**: Interactive tests with score reporting, detailed solutions, and HTML exports.
6. **Revision Flashcards**: Flip-to-reveal study cards styled via CSS transitions.
7. **AI Study Planner**: Custom schedule generator calculated by deadline constraints and daily hours.
8. **Dashboard Analytics**: Plotly visualizations analyzing streak records, scores, and upload histories.

---

## 🛠️ Setup & Installation

### Prerequisites
*   Python 3.10 or higher installed.
*   A Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### Installation
1. Clone or download this project to your directory:
   ```bash
   cd "c:\AI Companion"
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create and configure your environment file:
   *   Copy `.env.example` to `.env`
   *   Replace `your_api_key_here` with your actual Google Gemini API key:
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```

5. Run the Streamlit application:
   ```bash
   streamlit run streamlit_app.py
   ```

6. Open the app in your browser at `http://localhost:8501`.
