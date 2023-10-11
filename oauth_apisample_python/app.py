import os
import typing as t

from authlib.integrations.flask_oauth2 import ResourceProtector  # type: ignore[import]
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, Response, jsonify
from logging.config import dictConfig
from werkzeug.exceptions import HTTPException
from werkzeug.serving import WSGIRequestHandler

from .auth.validator import init_auth
from .config import LOGGING_CONFIG

load_dotenv()

dictConfig(LOGGING_CONFIG)

issuer = os.environ.get("OAUTH_ISSUER")
require_auth: ResourceProtector | None = None
if issuer:
    require_auth = init_auth(issuer, os.environ.get("OAUTH_AUDIENCE"))

app = Flask("oauth.apisample.python", static_folder=None)

with app.app_context():
    from .controller.company_controller import CompanyController

    base_path = "/investments"

    company_controller = CompanyController(require_auth)
    app.register_blueprint(
        company_controller.blueprint,
        url_prefix=f"{base_path}{company_controller.route}",
    )
    app.logger.debug(f"Registered {base_path}{company_controller.route}")


@app.get("/health")
def health() -> Response:
    ts = datetime.now().astimezone().replace(microsecond=0).isoformat()
    return jsonify(
        {
            "healthy": True,
            "timestamp": ts,
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
        "%s HTTPException. statusCode=%d",
        e.name,
        code,
        exc_info=e,
        stacklevel=0,
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
