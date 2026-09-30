from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.database import chat_conversations_collection, chat_messages_collection, users_collection
from app.routers.auth import current_user, require_admin

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class MessageCreate(BaseModel):
    message: str


def clean_message(value: str) -> str:
    value = value.strip()
    if not value:
        raise HTTPException(status_code=400, detail="Skriv ett meddelande.")
    if len(value) > 2000:
        raise HTTPException(status_code=400, detail="Meddelandet får vara högst 2 000 tecken.")
    return value


async def get_or_create_conversation(user: dict) -> dict:
    conversation = await chat_conversations_collection.find_one({"user_email": user["email"]})
    if conversation:
        return conversation
    now = datetime.now(timezone.utc)
    result = await chat_conversations_collection.insert_one({
        "user_email": user["email"],
        "user_name": user.get("name") or user["email"].split("@")[0],
        "created_at": now,
        "updated_at": now,
        "last_message": "",
        "last_sender": "",
        "unread_for_admin": 0,
        "unread_for_user": 0,
    })
    return await chat_conversations_collection.find_one({"_id": result.inserted_id})


def serialize_message(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "message": doc["message"],
        "sender": doc["sender"],
        "senderName": doc.get("sender_name", ""),
        "createdAt": doc["created_at"],
    }


@router.get("/mine")
async def get_my_chat(user: dict = Depends(current_user)):
    conversation = await get_or_create_conversation(user)
    messages = await chat_messages_collection.find({"conversation_id": conversation["_id"]}).sort("created_at", 1).to_list(length=300)
    await chat_conversations_collection.update_one({"_id": conversation["_id"]}, {"$set": {"unread_for_user": 0}})
    return {"conversationId": str(conversation["_id"]), "messages": [serialize_message(message) for message in messages]}


@router.post("/mine/messages", status_code=status.HTTP_201_CREATED)
async def send_my_message(payload: MessageCreate, user: dict = Depends(current_user)):
    conversation = await get_or_create_conversation(user)
    now = datetime.now(timezone.utc)
    message = clean_message(payload.message)
    result = await chat_messages_collection.insert_one({
        "conversation_id": conversation["_id"], "message": message, "sender": "user",
        "sender_name": conversation["user_name"], "created_at": now,
    })
    await chat_conversations_collection.update_one({"_id": conversation["_id"]}, {"$set": {"updated_at": now, "last_message": message, "last_sender": "user"}, "$inc": {"unread_for_admin": 1}})
    created = await chat_messages_collection.find_one({"_id": result.inserted_id})
    return serialize_message(created)


@router.get("/admin/conversations")
async def list_conversations(_: dict = Depends(require_admin)):
    conversations = await chat_conversations_collection.find({}).sort("updated_at", -1).to_list(length=300)
    return [{
        "id": str(item["_id"]), "userEmail": item["user_email"], "userName": item.get("user_name") or item["user_email"].split("@")[0],
        "lastMessage": item.get("last_message", ""), "lastSender": item.get("last_sender", ""),
        "updatedAt": item.get("updated_at"), "unreadForAdmin": item.get("unread_for_admin", 0),
    } for item in conversations]


@router.get("/admin/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, _: dict = Depends(require_admin)):
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=404, detail="Konversationen hittades inte.")
    conversation = await chat_conversations_collection.find_one({"_id": ObjectId(conversation_id)})
    if not conversation:
        raise HTTPException(status_code=404, detail="Konversationen hittades inte.")
    messages = await chat_messages_collection.find({"conversation_id": conversation["_id"]}).sort("created_at", 1).to_list(length=300)
    await chat_conversations_collection.update_one({"_id": conversation["_id"]}, {"$set": {"unread_for_admin": 0}})
    return {"conversation": {"id": str(conversation["_id"]), "userEmail": conversation["user_email"], "userName": conversation.get("user_name") or conversation["user_email"].split("@")[0]}, "messages": [serialize_message(message) for message in messages]}


@router.post("/admin/conversations/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_admin_message(conversation_id: str, payload: MessageCreate, admin: dict = Depends(require_admin)):
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=404, detail="Konversationen hittades inte.")
    conversation = await chat_conversations_collection.find_one({"_id": ObjectId(conversation_id)})
    if not conversation:
        raise HTTPException(status_code=404, detail="Konversationen hittades inte.")
    now = datetime.now(timezone.utc)
    message = clean_message(payload.message)
    result = await chat_messages_collection.insert_one({
        "conversation_id": conversation["_id"], "message": message, "sender": "admin",
        "sender_name": admin.get("name") or admin["email"].split("@")[0], "created_at": now,
    })
    await chat_conversations_collection.update_one({"_id": conversation["_id"]}, {"$set": {"updated_at": now, "last_message": message, "last_sender": "admin"}, "$inc": {"unread_for_user": 1}})
    created = await chat_messages_collection.find_one({"_id": result.inserted_id})
    return serialize_message(created)
