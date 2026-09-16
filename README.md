# Lenny Growth Assistant

Youtube Video Demo --> [[Oogway Labs Assignment - Lenny's Growth Assistant]](https://youtu.be/rfywW39RPLE)


## The Problem
There is an overwhelming amount of high-quality growth, product, and startup advice buried in hundreds of hours of long-form podcast transcripts (specifically *Lenny's Podcast*). For a product manager, founder, or tech enthusiast, finding actionable insights requires sifting through massive amounts of text. 

Users struggle to query this knowledge base accurately, synthesize it into readable formats (like essays), or extract specific UI/diagrammatic concepts quickly. General LLMs often hallucinate answers because they lack the specific, grounded context of the podcast.

## The Solution
**The Lenny Growth Assistant** is a full-stack, RAG-powered (Retrieval-Augmented Generation) application designed to extract and synthesize insights directly from Lenny's Podcast transcripts. 

- **No Hallucinations:** Answers are 100% grounded in a `pgvector` database containing chunks of podcast transcripts.
- **Artifact Viewer:** Dynamically generates and renders Mermaid.js flowcharts and Tailwind HTML UI components in an isolated, sandboxed split-pane UI.
- **LLM Tool Use:** Automatically routes specific queries to generate highly-formatted "Ship 30 for 30" essays.
- **Provider Agnostic:** Supports switching between local models (Ollama) and cloud models (OpenAI, Anthropic, Groq).


## Setup Instructions

This application is fully Dockerized for a seamless evaluation and deployment experience. You do not need to install Node, Python, or PostgreSQL locally.

### Prerequisites
- **Ollama**: You **must** have Ollama running locally, as the application relies on it exclusively to generate RAG vector embeddings (`nomic-embed-text`), *even if you are using Cloud Providers (like OpenAI/Groq) for chat generation, and even if you are accessing a deployed version of the app!*
- **Docker Desktop** (If running locally via Docker)
- **Supabase Cloud Database** (The `DATABASE_URL` is already provided in the `.env` file).

### 1. Ollama Setup (Mandatory)
Before starting the app, ensure Ollama is installed and the embedding model is pulled:
```bash
ollama run nomic-embed-text
```
*(Note for Docker/Deployed users: You must configure Ollama to accept external connections. Set your environment variable `OLLAMA_HOST=0.0.0.0` on your host machine and restart the Ollama app).*

### 2. Environment Configuration
The repository comes pre-configured with environment variables for local Docker deployment. 

Ensure your `backend/.env` looks like this:
```env
# This is a mock Supabase connection that has the embeddings for testing purposes
DATABASE_URL=postgresql://postgres.wuwmcphowwungxgjojbk:HcB1WE4PC0kEquvQ@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres

OLLAMA_URL=http://host.docker.internal:11434
```

### 3. Cloud Provider Setup
If you wish to use a cloud model for significantly faster and higher quality chat generation instead of local LLMs, you have two options:

**Option A (Use your own API Key):**
1. Generate an API Key (e.g. from the [GroqCloud Console](https://console.groq.com/keys)).
2. In the Chat UI settings modal, select your provider and paste your key.

**Option B (Use Pre-provided Groq LLM):**
Regardless of which provider is currently selected in the UI, you can click the green **"Use Pre-provided Groq LLM"** button in the API settings modal. This bypasses the key requirement and automatically routes your chat using the `GROQ_API_KEY` configured in the backend `.env` file!

### 4. Start the Application
Open your terminal in the root of the project and run:

```bash
docker-compose up --build
```

Docker will:
1. Build the Python FastAPI backend.
2. Build the Vite React frontend.
3. Serve the frontend via an Nginx container.

### 5. Access the App
Once the containers are running, open your browser and navigate to:
**http://localhost:5173**

You can register a new account and immediately start chatting!

### Optional: Local LLM for Chat Generation
If you want to use a local LLM instead of Cloud providers for the final text generation:
1. Pull a chat model: `ollama run llama3`.
2. Select "Local (Ollama)" from the provider dropdown in the UI.

---

## Architecture Overview
- **Frontend**: React + Vite SPA with dynamic component rendering via sandboxed iframes and Mermaid.js diagram generation.
- **Backend**: Python FastAPI with `httpx` for async API calls to LLM providers.
- **Database**: Supabase Cloud (PostgreSQL + pgvector).
- **RAG Pipeline**: Transcript chunks are embedded using Ollama's `nomic-embed-text` and retrieved via cosine distance similarity search in SQL.
- **Agent Routing**: The `/chat` endpoint scans messages for intents (like "Ship 30") and seamlessly injects JSON Tool Schemas to trigger autonomous scraping and essay generation.

---

## Automated Testing
The application includes an automated test suite for the backend API and RAG pipeline.

To run the tests locally:
1. Open a terminal and navigate to the `backend` directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio httpx
   ```
3. Execute the test suite:
   ```bash
   pytest tests/ -v
   ```

---

## Troubleshooting

> [!CAUTION]
> **Deployed Links & Cloud Vercel Instances**
> If you are attempting to test a live, deployed version of this backend (e.g. on Vercel) instead of running it locally via Docker, **you will likely encounter connection errors.**
> 
> The application's core RAG pipeline fundamentally requires access to the local Ollama `nomic-embed-text` model to embed your questions. A cloud server on Vercel cannot reach the `localhost:11434` instance running on your personal laptop. Unless you expose your local Ollama instance to the public internet (using tools like Ngrok) and update the `OLLAMA_URL` environment variable on Vercel, the deployed app will not function for RAG queries.
>
> **For the smoothest evaluation, please run the application locally using the provided `docker-compose up` instructions.**
