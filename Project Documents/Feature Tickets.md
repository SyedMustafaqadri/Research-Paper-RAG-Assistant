# Research Paper RAG Assistant

## Engineering Feature Ticket List (MVP + Future Roadmap)

---

# EPIC 1 — Project Foundation

---

## TICKET-001: Project Setup and Folder Structure

### Priority

Must-Have for Launch

### Description

Initialize the project and create a clean production-ready folder structure.

Create directories for:

* graph
* rag
* services
* database
* prompts
* uploaded_pdfs
* chroma_db

Configure environment variable loading.

### Acceptance Criteria

* Project runs successfully.
* Environment variables load correctly.
* Folder structure matches architecture document.
* Application starts without errors.

### Dependencies

None

---

## TICKET-002: Configuration Management

### Priority

Must-Have for Launch

### Description

Implement centralized configuration management.

Load settings from .env file.

Provide typed access to:

* Gemini API Key
* ChromaDB path
* Upload directory
* Debug mode

### Acceptance Criteria

* Configuration values accessible globally.
* Missing required variables raise clear errors.
* Environment switching supported.

### Dependencies

TICKET-001

---

# EPIC 2 — PDF Processing

---

## TICKET-003: PDF Upload System

### Priority

Must-Have for Launch

### Description

Build file upload functionality using Chainlit.

Users should upload one or more PDF files.

Validate:

* PDF format
* Maximum file size
* File integrity

Store uploaded files locally.

### Acceptance Criteria

* PDF uploads succeed.
* Invalid files rejected.
* Uploaded files saved to upload directory.
* Success and failure messages displayed.

### Dependencies

TICKET-001

---

## TICKET-004: PDF Text Extraction

### Priority

Must-Have for Launch

### Description

Extract text from uploaded research papers.

Capture:

* Page number
* Text content
* Document metadata

Use LangChain PDF loaders.

### Acceptance Criteria

* Text extracted from all pages.
* Page metadata preserved.
* Extraction errors handled gracefully.

### Dependencies

TICKET-003

---

## TICKET-005: Document Chunking Pipeline

### Priority

Must-Have for Launch

### Description

Split extracted content into chunks suitable for retrieval.

Requirements:

* Configurable chunk size
* Configurable overlap
* Preserve metadata

### Acceptance Criteria

* Chunks generated successfully.
* Chunk overlap implemented.
* Metadata preserved.

### Dependencies

TICKET-004

---

# EPIC 3 — Vector Database

---

## TICKET-006: Embedding Generation

### Priority

Must-Have for Launch

### Description

Generate embeddings for all document chunks using Gemini embeddings.

Store embedding metadata.

### Acceptance Criteria

* Embeddings created successfully.
* Failed embeddings logged.
* Embedding pipeline reusable.

### Dependencies

TICKET-005

---

## TICKET-007: ChromaDB Integration

### Priority

Must-Have for Launch

### Description

Store embeddings and metadata inside ChromaDB.

Metadata should include:

* Document ID
* Page Number
* Chunk Index
* Filename

### Acceptance Criteria

* Chunks stored in ChromaDB.
* Metadata searchable.
* Collection persists after restart.

### Dependencies

TICKET-006

---

## TICKET-008: Retrieval Engine

### Priority

Must-Have for Launch

### Description

Implement semantic retrieval.

Given a user query:

* Search ChromaDB
* Return top-k chunks
* Include metadata

### Acceptance Criteria

* Top relevant chunks returned.
* Retrieval configurable.
* Metadata included.

### Dependencies

TICKET-007

---

# EPIC 4 — LangGraph Workflow

---

## TICKET-009: LangGraph State Definition

### Priority

Must-Have for Launch

### Description

Create application state model.

State should contain:

* User question
* Retrieved documents
* Generated answer

### Acceptance Criteria

* State passes correctly between nodes.
* Workflow compiles successfully.

### Dependencies

TICKET-008

---

## TICKET-010: Retrieval Node

### Priority

Must-Have for Launch

### Description

Create LangGraph retrieval node.

Node responsibilities:

* Receive question
* Retrieve documents
* Update graph state

### Acceptance Criteria

* Documents retrieved correctly.
* State updated successfully.

### Dependencies

TICKET-009

---

## TICKET-011: Answer Generation Node

### Priority

Must-Have for Launch

### Description

Create generation node using Gemini.

Requirements:

