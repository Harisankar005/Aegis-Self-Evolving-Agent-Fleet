class SearchTool:
    name = "SearchTool"
    description = "Performs a simple web search (mocked)."
    parameters = {
        "query": "Text query to search for"
    }

    def call(self, args, context):
        query = args.get("query")
        if not query:
            return {"error": "Missing required parameter: query"}

        # Mocked search results
        return {
            "results": [
                f"Result 1 for '{query}'",
                f"Result 2 for '{query}'",
                f"Meta information about '{query}'"
            ],
            "source": "MockSearch"
        }
