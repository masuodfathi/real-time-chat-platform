import json
import logging
from time import perf_counter, sleep
from uuid import uuid4
from app.services.request_store import chat_requests
from flask import Blueprint, Response, jsonify, request

from app.services.chat_service import (
    build_ui_component,
    generate_mock_response,
    split_into_chunks,
)

chat_bp = Blueprint("chat", __name__)

logger = logging.getLogger("chat")


@chat_bp.post("/chat")
def create_chat_request():
    start_time = perf_counter()

    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    if not message:
        duration_ms = round(
            (perf_counter() - start_time) * 1000,
            2
        )

        logger.warning(
            "chat_request_rejected",
            extra={
                "endpoint": "/api/chat",
                "status": 400,
                "duration_ms": duration_ms,
            },
        )

        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    request_id = str(uuid4())

    chat_requests[request_id] = {
        "message": message
    }

    duration_ms = round(
        (perf_counter() - start_time) * 1000,
        2
    )

    logger.info(
        "chat_request_created",
        extra={
            "request_id": request_id,
            "endpoint": "/api/chat",
            "status": 201,
            "duration_ms": duration_ms,
        },
    )

    return jsonify({
        "requestId": request_id
    }), 201


@chat_bp.get("/chat/stream/<request_id>")
def stream_chat_response(request_id):
    chat_request = chat_requests.get(request_id)

    if not chat_request:
        logger.warning(
            "stream_request_not_found",
            extra={
                "request_id": request_id,
                "endpoint": "/api/chat/stream",
                "status": 404,
            },
        )

        return jsonify({
            "error": "Chat request not found."
        }), 404

    message = chat_request["message"]

    def generate():
        stream_start = perf_counter()

        first_chunk_sent = False

        logger.info(
            "stream_started",
            extra={
                "request_id": request_id,
                "endpoint": "/api/chat/stream",
            },
        )

        try:
            response_text = generate_mock_response(
                message
            )

            for chunk in split_into_chunks(
                response_text
            ):
                event = {
                    "type": "message.delta",
                    "data": {
                        "text": chunk
                    }
                }

                if not first_chunk_sent:
                    time_to_first_chunk_ms = round(
                        (
                            perf_counter()
                            - stream_start
                        ) * 1000,
                        2,
                    )

                    logger.info(
                        "first_chunk_sent",
                        extra={
                            "request_id": request_id,
                            "time_to_first_chunk_ms":
                                time_to_first_chunk_ms,
                        },
                    )

                    first_chunk_sent = True

                yield (
                    f"data: "
                    f"{json.dumps(event)}"
                    f"\n\n"
                )

                sleep(0.25)

            ui_component = build_ui_component(
                message
            )

            if ui_component:
                ui_event = {
                    "type": "ui.component",
                    "data": ui_component,
                }

                logger.info(
                    "ui_component_sent",
                    extra={
                        "request_id": request_id,
                        "component_type":
                            ui_component["type"],
                    },
                )

                yield (
                    f"data: "
                    f"{json.dumps(ui_event)}"
                    f"\n\n"
                )

            done_event = {
                "type": "message.done"
            }

            yield (
                f"data: "
                f"{json.dumps(done_event)}"
                f"\n\n"
            )

            duration_ms = round(
                (
                    perf_counter()
                    - stream_start
                ) * 1000,
                2,
            )

            logger.info(
                "stream_completed",
                extra={
                    "request_id": request_id,
                    "status": 200,
                    "duration_ms": duration_ms,
                },
            )

        except Exception:
            logger.exception(
                "stream_failed",
                extra={
                    "request_id": request_id,
                    "endpoint":
                        "/api/chat/stream",
                },
            )

            error_event = {
                "type": "error",
                "data": {
                    "message":
                        "Streaming interrupted."
                }
            }

            yield (
                f"data: "
                f"{json.dumps(error_event)}"
                f"\n\n"
            )

        finally:
            chat_requests.pop(
                request_id,
                None
            )

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )