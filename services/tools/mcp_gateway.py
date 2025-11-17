class MCPRegistry:
    """
    MCP-style registry for tools & agents.
    Each tool/agent exposes:
        - name
        - description
        - parameters (dict)
        - call(args, context)
    """

    def __init__(self):
        self.registry = {}

    def register(self, tool):
        """Register a tool or agent with name + spec."""
        name = tool.name
        self.registry[name] = tool
        print(f"[MCP] Registered tool/agent: {name}")

    def get(self, name):
        """Retrieve a tool by name."""
        if name not in self.registry:
            raise KeyError(f"Tool/Agent '{name}' not found in MCP registry")
        return self.registry[name]

    def list_tools(self):
        """Return all available tool definitions."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": getattr(t, "parameters", {})
            }
            for t in self.registry.values()
        ]
