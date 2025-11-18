import google.generativeai as genai
import os

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Environment variable GEMINI_API_KEY not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
