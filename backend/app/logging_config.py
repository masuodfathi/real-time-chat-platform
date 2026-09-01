import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        optional_fields = [
            "request_id",
            "endpoint",
            "status",
            "duration_ms",
            "time_to_first_chunk_ms",
            "component_type",
        ]

        for field in optional_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        if record.exc_info:
            log_data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_data,
            ensure_ascii=False
        )


def configure_logging():
    logger = logging.getLogger("chat")

    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        handler.setFormatter(
            JsonFormatter()
        )

        logger.addHandler(handler)

    logger.propagate = False

    return logger