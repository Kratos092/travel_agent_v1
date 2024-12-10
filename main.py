import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
#from app.agents.utils import generate_llm_response, context
import app.agents.utils as utils
from app.database_module.database import *
# create_tables, save_session, load_messages, delete_session, list_sessions, save_message,rename_session
import numpy as np
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

create_tables()  # Initialize the database tables

app = FastAPI()

# Mount static files for the frontend
app.mount("/frontend", StaticFiles(directory="frontend",html=True), name="frontend")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Travel Agent v1!"}

class Query(BaseModel):
    question: str
    mode: str  # Toggle switch for 'rag' or 'agent'

@app.post("/query")
async def get_response(query: Query, background_tasks: BackgroundTasks):
    if query.mode not in ["agent"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'agent'.")

 
    
    response_text = utils.generate_llm_response(query.question)

    # Add the text_to_speech function to the background tasks
#        background_tasks.add_task(text_to_speech, response_text)  # Run in the background

    return {
        "text_response": response_text,
        # No need for 'voice_response' since audio plays live
    }

class SessionName(BaseModel):
    session_name: str


@app.post("/save_session")
async def save_chat_session(session: SessionName):
    try:
        save_session(session.session_name)  # Use session.session_name to get the name
        return {"message": "Session saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/load_session/{session_name}")
async def load_chat_session(session_name: str):
    messages = load_messages(session_name)
    # build context while loading session
    #global context
    if utils.context:
        utils.context.clear()
    utils.context = [
    {"role": "system", "content": utils.router_instructions},
    ]
    utils.context.extend([
    {"role": "user", "content": user} 
    if i % 2 == 0 else {"role": "assistant", "content": bot}
    for i, (user, bot) in enumerate(messages)
    ])
#    print(utils.context)
    if not messages:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"messages": [{"user_message": user, "bot_response": bot} for user, bot in messages]}

@app.delete("/delete_session/{session_name}")
async def delete_chat_session(session_name: str):
    try:
        delete_session(session_name)
        return {"message": "Session deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_sessions")
async def list_chat_sessions():
    try:
        sessions = list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class SaveMessageRequest(BaseModel):
    session_name: str
    user_message: str
    bot_response: str

@app.post("/save_message")
async def save_message_endpoint(message: SaveMessageRequest):
    logger.info(f"Saving message: {message}")
    try:
        save_message(message.session_name, message.user_message, message.bot_response)
        # adding to current context
        utils.context.append({"role":"user","content": message.user_message, "role":"system","content": message.bot_response})
        return {"detail": "Message saved successfully."}
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# useless load_messages_endpoint

class RenameSessionRequest(BaseModel):
    new_session_name: str

@app.put("/rename_session/{old_session_name}")
async def rename_session_route(old_session_name: str, request: RenameSessionRequest):
    print(f"Old session name: {old_session_name}, New session name: {request.new_session_name}")  # Add this line
    try:
        rename_session(old_session_name, request.new_session_name)  # Call the function from database.py
        return {"message": f"Session renamed from {old_session_name} to {request.new_session_name}"}
    except Exception as e:
        return {"error": str(e)}, 500



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
