from groq import Groq


def stream_model_response(
    messages: list[dict[str, str]],
    api_key: str,
    model: str,
):
    client = Groq(api_key=api_key)

    # Send the conversation history and the latest user message.
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content
        if content:
            yield content