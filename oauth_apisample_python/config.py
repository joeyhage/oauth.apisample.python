import os
import typing as t

LOGGING_CONFIG: t.Dict[str, t.Any] = {
    "version": 1,
    "formatters": {
        "default": {
            "format": f"[%(asctime)s | log_level=%(levelname)s | log_logger=%(name)s | log_message='%(message)s'",
        }
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default",
        }
    },
    "root": {
        "level": os.environ.get("LOG_LEVEL") or "INFO",
        "handlers": ["wsgi"],
    },
}
