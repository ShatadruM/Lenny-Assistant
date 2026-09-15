from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.schemas.chat import SourceNode
import httpx

async def get_embedding(text_input: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.OLLAMA_URL}/api/embeddings", 
            json={"model": "nomic-embed-text", "prompt": text_input}
        )
        response.raise_for_status()
        return response.json()["embedding"]

async def retrieve_context(query: str, db: AsyncSession, limit: int = 5) -> list[SourceNode]:
    query_vector = await get_embedding(query)
    
    # pgvector cosine distance operator is <=>
    sql = text("""
        SELECT episode_title, youtube_url, content 
        FROM document_chunks 
        ORDER BY embedding <=> :vector 
        LIMIT :limit
    """)
    
    result = await db.execute(sql, {"vector": str(query_vector), "limit": limit})
    rows = result.fetchall()
    
    return [
        SourceNode(
            title=row.episode_title,
            url=row.youtube_url,
            content_snippet=row.content
        ) for row in rows
    ]