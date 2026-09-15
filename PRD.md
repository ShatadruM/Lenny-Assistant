# Product Requirements Document (PRD)

## 1. User
The target user is a product manager, founder, or tech enthusiast looking to learn from top-tier Silicon Valley product leaders. They want actionable insights, essay summaries, and direct answers extracted exclusively from "Lenny's Podcast" transcripts, without having to listen to hundreds of hours of audio.

## 2. Problem Statement
There is an overwhelming amount of high-quality growth and product advice buried in long-form podcast transcripts (specifically Lenny's Podcast). Users struggle to search this knowledge base, synthesize it into readable formats (like essays), or extract specific UI/diagrammatic concepts quickly.

## 3. Success Metrics
- **Accuracy:** The agent grounds 100% of its growth advice in the provided vector database transcripts (preventing hallucination).
- **Format Adherence:** Successful rendering of HTML components and Mermaid.js diagrams directly within the UI when requested.
- **Latency:** Retrieval and LLM response generation should take < 5 seconds on average.
- **Security:** 0% execution of malicious scripts via the Artifact Viewer sandbox.

## 4. Assumptions
- Users have an OpenAI, Anthropic, or Groq API key, or a local Ollama instance running.
- The 300MB `init.sql` file containing the vector embeddings is successfully imported into the Supabase database.
- Users want isolated chat histories that don't leak between accounts.

## 5. Scope
### In-Scope
- User authentication (registration/login).
- Conversational chat interface with memory.
- RAG (Retrieval Augmented Generation) over Lenny's Podcast transcripts using pgvector.
- Specialized "Ship 30 for 30" essay generation via LLM Tool Use.
- Dynamic rendering of HTML/Tailwind and Mermaid diagrams via an isolated Artifact Viewer split-pane.
- Multi-LLM provider support (OpenAI, Anthropic, Groq, Ollama).

### Out-of-Scope
- Audio playback of the podcast.
- Live internet searching (strictly closed-domain RAG).
- Multi-user collaborative chats.

## 6. User Flows
1. **Authentication:** User visits the Landing Page -> Registers/Logs in -> Redirected to Chat Interface.
2. **Standard Query:** User asks a question -> Backend retrieves top 5 relevant transcript chunks -> LLM generates grounded markdown response -> Frontend renders.
3. **Artifact Request:** User asks for a UI layout or flowchart -> LLM generates ```html``` or ```mermaid``` blocks -> Frontend intercepts the block -> User clicks "Open in Artifact Viewer" -> Split-pane UI renders the code in a secure sandbox.
4. **Essay Generation:** User asks for an essay -> LLM triggers the `generate_ship30_essay` tool -> Backend scrapes provided principles (if any) and formats the output -> Frontend displays the essay.

## 7. Acceptance Criteria
- [x] Users must log in to view or send messages.
- [x] Chat history persists across browser reloads, separated by `user_id`.
- [x] The agent successfully triggers tool-use for essay generation when prompted.
- [x] HTML artifacts strip `<script>` tags and execute securely inside a zero-origin `<iframe>`.
- [x] The application can be run locally via Docker Compose.

## 8. Risks & Mitigations
- **Risk:** XSS Vulnerabilities from LLM-generated HTML.
  - **Mitigation:** Strict `DOMPurify` allow-listing and a zero-origin `sandbox="allow-scripts"` iframe.
- **Risk:** LLMs ignoring the system prompt or RAG context (especially open-source models).
  - **Mitigation:** Dynamically inject the context into the *last user message* instead of the system prompt to force attention mechanism weighting.
- **Risk:** Passlib compatibility crashing the backend during Auth.
  - **Mitigation:** Dropped `passlib` entirely in favor of direct `bcrypt` hashing.

## 9. Implementation Plan
- **Phase 1: Core Chat & Auth** (Postgres DB, JWT/Session auth, basic LLM connection).
- **Phase 2: RAG Pipeline** (pgvector integration, `nomic-embed-text` setup, context injection).
- **Phase 3: Artifact Viewer** (Split-pane React UI, DOMPurify sanitization, Iframe sandbox).
- **Phase 4: Agent Routing** (Tool use schemas for Anthropic/OpenAI/Groq, essay generation logic).
- **Phase 5: Dockerization & Deployment** (Multi-stage Dockerfiles, dynamic CORS, environment parameterization).
