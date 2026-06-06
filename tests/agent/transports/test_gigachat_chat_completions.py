from types import SimpleNamespace

from agent.transports.chat_completions import ChatCompletionsTransport
from providers import get_provider_profile


def test_gigachat_tools_are_sent_as_top_level_functions():
    profile = get_provider_profile("gigachat")
    transport = ChatCompletionsTransport()
    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write a file",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
        }
    ]

    kwargs = transport.build_kwargs(
        model="GigaChat-Max",
        messages=[{"role": "user", "content": "Create a file"}],
        tools=tools,
        provider_profile=profile,
    )

    assert "tools" not in kwargs
    assert "extra_body" not in kwargs
    assert kwargs["functions"] == [tools[0]["function"]]
    assert kwargs["function_call"] == "auto"


def test_gigachat_legacy_function_call_normalizes_to_tool_call():
    transport = ChatCompletionsTransport()
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="function_call",
                message=SimpleNamespace(
                    content=None,
                    tool_calls=None,
                    function_call={
                        "name": "write_file",
                        "arguments": {"path": "test.txt", "content": "hello"},
                    },
                ),
            )
        ],
        usage=None,
    )

    normalized = transport.normalize_response(response)

    assert normalized.tool_calls is not None
    assert normalized.tool_calls[0].id == "call_write_file"
    assert normalized.tool_calls[0].name == "write_file"
    assert normalized.tool_calls[0].arguments == '{"path": "test.txt", "content": "hello"}'


def test_gigachat_replay_converts_tool_call_arguments_to_object():
    profile = get_provider_profile("gigachat")
    messages = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_write_file",
                    "call_id": "call_write_file",
                    "response_item_id": "fc_write_file",
                    "type": "function",
                    "function": {
                        "name": "write_file",
                        "arguments": '{"path": "gigachat_test.txt", "content": "hello"}',
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_write_file",
            "content": '{"success": true}',
        },
    ]

    prepared = profile.prepare_messages(messages)

    assert prepared[0] == {
        "role": "assistant",
        "content": "",
        "function_call": {
            "name": "write_file",
            "arguments": {"path": "gigachat_test.txt", "content": "hello"},
        },
    }
    assert prepared[1] == {
        "role": "function",
        "name": "write_file",
        "content": '{"success": true}',
    }
