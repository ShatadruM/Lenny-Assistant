import os
import yaml
import asyncio
import asyncpg
import httpx
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "nomic-embed-text"

async def get_embedding(text: str):
    # Changed to 120 seconds. Enough for a cold start, but won't hang forever.
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OLLAMA_URL, 
            json={"model": MODEL_NAME, "prompt": text}
        )
        response.raise_for_status() # Raise an error if Ollama fails
        return response.json()["embedding"]

async def ingest_transcripts():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in environment.")
        return

    repo_path = Path("./lennys-podcast-transcripts")
    md_files = list(repo_path.rglob("*.md"))
    
    conn = await asyncpg.connect(db_url)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    try:
        for idx, md_file in enumerate(md_files, 1):
            content = md_file.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue

            parts = content.split("---", 2)
            if len(parts) < 3: continue

            meta = yaml.safe_load(parts[1]) or {}
            title = meta.get("title", md_file.stem)
            url = meta.get("youtube_url", "")
            body = parts[2]

            exists = await conn.fetchval(
                "SELECT 1 FROM document_chunks WHERE episode_title = $1 LIMIT 1", 
                title
            )
            if exists:
                print(f"[{idx}/{len(md_files)}] Skipping: {title}")
                continue

            print(f"[{idx}/{len(md_files)}] Processing: {title}")
            chunks = splitter.split_text(body)

            for c_idx, chunk in enumerate(chunks, 1):
                # Print progress for every 10th chunk so you know it's not frozen
                if c_idx % 10 == 0 or c_idx == len(chunks):
                    print(f"  ...embedding chunk {c_idx}/{len(chunks)}")
                
                vector = await get_embedding(chunk)
                await conn.execute(
                    "INSERT INTO document_chunks (episode_title, youtube_url, content, embedding) VALUES ($1, $2, $3, $4)",
                    title, url, chunk, str(vector)
                )
            print(f"-> Successfully stored {len(chunks)} chunks for: {title}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(ingest_transcripts())