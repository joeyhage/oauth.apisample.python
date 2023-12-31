# mypy: disable-error-code="misc"

from authlib.integrations.flask_oauth2 import ResourceProtector  # type: ignore[import]
from flask import Blueprint, jsonify, request as req, Response


class CompanyController:
    def __init__(self, require_auth: ResourceProtector | None) -> None:
        self.blueprint = Blueprint("company", __name__)
        self.route = "/companies"

        if require_auth:
            _setup_routes(self.blueprint, require_auth)


def _setup_routes(
    blueprint: Blueprint, require_auth: ResourceProtector
) -> None:
    @blueprint.get("/")
    @require_auth()
    def companies() -> Response:
        return jsonify(
            [
                {
                    "id": 1,
                    "name": "Company 1",
                    "region": "Europe",
                    "targetUsd": 20000000,
                    "investmentUsd": 13801299,
                    "noInvestors": 2310,
                },
                {
                    "id": 2,
                    "name": "Company 2",
                    "region": "USA",
                    "targetUsd": 35000000,
                    "investmentUsd": 41251365,
                    "noInvestors": 3951,
                },
                {
                    "id": 3,
                    "name": "Company 3",
                    "region": "Asia",
                    "targetUsd": 70000000,
                    "investmentUsd": 59621800,
                    "noInvestors": 10133,
                },
                {
                    "id": 4,
                    "name": "Company 4",
                    "region": "USA",
                    "targetUsd": 25000000,
                    "investmentUsd": 7114335,
                    "noInvestors": 1201,
                },
            ]
        )
