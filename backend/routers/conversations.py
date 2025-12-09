from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.conversation_service import ConversationService

router = APIRouter()
service = ConversationService()

@router.get("/")
async def list_conversations():
    return {"conversations": service.list_conversations()}

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    exists = service.conversation_exists(conversation_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = service.get_messages(conversation_id)
    return {"id": conversation_id, "messages_count": len(msgs)}

@router.get("/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    exists = service.conversation_exists(conversation_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"messages": service.get_messages(conversation_id)}

@router.post("/")
async def create_conversation():
    cid = service.create_conversation()
    return {"id": cid}

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    exists = service.conversation_exists(conversation_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    service.delete_conversation(conversation_id)
    return {"status": "deleted", "id": conversation_id}

@router.delete("/")
async def delete_all_conversations():
    service.delete_all()
    return {"status": "deleted_all"}

class RenameBody(BaseModel):
    title: str

@router.post("/{conversation_id}/rename")
async def rename_conversation(conversation_id: str, body: RenameBody):
    exists = service.conversation_exists(conversation_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    service.set_title(conversation_id, body.title)
    return {"id": conversation_id, "title": body.title}
