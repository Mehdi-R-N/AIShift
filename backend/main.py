from fastapi import FastAPI, UploadFile, File, Path, Depends, HTTPException
from schemas import UserCreate, UserUpdate, TokenData, StoreChat, ChatbotRequest, Message
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, get_db, engine
from models import Base, Chat
from auth import router as auth_router
import os
from typing import List
from fastapi.responses import FileResponse
from fastapi import Form
from chatbot import process_chat
from pydantic import BaseModel
from schemas import StoreChat
import models, schemas
from enum import Enum
# from constants import InteractionState

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000"
]

# # Initialize state dictionary globally
# state_dict = {}

# # Define utility functions for state management
# def get_current_state(user_id: str):
#     return state_dict.get(user_id, InteractionState.WELCOME)

# def set_current_state(user_id: str, new_state: InteractionState):
#     state_dict[user_id] = new_state

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/api/signup")
async def options_for_signup():
    return {}

@app.options("/api/login")
async def options_for_login():
    return {}

@app.options("/files/{filename}")
async def options_for_delete(filename: str):
    return {}

UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/files/")
async def create_upload_files(userId: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    user_dir = os.path.join(UPLOAD_DIR, userId)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    filename = file.filename
    file_path = os.path.join(user_dir, filename)
    with open(file_path, 'wb') as buffer:
        buffer.write(file.file.read())
    
    # Clear old messages if any
    old_messages = db.query(models.Chat).filter(models.Chat.user_id == int(userId)).all()
    for message in old_messages:
        db.delete(message)
    db.commit()

    # Generate new chatbot messages based on newly uploaded files
    new_messages = process_chat(userId)
    
    # Create and store these new messages in the database
    for msg in new_messages:
        await store_chat_message(StoreChat(user_id=int(userId), content=msg, sender="bot"), db)

    return {"filename": filename}


@app.get("/files/user/{userId}")
async def get_files(userId: str = Path(...)):
    user_dir = os.path.join(UPLOAD_DIR, userId)
    if not os.path.exists(user_dir):
        return {"filenames": []}

    file_list = os.listdir(user_dir)
    return {"filenames": file_list}

@app.delete("/files/{userId}/{filename}")
async def delete_file(userId: str, filename: str):
    user_dir = os.path.join(UPLOAD_DIR, userId)
    file_path = os.path.join(user_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "File deleted successfully"}
    else:
        return {"message": "File not found"}, 404

@app.get("/files/{userId}/{filename}")
async def get_file(userId: str, filename: str):
    user_dir = os.path.join(UPLOAD_DIR, userId)
    file_path = os.path.join(user_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv")
    else:
        return {"message": "File not found"}, 404




@app.get("/chat/user/{user_id}")
async def fetch_chat_history(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Chat).filter(models.Chat.user_id == user_id).all()
    if not messages:
        # Generate initial chatbot messages
        initial_messages = process_chat(str(user_id))

        # Create and store these messages in the database
        for msg in initial_messages:
            await store_chat_message(StoreChat(user_id=user_id, content=msg, sender="bot"), db)
        
        # Refetch the messages from the database to include the newly added ones
        messages = db.query(models.Chat).filter(models.Chat.user_id == user_id).all()

    return {"messages": [schemas.ChatOut.model_validate(message).model_dump() for message in messages]}

@app.post("/chat/")
async def store_chat_message(chat_data: StoreChat, db: Session = Depends(get_db)):
    chat_message = Chat(**chat_data.model_dump())
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return {"message_id": chat_message.id}

@app.delete("/chat/{user_id}/{message_id}")
async def delete_chat_message(user_id: str, message_id: int, db: Session = Depends(get_db)):
    message = db.query(Chat).filter(Chat.user_id == user_id, Chat.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}


@app.post("/api/interact_with_chatbot/")
async def interact_with_chatbot(request: ChatbotRequest):
    user_input = request.user_input
    user_id = request.user_id
    chatbot_reply = process_chat(user_id, user_input)
    
    # Store the user's message
    await store_chat_message(StoreChat(user_id=user_id, content=user_input, sender="user"), db=SessionLocal())
    
    chatbot_reply_string = ", ".join(chatbot_reply)
    # Store the chatbot's reply
    await store_chat_message(StoreChat(user_id=user_id, content=chatbot_reply_string, sender="bot"), db=SessionLocal())

    response = {
        "response": chatbot_reply
    }
    return response

@app.delete("/clearChat/user/{user_id}")
async def clear_chat_history(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Chat).filter(models.Chat.user_id == user_id).all()
    
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    
    # Delete all messages
    for message in messages:
        db.delete(message)
    
    db.commit()
    
    return {"message": "Chat history cleared successfully"}    

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)