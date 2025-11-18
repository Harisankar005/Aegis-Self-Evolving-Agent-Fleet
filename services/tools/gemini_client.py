import os
import google.generativeai as genai


class GeminiClient:
    """
    Minimal client wrapper for Gemini models.
    Ensures a consistent interface for agent modules.
    """

    def __init__(self, model_name: str = "gemini-pro"):
        api_key = os.getenv("AIzaSyDoWv4xzkgtemxwHK7IdVvBZZFJc19AWS4")
        if not api_key:
            raise ValueError(
                "Environment variable GEMINI_API_KEY is required but not set."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        """
        Generates text from the model based on the given prompt.
        """
        response = self.model.generate_content(prompt)
        return response.text
