def test_agent_execution(agent_engine, mock_tools):
    task = {"input": "find AI trends"}

    result = agent_engine.execute(task, tools=mock_tools)

    assert result is not None
    assert isinstance(result, dict) or isinstance(result, str)


def test_agent_handles_tool_failure(agent_engine):
    def failing_tool(_):
        raise RuntimeError("Tool failure")

    tools = {"search": failing_tool}

    task = {"input": "test failure"}

    result = agent_engine.execute(task, tools=tools)

    assert result is not None  # system should degrade gracefully


def test_agent_output_schema(agent_engine, mock_tools):
    task = {"input": "analyze data"}

    result = agent_engine.execute(task, tools=mock_tools)

    assert "output" in result or isinstance(result, str)
