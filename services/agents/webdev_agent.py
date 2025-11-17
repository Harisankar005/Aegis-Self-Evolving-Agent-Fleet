class WebDevAgent:
    """
    Agent: WebDevAgent
    Purpose: Produce simple HTML landing pages or assets for campaigns.
    """

    def __init__(self):
        self.name = "WebDevAgent"
        self.description = "Builds simple landing pages or HTML mockups."

    def call(self, args, session):
        brief = args.get("brief", "Product")

        html = f"""
        <html>
            <head><title>{brief} - Landing Page</title></head>
            <body>
                <h1>Welcome to {brief}</h1>
                <p>Your next generation solution for speed and simplicity.</p>
            </body>
        </html>
        """

        artifact = {
            "url": "https://example.com/generated-landing-page",
            "html": html.strip()
        }

        session.append_event(self.name, artifact)
        return artifact
