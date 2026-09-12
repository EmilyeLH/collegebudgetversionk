
import os

import dotenv
from google import genai

dotenv.load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

while True: 
    userInput = input("You: ")
    if userInput.lower() == "exit":
        break
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=userInput
    )
    print(f"\nAI Chatbot: {response.text}")
    