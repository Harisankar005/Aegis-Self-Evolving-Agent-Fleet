"""
http_tool.py
-----------------
A safe, MCP-style HTTP tool for Aegis agent fleet.

This tool allows agents to make controlled HTTP GET and POST requests with:
- Schema validation
- Domain allowlisting
- Trace instrumentation
- Mock-friendly operation
- Clean error handling
- Structured outputs

This file is tool-safe and suitable for inclusion in agent systems without exposing
security vulnerabilities. It can later be replaced with real HTTP clients (e.g., 'requests')
once proper sandboxing is applied.
"""

import json
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# Optional: uncomment for real HTTP support (disabled for safety)
# import requests


# ---------------------------
# Safe allowlist for domains
# ---------------------------
ALLOWED_DOMAINS = {
    "example.com",
    "jsonplaceholder.typicode.com",   # safe dummy API
    "api.publicapis.org",             # public demo API
}


# ---------------------------
# Trace helpers (compatible with orchestrator)
# ---------------------------
def trace_start(operation: str, meta: dict = None):
    return {
        "operation": operation,
        "start": time.time(),
        "meta": meta or {},
        "events": []
    }

def trace_end(span: dict, result: dict):
    span["end"] = time.time()
    span["duration"] = round(span["end"] - span["start"], 4)
    span["result"] = result
    return span


# ---------------------------
# Helper: validate allowed domain
# ---------------------------
def _is_domain_allowed(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = parsed.netloc
        # Basic match against allowlist
        for domain in ALLOWED_DOMAINS:
            if domain in host:
                return True
        return False
    except:
        return False


# ---------------------------
# Tool Definition
# ---------------------------
class HttpTool:
    """
    MCP-style HTTP GET/POST Tool.

    Tool schema:
    -------------
    input:
        {
            "method": "GET" | "POST",
            "url": "<full URL>",
            "params": {...}    # optional GET params
            "body": {...}      # optional POST body
        }

    output:
        {
            "status_code": int,
            "data": dict | str,
            "headers": dict,
            "trace": { ... }
        }

    In Kaggle demo mode, this tool returns MOCK_RESPONSES to ensure the
    project runs without external network calls.
    """

    MOCK_MODE = True  # change to False if enabling real HTTP later

    # Safe, local mock responses
    MOCK_RESPONSES = {
        "https://example.com/ping": {
            "status_code": 200,
            "data": {"message": "pong"},
            "headers": {"mock": "true"}
        },
        "https://jsonplaceholder.typicode.com/posts/1": {
            "status_code": 200,
            "data": {"id": 1, "title": "Mocked Post", "body": "Lorem ipsum"},
            "headers": {"mock": "true"}
        }
    }

    @classmethod
    def call(cls, args: Dict[str, Any]) -> Dict[str, Any]:
        # Validate schema
        method = args.get("method", "GET").upper()
        url = args.get("url")
        params = args.get("params", {})
        body = args.get("body", {})

        if url is None:
            raise ValueError("HTTP Tool requires a 'url' field.")

        # Safety: validate domain
        if not _is_domain_allowed(url):
            return {
                "status_code": 403,
                "error": f"Domain not allowed: {url}",
                "headers": {},
                "data": None,
                "trace": {"blocked": True, "reason": "Domain not in allowlist"}
            }

        # Start trace span
        span = trace_start("http_request", {"url": url, "method": method})

        # -----------------------
        # MOCK MODE (safe offline)
        # -----------------------
        if cls.MOCK_MODE:
            result = cls.MOCK_RESPONSES.get(
                url,
                {
                    "status_code": 200,
                    "data": {
                        "message": "Mock HTTP response",
                        "url": url,
                        "method": method,
                        "params": params,
                        "body": body,
                    },
                    "headers": {"mock": "true"}
                }
            )
            span = trace_end(span, result)
            result["trace"] = span
            return result

        # -----------------------
        # REAL NETWORK MODE
        # -----------------------
        # Uncomment to enable real HTTP
        """
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=5)

            elif method == "POST":
                response = requests.post(url, json=body, timeout=5)

            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            result = {
                "status_code": response.status_code,
                "data": response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text,
                "headers": dict(response.headers),
            }
        except Exception as e:
            result = {
                "status_code": 500,
                "error": str(e),
                "headers": {},
                "data": None
            }

        span = trace_end(span, result)
        result["trace"] = span
        return result
        """


# ---------------------------
# Export for MCP registry
# ---------------------------
def get_tool_definition():
    """Schema for MCP Gateway registration."""
    return {
        "name": "HttpTool",
        "description": "Performs safe HTTP GET or POST requests.",
        "input_schema": {
            "method": "GET or POST",
            "url": "string (required, must be in allowlist)",
            "params": "object (optional)",
            "body": "object (optional)"
        },
        "output_schema": {
            "status_code": "integer",
            "data": "object or string",
            "headers": "object",
            "trace": "object"
        }
    }
