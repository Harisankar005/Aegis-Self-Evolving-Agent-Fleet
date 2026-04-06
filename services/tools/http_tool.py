"""
http_tool.py
------------
Safe, MCP-style HTTP GET/POST tool for Aegis agents.

Features:
✔ Domain allowlisting (safety)
✔ Mock mode (no network required for demos/tests)
✔ Trace instrumentation
✔ Clean error handling and structured output

MCP handler signature:
    http_tool(args: dict, context: Any) -> dict

FIX LOG (v2):
- Module-level http_tool() function added — tests imported "http_tool" as a
  function but v1 only exported the HttpTool class.
- http_get(url) convenience function added — tests directly call
  http_get("https://example.com/api/test") → NameError in v1.
- HttpTool.call() was a classmethod that returned None in MOCK_MODE when the
  URL was not in MOCK_RESPONSES (missing return statement in the fallback path).
  Fixed: fallback branch now always returns a valid dict.
- Output dict now always contains "url" and "status" fields so test assertions
  (out["url"], out["status"]) pass.
"""

import time
import uuid
from typing import Any, Dict
from urllib.parse import urlparse


# ─── Configuration ────────────────────────────────────────────────────────────

ALLOWED_DOMAINS = {
    "example.com",
    "jsonplaceholder.typicode.com",
    "api.publicapis.org",
}


# ─── Trace helpers ────────────────────────────────────────────────────────────

def _trace_start(operation: str, meta: Dict = None) -> Dict[str, Any]:
    return {
        "id":        str(uuid.uuid4()),
        "operation": operation,
        "start":     time.time(),
        "meta":      meta or {},
    }


def _trace_end(span: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    span["end"]      = time.time()
    span["duration"] = round(span["end"] - span["start"], 4)
    span["result"]   = result
    return span


# ─── Domain guard ─────────────────────────────────────────────────────────────

def _is_allowed(url: str) -> bool:
    try:
        host = urlparse(url).netloc
        return any(domain in host for domain in ALLOWED_DOMAINS)
    except Exception:
        return False


# ─── Core HttpTool class ──────────────────────────────────────────────────────

class HttpTool:
    """
    MCP-style HTTP GET/POST tool.

    Input schema:
        {
            "method": "GET" | "POST",     (default "GET")
            "url":    str,                (required)
            "params": dict,               (optional, GET query params)
            "body":   dict,               (optional, POST body)
        }

    Output:
        {
            "url":         str,
            "status":      "ok" | "mocked" | "blocked" | "error",
            "status_code": int,
            "data":        dict | str,
            "headers":     dict,
            "trace":       dict,
        }
    """

    MOCK_MODE = True

    MOCK_RESPONSES: Dict[str, Dict[str, Any]] = {
        "https://example.com/ping": {
            "status_code": 200,
            "data":        {"message": "pong"},
            "headers":     {"mock": "true"},
        },
        "https://jsonplaceholder.typicode.com/posts/1": {
            "status_code": 200,
            "data":        {"id": 1, "title": "Mocked Post", "body": "Lorem ipsum"},
            "headers":     {"mock": "true"},
        },
    }

    @classmethod
    def call(
        cls,
        args:    Dict[str, Any],
        context: Any = None,
    ) -> Dict[str, Any]:
        method = args.get("method", "GET").upper()
        url    = args.get("url")
        params = args.get("params", {})
        body   = args.get("body", {})

        if not url:
            return {
                "url":         "",
                "status":      "error",
                "status_code": 400,
                "data":        None,
                "headers":     {},
                "trace":       {},
                "error":       "Missing required field: 'url'",
            }

        # ── Safety check ──────────────────────────────────────────────────
        if not _is_allowed(url):
            return {
                "url":         url,
                "status":      "blocked",
                "status_code": 403,
                "data":        None,
                "headers":     {},
                "trace":       {"blocked": True, "reason": "Domain not in allowlist"},
                "error":       f"Domain not allowed: {url}",
            }

        span = _trace_start("http_request", {"url": url, "method": method})

        # ── Mock mode ─────────────────────────────────────────────────────
        if cls.MOCK_MODE:
            mock = cls.MOCK_RESPONSES.get(url) or {
                "status_code": 200,
                "data":        {
                    "message": "Mock HTTP response",
                    "url":     url,
                    "method":  method,
                    "params":  params,
                    "body":    body,
                },
                "headers": {"mock": "true"},
            }
            result = {
                "url":         url,
                "status":      "mocked",
                "status_code": mock["status_code"],
                "data":        mock["data"],
                "headers":     mock["headers"],
            }
            result["trace"] = _trace_end(span, result)
            return result

        # ── Real network mode (uncomment for production use) ──────────────
        # import requests
        # try:
        #     if method == "GET":
        #         resp = requests.get(url, params=params, timeout=5)
        #     elif method == "POST":
        #         resp = requests.post(url, json=body, timeout=5)
        #     else:
        #         raise ValueError(f"Unsupported method: {method}")
        #     ct = resp.headers.get("Content-Type", "")
        #     data = resp.json() if "application/json" in ct else resp.text
        #     result = {"url": url, "status": "ok", "status_code": resp.status_code,
        #               "data": data, "headers": dict(resp.headers)}
        # except Exception as exc:
        #     result = {"url": url, "status": "error", "status_code": 500,
        #               "data": None, "headers": {}, "error": str(exc)}
        # result["trace"] = _trace_end(span, result)
        # return result

        # Fallback (should not be reached in mock mode)
        return {
            "url":         url,
            "status":      "error",
            "status_code": 500,
            "data":        None,
            "headers":     {},
            "trace":       {},
            "error":       "Real network mode not enabled.",
        }


# ─── Module-level callables ───────────────────────────────────────────────────

def http_tool(
    args:    Dict[str, Any],
    context: Any = None,
) -> Dict[str, Any]:
    """Primary MCP handler for HttpTool."""
    return HttpTool.call(args, context)


def http_get(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience shortcut for GET requests.

    Parameters
    ----------
    url    : str — target URL (must be in ALLOWED_DOMAINS).
    params : dict — optional query parameters.
    """
    return HttpTool.call({"method": "GET", "url": url, "params": params or {}})


# ─── Schema for MCP registry ──────────────────────────────────────────────────

def get_tool_definition() -> Dict[str, Any]:
    return {
        "name":        "HttpTool",
        "description": "Performs safe HTTP GET or POST requests to allowlisted domains.",
        "input_schema": {
            "method": "string — GET or POST (default GET)",
            "url":    "string — required; must be in domain allowlist",
            "params": "object (optional) — GET query parameters",
            "body":   "object (optional) — POST request body",
        },
        "output_schema": {
            "url":         "string",
            "status":      "string — ok | mocked | blocked | error",
            "status_code": "integer",
            "data":        "object or string",
            "headers":     "object",
            "trace":       "object",
        },
    }
