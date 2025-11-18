import json
from typing import Dict, Any
from services.tools.gemini_client import GeminiClient

class AgentCreator:
    """
    Creates new agents at runtime based on capability requirements.
    The generated agent is a callable object compatible with the MCP registry.
    """

    def __init__(self, registry):
        self.registry = registry
        self.llm = GeminiClient()

    def generate_new_agent(self, capability: str) -> Dict[str, Any]:
        """
        Creates a new agent specification and runtime implementation.
        Returns:
            spec: Metadata describing the agent.
            agent_instance: The instantiated agent class ready to register.
        """
        prompt = f"""
        Create a new agent specification for a capability called "{capability}".
        Define:
        - name: PascalCase agent name
        - description: a single-sentence description of its purpose
        - sample_prompt: template prompt the agent should use when performing its task
        Respond only with JSON:
        {{
            "name": "...",
            "description": "...",
            "sample_prompt": "..."
        }}
        """

        response = self.llm.generate(prompt)
        spec = json.loads(response)

        agent_instance = self._build_agent_class(
            name=spec["name"],
            base_prompt=spec["sample_prompt"]
        )

        return spec, agent_instance

    def _build_agent_class(self, name: str, base_prompt: str):
        """
        Dynamically generates a callable agent class using the provided prompt.
        """

        class DynamicAgent:
            def __init__(self, name: str, base_prompt: str):
                self.name = name
                self.base_prompt = base_prompt
                self.llm = GeminiClient()

            def call(self, args: Dict[str, Any], session: Any) -> Dict[str, Any]:
                filled_prompt = self.base_prompt.format(**args)
                output = self.llm.generate(filled_prompt)
                return {"agent": self.name, "output": output}

        return DynamicAgent(name, base_prompt)
