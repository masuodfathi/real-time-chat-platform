from groq import Groq


def stream_model_response(
    message: str,
    api_key: str,
    model: str
):
    client = Groq(
        api_key=api_key
    )

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
        stream=True
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content

        if content:
            yield content