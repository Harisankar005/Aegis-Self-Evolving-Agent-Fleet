import pytest

@pytest.fixture
def sample_task():
    return {
        "id": "task_1",
        "input": "Summarize the benefits of AI in healthcare",
    }

@pytest.fixture
def mock_plan():
    return [
        {"step": "research", "agent": "researcher"},
        {"step": "summarize", "agent": "writer"},
    ]

@pytest.fixture
def mock_memory():
    return {}

@pytest.fixture
def mock_tools():
    return {
        "search": lambda q: f"results for {q}",
        "summarize": lambda x: f"summary of {x}",
    }
