# Technical Architecture

## 1. System Overview
The Lenny Growth Assistant is a full-stack, containerized web application designed for RAG (Retrieval-Augmented Generation) and dynamic artifact rendering.

## 2. Deployment Topology
- **Frontend Container:** A Vite + React Single Page Application (SPA), built via Node and served using an `nginx:alpine` reverse proxy.
- **Backend Container:** A Python 3.12 FastAPI application served by Uvicorn.
- **Database:** Supabase Cloud (PostgreSQL + pgvector).

All local environments are orchestrated via `docker-compose.yml`, which handles network routing and dynamic environment variable injection (e.g., `FRONTEND_URL` and `VITE_API_URL`) to prevent CORS issues across environments (Vercel/Railway).

## 3. Database Schema (PostgreSQL)
The application utilizes SQLAlchemy ORM with the following relational schema:
- **`users`**: `id` (UUID), `username`, `password_hash` (bcrypt), `created_at`.
- **`sessions`**: `id` (UUID), `user_id` (FK), `created_at`, `user_metadata` (JSON).
- **`messages`**: `id` (UUID), `session_id` (FK), `role` (user/assistant), `content`, `created_at`.
- **`document_chunks`**: `id` (INT), `episode_title` (TEXT), `youtube_url` (TEXT), `content` (TEXT), `embedding` (VECTOR(768)).

## 4. API Endpoints
All endpoints are prefixed with `/api`.
- `POST /auth/register`: Hashes password using bcrypt and creates a `User`.
- `POST /auth/login`: Verifies bcrypt hash, returns `user_id`.
- `POST /chat`: Main agent router. Accepts `message`, `session_id`, `llm_provider`, `api_key`.
- `GET /sessions`: Returns a list of chat sessions filtered by `user_id`.
- `GET /sessions/{id}/messages`: Returns the chronological message history for a specific session.

## 5. Ingestion & Retrieval Flow (RAG)
1. **Ingestion:** Transcripts are pre-chunked and embedded using `nomic-embed-text` (768 dimensions), then stored in `document_chunks` via the 300MB `init.sql` script executed directly on the Supabase Cloud.
2. **Retrieval:** When a user sends a message, `app/services/retrieval.py` converts the query into a vector using the Ollama Embedding API.
3. **Distance Calculation:** A SQL query uses pgvector's cosine distance operator (`<=>`) to fetch the top 5 closest chunks.
4. **Context Injection:** To ensure high compliance from open-source LLMs, the RAG chunks are dynamically appended directly to the *final user message* rather than the system prompt.

## 6. Agent Routing & Model Toggles
The user can seamlessly switch between LLM providers (Anthropic, OpenAI, Groq, local Ollama) via a UI dropdown.
- **Heuristic Routing:** The `/chat` endpoint scans the incoming message for intents (e.g., "Ship 30"). If detected, it attaches an OpenAI/Anthropic-compatible JSON Tool Schema (`generate_ship30_essay`) to the LLM request.
- **Tool Execution:** If the LLM triggers the tool, the backend intercepts the `tool_use` stop reason, scrapes the requested target URL for writing principles, and makes a *secondary* LLM call to synthesize the essay.

## 7. Security Boundaries
- **Authentication:** `passlib` was removed due to compatibility issues with modern `bcrypt`. Hashing is handled explicitly via the native `bcrypt.hashpw` implementation.
- **Artifact Sandboxing:** 
  - **DOMPurify:** Incoming HTML artifacts are stripped of `<script>`, `<object>`, `<iframe>`, and dangerous execution attributes (`onclick`, `onload`).
  - **Iframe Isolation:** The sanitized HTML is injected via `srcDoc` into an `<iframe>` configured with `sandbox="allow-scripts"`. Critically, `allow-same-origin` is omitted, trapping any hallucinated malicious code in a zero-origin environment unable to access the parent React DOM or LocalStorage session tokens.
