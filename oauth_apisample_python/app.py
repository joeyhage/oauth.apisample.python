from datetime import datetime
import os
import typing as t
from flask import Flask, Response, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.serving import WSGIRequestHandler, _log  # type: ignore[attr-defined]
from logging.config import dictConfig

dictConfig(
    {
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
)

app = Flask("oauth.apisample.python", static_folder=None)


@app.get("/health")
def health() -> Response:
    return jsonify(
        {
            "healthy": True,
            "timestamp": datetime.now()
            .astimezone()
            .replace(microsecond=0)
            .isoformat(),
        }
    )


@app.after_request
def add_headers(response: Response) -> Response:
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "deny"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.errorhandler(HTTPException)
def handle_http_exception(e: HTTPException) -> t.Tuple[str, int]:
    code = e.code or 500
    app.logger.error(
        "%s HTTPException. statusCode=%d", e.name, code, exc_info=e
    )
    if e.code:
        return e.name, code
    else:
        return "Server Error", code


@app.errorhandler(Exception)
def handle_exception(e: Exception) -> t.Tuple[str, int]:
    app.logger.error(
        "Uncaught application exception. statusCode=%d",
        500,
        exc_info=e,
        stack_info=False,
    )
    return "Server Error", 500


class CustomRequestHandler(WSGIRequestHandler):
    def log_request(self, code: int | str = "-", _: int | str = "-") -> None:
        app.logger.info(
            "type=request | method=%s | statusCode=%s | url=%s | ipAddress=%s",
            self.command,
            str(code),
            self.path,
            self.address_string(),
        )


if __name__ == "__main__":
    port = int(os.environ.get("FLASK_SERVER_PORT") or 9998)
    app.logger.info(f"Starting {app.name} on port {port}")
    app.run(
        host="0.0.0.0",
        port=port,
        request_handler=CustomRequestHandler,
        debug=os.environ.get("DEBUG") in {"true", "1"},
    )
