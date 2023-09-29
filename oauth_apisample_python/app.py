import os
from typing import Tuple
from flask import Flask, Response, jsonify
from werkzeug.exceptions import HTTPException
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": f"[%(asctime)s | log_level=%(levelname)s | log_logger=%(name)s | log_message=%(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask("oauth.apisample.python", static_folder=None)


@app.get("/health")
def health() -> Response:
    app.logger.debug("GET /health")
    return jsonify({"healthy": True})


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
def handle_http_exception(e: HTTPException) -> Tuple[str, int]:
    app.logger.error(
        "%s HTTPException. statusCode=%d", e.name, e.code, exc_info=e
    )
    if e.code:
        return e.name, e.code
    else:
        return "Server Error", 500


@app.errorhandler(Exception)
def handle_exception(e: Exception) -> Tuple[str, int]:
    app.logger.error("Uncaught application exception", exc_info=e)
    return "Server Error", 500


if __name__ == "__main__":
    app.logger.info(f"Starting up...")
    app.run(host='0.0.0.0', port=int(os.environ.get("FLASK_SERVER_PORT") or 9998))
