def test_agent_creation_trigger(agent_creator):
    missing_capability = "code_generation"

    agent = agent_creator.create_if_missing(missing_capability)

    assert agent is not None
    assert agent["capability"] == missing_capability


def test_agent_versioning(agent_creator):
    agent_v1 = agent_creator.create("researcher")
    agent_v2 = agent_creator.create("researcher")

    assert agent_v1 != agent_v2
    assert agent_v2["version"] > agent_v1["version"]
