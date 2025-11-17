import math

SAFE_GLOBALS = {
    "__builtins__": {},
    "math": math
}

class CodeExecutionTool:
    name = "CodeExecutionTool"
    description = "Executes Python code safely in a sandbox."
    parameters = {
        "code": "Python code to execute (limited sandbox)"
    }

    def call(self, args, context):
        code = args.get("code")
        if not code:
            return {"error": "Missing code"}

        local_vars = {}

        try:
            exec(code, SAFE_GLOBALS, local_vars)
            return {"output": local_vars}
        except Exception as e:
            return {"error": str(e)}
