import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_json(self, prompt: str):
        response = self.model.generate_content(prompt)
        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        return json.loads(text)

    def generate_text(self, prompt: str):
        response = self.model.generate_content(prompt)
        return response.text.strip()