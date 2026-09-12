import os

import dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

from stacked_backend import router as stacked_router


dotenv.load_dotenv()

app = FastAPI()


# Connect Emilye's Stacked backend
app.include_router(stacked_router)


# Connect Gemini
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class ChatMessage(BaseModel):
    message: str


@app.post("/chat")
def chat(chat_message: ChatMessage):

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=chat_message.message
    )

    return {
        "response": response.text
    }