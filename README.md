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

---

## Setup Instructions

This application is fully Dockerized for a seamless evaluation and deployment experience. You do not need to install Node, Python, or PostgreSQL locally.

### Prerequisites
- **Docker Desktop** (Make sure the Docker engine is running!)
- **Supabase Cloud Database** (The `DATABASE_URL` is already provided in the `.env` file).

### 1. Environment Configuration
The repository comes pre-configured with environment variables for local Docker deployment. 
If you wish to use cloud models, you can enter your API keys directly in the Frontend UI, or set them in `backend/.env`.

Ensure your `backend/.env` looks like this:
```env
DATABASE_URL=postgresql://postgres.[YOUR_PROJECT]:[YOUR_PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
OLLAMA_URL=http://host.docker.internal:11434
```
use this
DATABASE_URL=postgresql://postgres.wuwmcphowwungxgjojbk:HcB1WE4PC0kEquvQ@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
this is a supabase connection that has the embeddings for testing purpose

### 2. Start the Application
Open your terminal in the root of the project and run:

```bash
docker-compose up --build
```

Docker will:
1. Build the Python FastAPI backend.
2. Build the Vite React frontend.
3. Serve the frontend via an Nginx container.

### 3. Access the App
Once the containers are running, open your browser and navigate to:
**http://localhost:5173**

You can register a new account and immediately start chatting!

### Optional: Local Ollama Setup
If you want to use a local LLM instead of Cloud providers:
1. Install [Ollama](https://ollama.com/).
2. Pull a model: `ollama run llama3`.
3. **Important (Windows/Mac):** You must configure Ollama to accept connections from Docker. Set the environment variable `OLLAMA_HOST=0.0.0.0` on your host machine and restart the Ollama app.
