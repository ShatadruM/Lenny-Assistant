from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Session, Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import process_chat_message
from app.core.logger import logger
import httpx

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Ensure session exists or create a new one
        session_id = request.session_id
        if not session_id:
            new_session = Session(user_id=request.user_id)
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            session_id = new_session.id
            logger.info(f"Created new session: {session_id}")

        # 2. Save user message to database
        user_msg = Message(session_id=session_id, role="user", content=request.message)
        db.add(user_msg)
        await db.commit()

        # 3. Detect if the user wants a Ship 30 essay
        generate_essay = "Ship 30" in request.message or "essay" in request.message.lower()

        # 4. Fetch previous conversation history for context
        from sqlalchemy import select
        stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc())
        result = await db.execute(stmt)
        past_messages = result.scalars().all()
        chat_history = [{"role": m.role, "content": m.content} for m in past_messages]

        # 5. Route to the agent 
        try:
            reply_content, source_nodes = await process_chat_message(
                message=request.message,
                provider=request.llm_provider,
                db=db,
                generate_essay_flag=generate_essay,
                api_key=request.api_key,
                chat_history=chat_history
            )
        except httpx.ConnectError:
            reply_content = "Please use a Cloud Provider with your own api key to chat, or ensure your local Ollama instance is running."
            source_nodes = []

        # 6. Save assistant message to database
        assistant_msg = Message(session_id=session_id, role="assistant", content=reply_content)
        db.add(assistant_msg)
        await db.commit()

        return ChatResponse(
            session_id=session_id,
            reply=reply_content,
            source_nodes=source_nodes
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during chat processing.")

@router.get("/sessions")
async def get_sessions(user_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    try:
        # Fetch sessions ordered by creation date descending, filtered by user
        stmt = select(Session).where(Session.user_id == user_id).order_by(Session.created_at.desc())
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        return [{"id": s.id, "created_at": s.created_at, "user_metadata": s.user_metadata} for s in sessions]
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions.")

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    try:
        stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc())
        result = await db.execute(stmt)
        messages = result.scalars().all()
        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "timestamp": m.created_at,
                "sourceNodes": [] # Optionally can fetch or store source nodes, but keep simple for now
            }
            for m in messages
        ]
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages.")