# 1. High-Level Architecture

```text
┌─────────────────────────┐
│      Chainlit UI        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     LangGraph Agent     │
└────────────┬────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
Retrieval      LLM Generation
      │             │
      ▼             ▼
 ChromaDB      Gemini API
      │
      ▼
 Research Paper Chunks
```

Flow:

1. User uploads PDF
2. PDF processed
3. Text split into chunks
4. Chunks embedded
5. Stored in ChromaDB
6. User asks question
7. Retriever finds relevant chunks
8. LangGraph orchestrates workflow
9. Gemini generates answer
10. Answer returned with sources

---

# 2. Recommended Tech Stack

## Frontend

### Chainlit

Why:

* Built specifically for LLM applications
* File uploads
* Streaming responses
* Chat UI ready immediately
* Minimal frontend work

Alternative:

* Next.js + React

Use when:

* Building commercial SaaS

For portfolio:

**Chainlit is perfect.**

---

## Agent Layer

### LangGraph

Why:

* Industry standard for AI workflows
* Supports branching workflows
* Easy upgrade path

Current workflow:

```text
Question
  ↓
Retrieve
  ↓
Generate
```

Future:

```text
Question
   ↓
Query Rewrite
   ↓
Retrieve
   ↓
Grade Docs
   ↓
Generate
```

---

## LLM Framework

### LangChain

Why:

* Large ecosystem
* Retriever abstraction
* Document loaders
* Vector store integrations

---

## Vector Database

### ChromaDB

Why:

* Easy setup
* Open source
* Local storage
* Perfect for portfolio projects

Future production alternatives:

* Pinecone
* Weaviate
* Qdrant

---

## LLM

### Gemini 3 Flash

Why:

* Very cheap
* Fast
* Good context length
* Strong document understanding

---

## Embeddings

### Gemini Embeddings

Why:

* Same ecosystem
* Easy integration
* Good retrieval quality

---

## Database

### PostgreSQL

Even if Chroma stores vectors, you still need relational data.

Store:

* Users
* Chats
* Documents
* Metadata

---

# 3. Production Folder Structure

```text
research-rag/

├── app/
│
├── api/
│   ├── chat.py
│   ├── upload.py
│   └── health.py
│
├── core/
│   ├── config.py
│   ├── logger.py
│   └── security.py
│
├── graph/
│   ├── workflow.py
│   ├── nodes.py
│   └── state.py
│
├── rag/
│   ├── ingest.py
│   ├── retriever.py
│   ├── embeddings.py
│   └── vectorstore.py
│
├── database/
│   ├── models.py
│   ├── connection.py
│   └── migrations/
│
├── services/
│   ├── document_service.py
│   ├── chat_service.py
│   └── user_service.py
│
├── prompts/
│   ├── system_prompt.py
│   └── retrieval_prompt.py
│
├── uploaded_pdfs/
│
├── chroma_db/
│
├── tests/
│
├── chainlit_app.py
│
├── requirements.txt
│
├── .env
│
└── README.md
```

---

# 4. Database Schema

Even if your MVP doesn't need authentication, designing for SaaS is valuable.

---

## users

Stores user accounts.

| Field         | Type      |
| ------------- | --------- |
| id            | UUID      |
| email         | VARCHAR   |
| name          | VARCHAR   |
| password_hash | TEXT      |
| created_at    | TIMESTAMP |

Example:

```text
User
 ├─ uploads papers
 └─ creates chats
```

---

## documents

Stores uploaded PDFs.

| Field       | Type      |
| ----------- | --------- |
| id          | UUID      |
| user_id     | UUID      |
| filename    | VARCHAR   |
| file_path   | TEXT      |
| total_pages | INTEGER   |
| upload_date | TIMESTAMP |

Relationship:

```text
User
  ↓
Documents
```

One user → many documents.

---

## document_chunks

Metadata for vectorized chunks.

| Field       | Type    |
| ----------- | ------- |
| id          | UUID    |
| document_id | UUID    |
| chunk_index | INTEGER |
| page_number | INTEGER |
| chunk_text  | TEXT    |
| chroma_id   | VARCHAR |

Relationship:

```text
Document
    ↓
Many Chunks
```

---

## chats

Stores conversations.

| Field      | Type      |
| ---------- | --------- |
| id         | UUID      |
| user_id    | UUID      |
| title      | VARCHAR   |
| created_at | TIMESTAMP |

Example:

```text
Chat:
Research Questions
```

---

## messages

Stores individual messages.

| Field      | Type      |
| ---------- | --------- |
| id         | UUID      |
| chat_id    | UUID      |
| role       | VARCHAR   |
| content    | TEXT      |
| created_at | TIMESTAMP |

role:

```text
user
assistant
system
```

---

## retrieval_logs

Useful for debugging.

| Field            | Type      |
| ---------------- | --------- |
| id               | UUID      |
| question         | TEXT      |
| retrieved_chunks | JSON      |
| response_time    | FLOAT     |
| timestamp        | TIMESTAMP |

This table becomes extremely useful during interviews.

---

# 5. Database Relationships

```text
users
 │
 ├─────────► documents
 │               │
 │               ▼
 │         document_chunks
 │
 ▼
chats
 │
 ▼
messages
```

---

# 6. ChromaDB Collection Design

Instead of one huge collection:

```text
research_papers
```

Store metadata:

```python
{
    "document_id": "...",
    "paper_title": "...",
    "page": 5,
    "chunk": 14
}
```

This allows:

```text
Show source page

Filter by document

Multi-document retrieval
```

---

# 7. Environment Variables

`.env`

```env
# Gemini

GOOGLE_API_KEY=

# PostgreSQL

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

# Chroma

CHROMA_DB_PATH=./chroma_db

# Uploads

UPLOAD_FOLDER=./uploaded_pdfs

# Application

ENV=development
DEBUG=True


