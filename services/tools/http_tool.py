import requests

class HttpTool:
    name = "HttpTool"
    description = "Performs HTTP GET/POST requests."
    parameters = {
        "url": "Full URL",
        "method": "'GET' or 'POST'",
        "data": "Optional JSON payload"
    }

    def call(self, args, context):
        url = args.get("url")
        method = args.get("method", "GET").upper()
        data = args.get("data")

        if not url:
            return {"error": "Missing URL"}

        try:
            if method == "GET":
                r = requests.get(url)
            elif method == "POST":
                r = requests.post(url, json=data or {})
            else:
                return {"error": f"Unsupported method {method}"}

            return {
                "status": r.status_code,
                "response": r.text[:500]
            }
        except Exception as e:
            return {"error": str(e)}
