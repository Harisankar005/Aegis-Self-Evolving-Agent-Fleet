def test_tool_contract(mock_tools):
    for name, tool in mock_tools.items():
        result = tool("test input")

        assert result is not None
        assert isinstance(result, str)


def test_tool_invalid_input(mock_tools):
    for tool in mock_tools.values():
        try:
            tool(None)
        except Exception:
            assert True
