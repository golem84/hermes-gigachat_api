import inspect

from agent import conversation_loop


def test_gigachat_function_calling_uses_non_streaming_path():
    source = inspect.getsource(conversation_loop.run_conversation)

    assert "gigachat" in source
    assert 'api_kwargs.get("functions")' in source
    assert "_use_streaming = False" in source
