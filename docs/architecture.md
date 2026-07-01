# System Architecture

The AI Study Companion architecture is structured into four main layers: Frontend Presentation (Streamlit), Application Logic, Vector Storage/AI Integration, and the Database Storage layer.

```mermaid
graph TD
    User([User Browser]) <--> |HTTP / WebSockets| StreamlitApp[Streamlit App Layer]
    
    subgraph StreamlitApp [Streamlit App & Pages]
        AppEntry[app.py]
        Pages[Page Modules]
        Theme[style.css]
    end

    StreamlitApp <--> |Auth Check & Session| Auth[auth.py]
    StreamlitApp <--> |CRUD Queries| DB[db.py]
    StreamlitApp <--> |Text Chunking| PDFProc[pdf_processor.py]
    StreamlitApp <--> |Similarity Search| VectorStore[vector_store.py]
    StreamlitApp <--> |AI Queries| AIEngine[ai_engine.py]

    subgraph ExternalServices [AI & Vectorization]
        GeminiGen[Gemini 2.0 Flash]
        GeminiEmbed[text-embedding-004]
    end

    AIEngine <--> |API Key / REST| GeminiGen
    VectorStore <--> |Generate Embeddings| GeminiEmbed

    subgraph DataStorage [Storage Layer]
        SQLite[(sqlite3 - study_companion.db)]
        UploadsFolder[[uploads/ PDF files]]
        VectorstoreFolder[[vectorstore/ FAISS Index]]
    end

    DB <--> SQLite
    PDFProc --> |Read File| UploadsFolder
    VectorStore <--> |Save/Load Index| VectorstoreFolder
```

## Description of Components
1. **Frontend Presentation**: Standard Streamlit multipage setup utilizing navigation routines, custom stylesheets (`style.css`), and Plotly visualization libraries.
2. **Application Logic**: Modular Python utility modules implementing core flows (auth logic, PDF preprocessing, RAG searches, and Gemini prompt constructions).
3. **AI & Vector Integration**: Utilizes Google Gen AI SDK for generating text completions and embedding structures. Searches are stored and computed locally using FAISS.
4. **Data Storage**: SQLite handles local relational tables (users, quiz results, study plans, metadata). Original PDFs are held securely in the system folder structures.
