def test_full_pipeline(planner, agent_engine, memory, mock_tools, sample_task):
    plan = planner.create_plan(sample_task)

    result = None

    for step in plan:
        result = agent_engine.execute(step, tools=mock_tools)
        memory.store(step["step"], result)

    assert result is not None
    assert len(memory.data) > 0
