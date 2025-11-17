class CopyAgent:
    """
    Agent: CopyAgent
    Purpose: Produce marketing copy, ad scripts, headlines, blogs, and UX text.
    """

    def __init__(self):
        self.name = "CopyAgent"
        self.description = "Writes marketing copy based on a brief or product details."

    def call(self, args, session):
        brief = args.get("brief", "")
        copy = {
            "headline": f"Introducing {brief} — Designed to Make Life Easier",
            "body": f"Our latest solution ({brief}) boosts productivity effortlessly.",
        }

        session.append_event(self.name, copy)
        return copy
