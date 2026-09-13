import os
from fastapi.middleware.cors import CORSMiddleware

import dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

from stacked_backend import router as stacked_router




dotenv.load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
You are Bank Roll AI, a budgeting assistant for college students.

Give practical, student-friendly financial advice.
Keep your response concise and easy to scan.
Use no more than 3 short suggestions.
Keep the entire response under 100 words.
Do not give long explanations.

Student's question:
{chat_message.message}
"""
        )

        return {
            "response": response.text
        }

    except Exception as e:
        print("Gemini error:", e)

        return {
            "response": "Gemini is temporarily busy. Please try again in a moment."
        }
