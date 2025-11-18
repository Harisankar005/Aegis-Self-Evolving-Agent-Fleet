from typing import Dict, Any
from services.tools.gemini_client import GeminiClient

class CopyAgent:
    """
    Generates marketing copy such as headlines and short descriptions
    based on a brief provided by the orchestrator.
    """
    name = "CopyAgent"
    description = "Generates marketing copy from a provided brief."

    def __init__(self):
        self.llm = GeminiClient()

    def call(self, args: Dict[str, Any], session: Any) -> Dict[str, Any]:
        brief = args.get("brief", "")

        prompt = (
            "Write a concise marketing headline and subheading based on the brief:\n"
            f"{brief}\n\n"
            "Output should be in JSON format:\n"
            "{\n"
            "  \"headline\": \"...\",\n"
            "  \"subheading\": \"...\"\n"
            "}\n"
        )

        response = self.llm.generate(prompt)

        return {
            "agent": self.name,
            "output": response
        }
