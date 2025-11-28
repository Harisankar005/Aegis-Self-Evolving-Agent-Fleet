"""
AgentCreator: A meta-agent that generates new agent specifications when the
evaluation pipeline detects missing capabilities.

This class supports:
- Gap detection
- Agent spec generation (schema)
- Optional LLM-based generation (stub only)
- Registration into the MCP gateway
- Logging + trace-friendly outputs

All external LLM calls must be added by the user (NO API KEYS here).
"""

import uuid
import json
from datetime import datetime
from rich import print as rprint


class AgentCreator:
    """
    AgentCreator dynamically generates new agent definitions.

    It produces:
    - Agent name
    - Description
    - Input schema
    - Output schema
    - Example I/O for few-shot prompting
    """

    def __init__(self, registry, llm_client=None):
        """
        Args:
            registry: Reference to MCP-style registry for registering agents.
            llm_client: Optional LLM client for generating agent specs.
                        Not used in this offline-capable version.
        """
        self.registry = registry
        self.llm = llm_client  # Optional for production expansions

    # ----------------------------------------------------------------------
    # 1. CAPABILITY GAP DETECTION
    # ----------------------------------------------------------------------
    def detect_missing_capabilities(self, judge_feedback: dict) -> str:
        """
        Example capability detection from judge feedback.

        judge_feedback = {
            "score": 0.72,
            "notes": "Missing analytics step. No post-campaign insights."
        }

        Returns a capability label like "analytics" or "monitoring".
        """
        notes = judge_feedback.get("notes", "").lower()

        if "analytics" in notes:
            return "analytics"
        if "monitor" in notes:
            return "monitoring"
        if "sentiment" in notes:
            return "sentiment-analysis"

        # Default fallback
        return "general-enhancement"

    # ----------------------------------------------------------------------
    # 2. AGENT SPEC GENERATION
    # ----------------------------------------------------------------------
    def generate_agent_spec(self, capability: str) -> dict:
        """
        Creates a new agent specification using templates.

        In a real deployment, this would call LLM; here it uses templates
        so the project stays API-key safe and runnable on Kaggle.
        """

        agent_name = f"{capability.capitalize()}Agent"
        unique_id = uuid.uuid4().hex[:6]

        spec = {
            "id": f"{agent_name}-{unique_id}",
            "name": agent_name,
            "description": f"Auto-generated agent for {capability} tasks.",
            "capability": capability,
            "created_at": str(datetime.utcnow()),
            "input_schema": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": f"Input for {agent_name}"}
                },
                "required": ["input"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": f"Generated {capability} output"}
                }
            },
            "examples": {
                "input": {"input": f"Run {capability} on campaign metrics"},
                "output": {"result": f"Mock {capability} insights"}
            }
        }

        return spec

    # ----------------------------------------------------------------------
    # 3. AGENT IMPLEMENTATION (PYTHON CALLABLE)
    # ----------------------------------------------------------------------
    def build_python_implementation(self, capability: str):
        """
        Returns a Python function that implements the new agent.
        Simple mock implementation to keep project API-key-free.
        """

        def dynamic_agent_fn(args, ctx=None):
            text = args.get("input", "")
            return {
                "result": f"[Auto-generated {capability} analysis] Processed: '{text}'",
                "confidence": 0.95
            }

        return dynamic_agent_fn

    # ----------------------------------------------------------------------
    # 4. FULL PIPELINE: DETECT → SPEC → REGISTER → IMPLEMENT
    # ----------------------------------------------------------------------
    def generate_new_agent(self, judge_feedback: dict) -> dict:
        """
        End-to-end process invoked by orchestrator:
        - Detect missing capability
        - Generate agent spec
        - Generate python implementation
        - Register agent into MCP registry
        """

        capability = self.detect_missing_capabilities(judge_feedback)
        rprint(f"[yellow]Detected missing capability:[/] {capability}")

        spec = self.generate_agent_spec(capability)
        rprint(f"[cyan]Generated Agent Spec for:[/] {spec['name']}")

        impl = self.build_python_implementation(capability)

        # Register in the MCP registry
        self.registry.register_agent(
            name=spec["name"],
            description=spec["description"],
            func=impl,
            spec=spec  # store JSON spec in registry for documentation
        )

        rprint(f"[green]Registered new agent:[/] {spec['name']}")
        return spec

    # ----------------------------------------------------------------------
    # 5. OPTIONAL: EXPORT SPEC FOR DOCUMENTATION
    # ----------------------------------------------------------------------
    def save_spec_to_file(self, spec: dict, path: str):
        """Save the generated agent spec to disk (optional)."""
        with open(path, "w") as f:
            json.dump(spec, f, indent=4)
        rprint(f"[blue]Saved agent spec to[/] {path}")
