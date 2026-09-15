from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    message: str
    llm_provider: str = "local"
    api_key: Optional[str] = None

class SourceNode(BaseModel):
    title: str
    url: str
    content_snippet: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    source_nodes: List[SourceNode] = []