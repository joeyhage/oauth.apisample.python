import json
from urllib.request import urlopen

from authlib.integrations.flask_oauth2 import ResourceProtector  # type: ignore[import]
from authlib.jose.rfc7517.jwk import JsonWebKey  # type: ignore[import]
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator  # type: ignore[import]


class JwtValidator(JWTBearerTokenValidator):  # type: ignore[misc]
    def __init__(self, issuer: str, audience: str | None) -> None:
        jsonurl = urlopen(f"{issuer}/.well-known/jwks.json")
        public_key = JsonWebKey.import_key_set(json.loads(jsonurl.read()))

        super(JwtValidator, self).__init__(public_key)

        if audience:
            self.claims_options["aud"] = {"essential": True, "value": audience}


def init_auth(issuer: str, audience: str | None) -> ResourceProtector:
    require_auth = ResourceProtector()
    validator = JwtValidator(issuer, audience)
    require_auth.register_token_validator(validator)
    return require_auth
