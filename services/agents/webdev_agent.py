from typing import Dict, Any
from services.tools.gemini_client import GeminiClient

class WebDevAgent:
    name = "WebDevAgent"
    description = "Generates simple HTML landing pages from a brief."

    def __init__(self):
        self.llm = GeminiClient()

    def call(self, args: Dict[str, Any], session: Any) -> Dict[str, Any]:
        brief = args.get("brief", "")

        prompt = (
            "Generate clean, responsive HTML for a landing page based on the following brief:\n"
            f"{brief}\n\n"
            "The layout should include a headline, subheadline, features section, and call-to-action button. "
            "Return only HTML code without explanations."
        )

        html_output = self.llm.generate(prompt)

        result = {
            "agent": self.name,
            "output": {
                "html": html_output,
                "meta": {
                    "length": len(html_output),
                    "summary": "Landing page HTML generated."
                }
            }
        }

        return result
