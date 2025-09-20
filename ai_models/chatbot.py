# backend/ai_models/chatbot.py

from pydantic import BaseModel
from openai import OpenAI
import os

# Initialize router
# Connect to local Ollama server
client = OpenAI(
    base_url=os.getenv("base_url"),
    api_key="ollama",  # required but not used by Ollama
)

# Request model
class ChatRequest(BaseModel):
    user_message: str

# Response model
class ChatResponse(BaseModel):
    reply: str

# Predefined system prompt for climate tutor
SYSTEM_PROMPT = (
    "You are ClimateBuddy, an AI tutor that helps learners understand climate change. "
    "Explain climate science concepts in simple, clear terms, use local-language examples if possible, "
    "and adapt explanations to the user's age or knowledge level. Encourage actionable steps "
    "and connect lessons to real-life behavior."
)


async def chat( user_message:str):
    """
    Send a user message to the AI tutor and return the assistant's reply.
    """
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        response = client.chat.completions.create(
            model="llama3.1:latest",
            messages=messages
        )
        assistant_reply = response.choices[0].message["content"]
        return ChatResponse(reply=assistant_reply)
    except Exception as e:
        pass
