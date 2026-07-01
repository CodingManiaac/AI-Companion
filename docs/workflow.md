# Workflow Diagram

This document illustrates the primary workflow pathways available within the AI Study Companion.

## 1. User Authentication & Upload Workflow
```mermaid
sequenceDiagram
    actor Student
    participant Auth as auth.py
    participant App as app.py
    participant DB as db.py
    participant FAISS as vector_store.py

    Student->>App: Open Page
    App->>Auth: Check session state
    alt Not Logged In
        Auth-->>Student: Display Login/Register forms
        Student->>App: Enter Credentials & Submit
        App->>DB: Verify / Insert User Record
        DB-->>App: OK
        App->>Auth: Set authenticated=True
    end
    App-->>Student: Show Home Dashboard

    Student->>App: Upload PDF Document
    App->>DB: Save Document Metadata & Text
    App->>FAISS: Create Vector Index (Gemini Embeddings)
    FAISS-->>App: Done
    App-->>Student: Display Upload Success Notification
```

## 2. RAG Q&A & Quiz Generation Workflows
```mermaid
sequenceDiagram
    actor Student
    participant App as Ask_Questions.py
    participant FAISS as vector_store.py
    participant Gemini as Gemini API (ai_engine.py)
    participant DB as db.py

    Note over Student, Gemini: 1. Question Answering Workflow (RAG)
    Student->>App: Input text question
    App->>FAISS: Search similarity index for query
    FAISS-->>App: Return top relevant text chunks (Context)
    App->>Gemini: Request answer (Context + Question + History)
    Gemini-->>App: Return AI Answer
    App->>DB: Save Chat Message exchange
    App-->>Student: Display Answer with expandable source chunks

    Note over Student, Gemini: 2. Quiz Generator Workflow
    Student->>App: Click 'Generate Quiz'
    App->>Gemini: Prompt MCQ quiz from PDF text
    Gemini-->>App: Return MCQ JSON structured response
    Student->>App: Submit completed quiz answers
    App->>DB: Log Quiz Score & Answers JSON
    App-->>Student: Display Score Card & detailed reviews
```
