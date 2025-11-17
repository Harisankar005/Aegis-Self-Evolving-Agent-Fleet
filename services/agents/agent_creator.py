import uuid

class AgentCreator:
    """
    Meta-agent that generates new agents or tools when gaps in capability are detected.
    Mimics a Level-4 evolving agent that expands its own skillset.
    """

    def __init__(self, registry):
        self.registry = registry

    def generate_new_agent(self, capability_name: str):
        """
        Generates a new agent dynamically and registers it in the tool registry.
        """

        agent_name = f"{capability_name.capitalize()}Agent"
        agent_id = str(uuid.uuid4())

        spec = {
            "id": agent_id,
            "name": agent_name,
            "description": f"Auto-generated agent to handle {capability_name} tasks.",
            "version": "1.0",
            "schema": {
                "args": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }
        }

        print(f"[AgentCreator] Generated new agent: {agent_name}")
        self.registry.register_spec(spec)
        return spec