* Use retrieved context
* Answer only from provided documents
* Avoid unsupported claims

### Acceptance Criteria

* Answer generated successfully.
* Context included in prompt.
* Response returned through graph.

### Dependencies

TICKET-010

---

## TICKET-012: LangGraph Workflow Assembly

### Priority

Must-Have for Launch

### Description

Connect nodes into workflow.

Flow:

Question
→ Retrieve
→ Generate
→ Return Answer

### Acceptance Criteria

* Workflow executes end-to-end.
* Graph compiles successfully.

### Dependencies

TICKET-011

---

# EPIC 5 — Conversational Interface

---

## TICKET-013: Chainlit Chat Interface

### Priority

Must-Have for Launch

### Description

Build chat interface.

Requirements:

* Welcome message
* Chat input
* Response display

### Acceptance Criteria

* Users can send messages.
* Assistant replies displayed.
* UI loads successfully.

### Dependencies

TICKET-012

---

## TICKET-014: Connect Chat to LangGraph

### Priority

Must-Have for Launch

### Description

Connect Chainlit frontend to LangGraph workflow.

User message should trigger graph execution.

### Acceptance Criteria

* Questions processed through graph.
* Answers displayed in UI.

### Dependencies

TICKET-013

---

# EPIC 6 — Source Grounding

---

## TICKET-015: Source Citation Support

### Priority

Must-Have for Launch

### Description

Display document sources used to generate answers.

Show:

* File Name
* Page Number

### Acceptance Criteria

* Sources displayed with answer.
* Sources correspond to retrieved chunks.

### Dependencies

TICKET-014

---

## TICKET-016: Hallucination Reduction Prompt

### Priority

Must-Have for Launch

### Description

Implement prompt rules.

Model should:

* Use retrieved context only.
* State uncertainty if answer not found.

### Acceptance Criteria

* Unsupported answers reduced.
* Missing information acknowledged.

### Dependencies

TICKET-011

---

# EPIC 7 — Research Assistant Features

---

## TICKET-017: Research Paper Summary Generator

### Priority

Must-Have for Launch

### Description

Create paper summary feature.

Generate:

* Overview
* Methodology
* Results
* Limitations

### Acceptance Criteria

* Summary generated successfully.
* Sections clearly formatted.

### Dependencies

TICKET-014

---

## TICKET-018: Follow-Up Question Support

### Priority

Must-Have for Launch

### Description

Maintain conversation context.

Allow users to ask follow-up questions naturally.

### Acceptance Criteria

* Context retained within session.
* Follow-up questions answered correctly.

### Dependencies

TICKET-014

---

# EPIC 8 — Monitoring and Reliability

---

## TICKET-019: Retrieval Logging

### Priority

Should-Have

### Description

Log:

* User question
* Retrieved chunks
* Response time

### Acceptance Criteria

* Logs stored successfully.
* Logs available for debugging.

### Dependencies

TICKET-014

---

## TICKET-020: Error Handling Framework

### Priority

Should-Have

### Description

Create centralized error handling.

Handle:

* Upload failures
* PDF parsing failures
* Gemini API failures
* ChromaDB failures

### Acceptance Criteria

* Errors do not crash application.
* User-friendly messages displayed.

### Dependencies

TICKET-001

---

# EPIC 9 — Future Enhancements

---

## TICKET-021: Multi-Paper Comparison

### Priority

Nice-to-Have

### Description

Allow users to compare multiple uploaded papers.

Questions such as:

"Compare methodologies of Paper A and Paper B"

### Acceptance Criteria

* Multiple papers searchable.
* Comparison response generated.

### Dependencies

All MVP tickets

---

## TICKET-022: User Authentication

### Priority

Nice-to-Have

### Description

Add user accounts.

Support:

* Registration
* Login
* Session management

### Acceptance Criteria

* Users can create accounts.
* Documents isolated per user.

### Dependencies

Database implementation

---

## TICKET-023: Export Results

### Priority

Nice-to-Have

### Description

Allow exporting:

* Answers
* Summaries
* Citations

Formats:

* PDF
* DOCX

### Acceptance Criteria

* Export files generated successfully.

### Dependencies

TICKET-017

---

## TICKET-024: Research Workspace Dashboard

### Priority

Nice-to-Have

### Description

Create dashboard for:

* Uploaded papers
* Chat history
* Summaries

### Acceptance Criteria

* Users can browse previous work.

### Dependencies

Authentication
