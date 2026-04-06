import random

def test_random_failures(agent_engine, mock_tools):
    def flaky_tool(x):
        if random.random() < 0.3:
            raise RuntimeError("Random failure")
        return f"ok {x}"

    tools = {"search": flaky_tool}

    task = {"input": "stress test"}

    result = agent_engine.execute(task, tools=tools)

    assert result is not None
