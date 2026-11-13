from openai import OpenAI


def stream_model_response(
    message: str,
    api_key: str,
    model: str
):
    client = OpenAI(
        api_key=api_key
    )

    stream = client.responses.create(
        model=model,
        input=message,
        stream=True
    )

    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta