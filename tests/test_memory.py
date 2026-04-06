def test_memory_store_and_retrieve(memory):
    memory.store("key1", "value1")

    result = memory.retrieve("key1")

    assert result == "value1"


def test_memory_overwrite(memory):
    memory.store("key1", "value1")
    memory.store("key1", "value2")

    result = memory.retrieve("key1")

    assert result == "value2"


def test_memory_capacity(memory):
    for i in range(1000):
        memory.store(f"k{i}", f"v{i}")

    assert len(memory.data) <= memory.max_size
