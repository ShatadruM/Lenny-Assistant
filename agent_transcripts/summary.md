# Coding Agent Transcript Summary

This folder contains the complete, sanitized interaction logs (`transcript.jsonl`) between the human developer and the AI coding agent during the development of the Lenny Growth Assistant. All API keys and database credentials have been scrubbed.

## Failed Attempts & How We Corrected Them

### 1. The `passlib` Compatibility Crash
**The Problem:** During the authentication implementation, the agent initially used the `passlib` library to hash passwords. However, `passlib` is largely unmaintained and attempts to read internal `__about__` variables from the modern `bcrypt` package, causing the FastAPI server to crash entirely (`AttributeError`).
**The Fix:** The agent diagnosed the crash by tracing the Uvicorn stack trace, identified the library incompatibility, and refactored `backend/app/api/auth.py` to strip out `passlib` entirely. We dropped down to using the native `bcrypt.hashpw()` and `bcrypt.checkpw()` methods, resolving the crash immediately and improving performance.

### 2. Open-Source LLMs Ignoring RAG Context
**The Problem:** The user noted that when switching to Groq-hosted open-source models (like Llama 3), the agent lost the ability to answer questions about Lenny's podcast. The agent realized that some open-source models heavily discount or entirely ignore long `system` prompts when translated through certain API layers.
**The Fix:** The agent refactored the prompt construction logic in `backend/app/services/agent.py`. Instead of appending the retrieved `pgvector` context to the system prompt, it dynamically intercepted the *final user message* and injected the transcripts directly into it (e.g. `[User Question] + [Here is the knowledge base]`). This forced the LLM's attention mechanism to read the context right before generation, fixing the issue across all providers instantly.

### 3. Docker "Pipe Not Found" Error on Windows
**The Problem:** When running the newly created Docker environment, the user encountered an `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified` error.
**The Fix:** The agent correctly identified this as an environmental issue where the Docker Desktop daemon on Windows had not fully started. The agent guided the user to launch Docker Desktop and wait for the engine to initialize, successfully unblocking the deployment. Additionally, the agent fixed an issue where the Docker container was unable to reach the host's Ollama instance by updating `.env` to use `http://host.docker.internal:11434` and advising the user to bind `OLLAMA_HOST=0.0.0.0`.
