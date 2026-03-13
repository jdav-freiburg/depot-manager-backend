import os
from datetime import date
from typing import Optional, List, Tuple

import httpx
from authlib.common.errors import AuthlibBaseError, AuthlibHTTPError
from authlib.integrations.starlette_client import OAuth
from authlib.jose.rfc7517.jwk import JsonWebKey
from authlib.jose.rfc7519.jwt import JsonWebToken
from authlib.oidc.core import UserInfo
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from depot_server.api.models import User
from depot_server.config import config
from depot_server.db import collections, DbReservation

AUTH_OFF = bool(os.getenv("NO_AUTH", False))

if AUTH_OFF:
    print("Running without authentication!")


oauth = OAuth()
# Prepare kwargs from pydantic model; ensure we don't accidentally register as OAuth1
# (authlib treats presence of `request_token_url` as OAuth1). Remove it if present.
oauth_kwargs = config.oauth2.model_dump()
oauth_kwargs.pop("request_token_url", None)
oauth.register('server', **oauth_kwargs)


async def parse_access_token_raw(token: str) -> dict:
    """Try to decode an access token as a JWT using provider JWKS.
    If decoding fails (opaque token), fall back to the provider `userinfo` endpoint.
    Returns a dict-like claims object.
    """
    if not token:
        raise ValueError("Missing token")

    # Try to decode as JWT using JWKS
    try:
        metadata = await oauth.server.load_server_metadata()
        jwks_uri = metadata.get("jwks_uri")
        if jwks_uri:
            async with httpx.AsyncClient() as client:
                r = await client.get(jwks_uri)
                r.raise_for_status()
                jwks = r.json()
            key_set = JsonWebKey.import_key_set(jwks)
            # allow common signing algorithms
            jwt = JsonWebToken(["RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "PS256", "PS384", "PS512", "HS256", "HS384", "HS512"])
            claims = jwt.decode(token, key_set)
            # validate time-based claims; use a small leeway
            try:
                claims.validate(leeway=120)
            except Exception:
                # validation failures should propagate as auth errors later
                pass
            return dict(claims)
    except Exception:
        # If any error occurs while decoding, we'll try userinfo below
        pass

    # Fallback: call userinfo endpoint
    try:
        userinfo = await oauth.server.userinfo(token={"token_type": "bearer", "access_token": token})
        return dict(userinfo)
    except Exception as e:
        raise

async def get_profile(user_id: str) -> dict:
    if AUTH_OFF:
        return {'sub': 'unknown', 'name': 'unknown', 'email': 'unknown.because@no.auth'}

    server_metadata = await oauth.server.load_server_metadata()
    issuer = server_metadata['issuer']
    profile_url = f"{issuer}/profiles/{user_id}"
    async with httpx.AsyncClient(auth=httpx.BasicAuth(config.oauth2.client_id, config.oauth2.client_secret)) as client:
        r = await client.get(profile_url)
        r.raise_for_status()
    return r.json()


async def get_profiles() -> List[dict]:
    if AUTH_OFF:
        return []

    server_metadata = await oauth.server.load_server_metadata()
    issuer = server_metadata['issuer']
    profiles_url = f"{issuer}/profiles"
    async with httpx.AsyncClient(auth=httpx.BasicAuth(config.oauth2.client_id, config.oauth2.client_secret)) as client:
        r = await client.get(profiles_url)
        r.raise_for_status()
    return r.json()


class Authentication:
    def __init__(
            self,
            require_manager: bool = False,
            require_admin: bool = False,
            auto_error: bool = True,
            require_userinfo: bool = False,
    ):
        self.require_manager = require_manager
        self.require_admin = require_admin
        self.auto_error = auto_error
        self.require_userinfo = require_userinfo

    async def __call__(
            self,
            authorization_code: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    ) -> Optional[UserInfo]:
        if AUTH_OFF:
            return UserInfo({'email': 'local@freiburg.jdav', 'name': 'local-fake-user', 'given_name': 'Local Fake User', 'roles': ['admin', 'manager'], 'sub': 'unknown'})
        if authorization_code is None:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            return None
        try:
            token_data = await parse_access_token_raw(authorization_code.credentials)
        except AuthlibHTTPError as e:
            raise HTTPException(*e())
        except AuthlibBaseError as e:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"{e.error}: {e.description}")
        if self.require_admin and 'admin' not in token_data['roles']:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Need admin"
                )
            return None
        if self.require_manager and ('manager' not in token_data['roles'] and 'admin' not in token_data['roles']):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Need manager"
                )
            return None
        if self.require_userinfo:
            userinfo = await oauth.server.userinfo(
                token={'token_type': 'bearer', 'access_token': authorization_code.credentials}
            )
            token_data.update(userinfo)
        return token_data


class DeviceAuthentication:
    def __init__(
            self,
            auto_error: bool = True,
    ):
        self.auto_error = auto_error

    async def __call__(
            self,
            device_api_key: Optional[str] = Depends(APIKeyHeader(name="X-Device-Api-Key", auto_error=False)),
            reservation_code: Optional[str] = Depends(APIKeyHeader(name="X-Reservation-Code", auto_error=False)),
    ) -> Tuple[Optional[User], Optional[DbReservation]]:
        if device_api_key is None or reservation_code is None:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            return None, None
        if device_api_key != config.device_api_key:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
        reservation = await collections.reservation_collection.find_one(
            {'code': reservation_code, 'start': {'$lte': date.today().toordinal()}},
        )
        if reservation is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No reservation for token")
        user_id = reservation.user_id
        profile = await get_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No profile for user id")

        return User.model_validate(profile), reservation
