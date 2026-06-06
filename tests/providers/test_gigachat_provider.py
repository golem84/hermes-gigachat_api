from types import SimpleNamespace

from agent.transports.chat_completions import ChatCompletionsTransport
from providers import get_provider_profile


def test_gigachat_tools_are_sent_as_legacy_functions_extra_body():
    profile = get_provider_profile("gigachat")
    assert profile is not None

    kwargs = ChatCompletionsTransport().build_kwargs(
        "GigaChat-Max",
        [{"role": "user", "content": "use a tool"}],
        [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a file",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ],
        provider_profile=profile,
    )

    assert "tools" not in kwargs
    assert kwargs["extra_body"]["functions"] == [
        {
            "name": "read_file",
            "description": "Read a file",
            "parameters": {"type": "object", "properties": {}},
        }
    ]


def test_gigachat_prepare_messages_converts_tool_result_to_function_message():
    profile = get_provider_profile("gigachat")
    assert profile is not None

    [message] = profile.prepare_messages(
        [
            {
                "role": "tool",
                "tool_call_id": "call_read_file",
                "content": "contents",
            }
        ]
    )

    assert message == {
        "role": "function",
        "name": "read_file",
        "content": "contents",
    }


def test_chat_completions_normalizes_legacy_function_call():
    msg = SimpleNamespace(
        content=None,
        tool_calls=None,
        function_call={"name": "read_file", "arguments": {"path": "README.md"}},
        reasoning=None,
    )
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=msg, finish_reason="function_call")],
        usage=None,
    )

    normalized = ChatCompletionsTransport().normalize_response(response)

    assert normalized.tool_calls is not None
    assert normalized.tool_calls[0].id == "call_read_file"
    assert normalized.tool_calls[0].name == "read_file"
    assert normalized.tool_calls[0].arguments == '{"path": "README.md"}'
