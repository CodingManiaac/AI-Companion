# AI Study Companion – Software Requirement Specification (SRS)

## 1. Introduction
The AI Study Companion (Intelligent Learning Assistant) is a web-based educational platform designed to enhance learning productivity. By integrating advanced generative AI, retrieval-augmented generation (RAG), and vector storage, the application automates key study aids such as content summarizing, question-answering, flashcard generation, quiz building, and study planning.

## 2. Functional Requirements

### 2.1 User Authentication & Management
*   **Registration**: Users can sign up with name, unique email, and password.
*   **Login**: Secures session access by verifying hashed passwords via bcrypt.
*   **Session Persistence**: Keeps users logged in across page reloads using Streamlit session state.
*   **Logout**: Destroys session variables and redirects users to the login screen.

### 2.2 Upload PDF Module
*   **File Selection**: Allows uploading multiple PDF documents.
*   **Text Extraction**: Extracts raw text using `pdfplumber`.
*   **Metadata Storage**: Saves document details (name, path, upload date) to the database.

### 2.3 AI Summary Generator
*   **Concise Summary**: Condenses document contents using Google Gemini.
*   **Key Points**: Outputs bullet-point takeaways.
*   **Chapter Breakdown**: Identifies section/chapter markers and outlines key concepts for each.
*   **Download**: Enables exporting generated summary output as styled HTML.

### 2.4 AI Question Answering (RAG)
*   **Embeddings**: Converts PDF document text chunks into 768-dimension vectors via `text-embedding-004`.
*   **Vector Database**: Builds and query-searches a local FAISS index.
*   **Chat Workspace**: Handles conversational questioning with context-aware responses and inline document citation references.

### 2.5 Quiz Generator
*   **Custom Parameters**: Slider for selecting quiz length (3-20 questions).
*   **MCQ Format**: Generates 4 options per question with explanation tooltips.
*   **Interactive Submission**: Immediate grading, showing correct/incorrect choices.
*   **History**: Logs results to SQLite database for dashboard tracking.

### 2.6 Flashcard Generator
*   **Interactive Revision**: Styled flipping card layout using CSS 3D transforms.
*   **Browse and Save**: Allows saving selected cards to a global flashcard library.

### 2.7 Study Planner
*   **Inputs**: Course subjects, target exam date, and available study hours.
*   **Plan Generation**: Generates a structured daily study plan showing hours and specific tasks.

### 2.8 Progress Dashboard
*   **Overview**: Metric cards for uploads, quiz completion counts, averages, and day streaks.
*   **Visualizations**: Dynamic Plotly graphs plotting study habits, distributions, and uploads over time.

---

## 3. Non-Functional Requirements
*   **Security**: Cleartext passwords are encrypted using bcrypt hashing. API keys are kept safe in `.env` configurations.
*   **Usability**: Fluid dark mode default palette with responsive styling designed for both desktop and mobile viewports.
*   **Performance**: RAG queries complete under 2 seconds; FAISS indices load instantly from local memory.
