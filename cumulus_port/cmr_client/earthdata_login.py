# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/cmr-client/src/EarthdataLogin.ts

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

import jwt

from cumulus_port.common import parse_caught_error


def get_edl_url(env: str) -> str:
    """Get the Earthdata Login endpoint URL based on the EDL environment

    :param env: the environment of the Earthdata Login (ex. 'SIT')
    :returns: str - the endpoint URL
    """
    if env in ("PROD", "OPS"):
        return "https://urs.earthdata.nasa.gov"
    if env == "UAT":
        return "https://uat.urs.earthdata.nasa.gov"

    return "https://sit.urs.earthdata.nasa.gov"


def parse_http_error(
    error: urllib.error.HTTPError,
    request_type: str,
) -> Exception:
    """Parse and handle error returned from EDL endpoint

    :param error: the HTTP error response returned by the EarthdataLogin
        endpoint
    :param request_type: the type of token request
        (options: 'retrieve', 'create', 'revoke')
    :returns: Exception - EarthdataLogin error
    """
    status_code = error.code
    status_message = error.reason or "Unknown"
    # In JavaScript the request_type is used to determine whether or not to
    # serialize the response body. In Python, the body is not deserialized for
    # us, so we know that we never need to serialize it again. request_type is
    # therefore unused.
    error_body = error.fp.read().decode()
    message = (
        f"EarthdataLogin error: {error_body},  statusCode: {status_code}, "
        f"statusMessage: {status_message}. Earthdata Login Request failed"
    )
    return Exception(message)


def is_token_expired(token: str):
    try:
        payload = jwt.decode(
            token["access_token"],
            options={
                "verify_signature": False,
                "verify_exp": True,
            },
        )
        return "exp" not in payload
    except jwt.ExpiredSignatureError:
        return True


def retrieve_edl_token(
    username: str,
    password: str,
    edl_env: str,
) -> Optional[str]:
    """Retrieve an existing valid token

    :param username: the username of the Earthdata Login user
    :param password: the password of the Earthdata Login user
    :param edl_env: the environment of the Earthdata Login (ex. 'SIT')
    :returns: Optional[str] - the token or undefined if there
    """
    try:
        url = f"{get_edl_url(edl_env)}/api/users/tokens"
        auth_handler = urllib.request.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm=None,
            uri=url,
            user=username,
            passwd=password,
        )
        opener = urllib.request.build_opener(auth_handler)
        raw_response = opener.open(url)
    except urllib.error.HTTPError as e:
        raise parse_http_error(e, "retrieve")
    except Exception as e:
        raise parse_caught_error(e)

    tokens = json.load(raw_response)
    unexpired_tokens = [
        token
        for token in tokens
        if "access_token" in token and not is_token_expired(token)
    ]
    sorted_tokens = sorted(
        unexpired_tokens,
        key=lambda token: jwt.decode(
            token["access_token"],
            options={"verify_signature": False},
        )["exp"],
    )
    if sorted_tokens:
        return sorted_tokens[-1]["access_token"]

    return None


def create_edl_token(
    username: str,
    password: str,
    edl_env: str,
) -> Optional[str]:
    """Create a token.

    :param username: the username of the Earthdata Login user
    :param password: the password of the Earthdata Login user
    :param edl_env: the environment of the Earthdata Login (ex. 'SIT')
    :returns: Optional[str] - the token or undefined
    """
    try:
        url = f"{get_edl_url(edl_env)}/api/users/tokens"
        auth_handler = urllib.request.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm=None,
            uri=url,
            user=username,
            passwd=password,
        )
        opener = urllib.request.build_opener(auth_handler)
        raw_response = opener.open(urllib.request.Request(url, method="POST"))
    except urllib.error.HTTPError as e:
        raise parse_http_error(e, "create")
    except Exception as e:
        raise parse_caught_error(e)

    response = json.load(raw_response)
    if response:
        return response[0]["access_token"]

    return None


def revoke_edl_token(
    username: str,
    password: str,
    edl_env: str,
    token: str,
) -> None:
    """Revoke a token

    :param username: the username of the Earthdata Login user
    :param password: the password of the Earthdata Login user
    :param edl_env: the environment of the Earthdata Login user (ex. 'SIT')
    :param token: the token to revoke
    :returns: None
    """
    try:
        url = f"{get_edl_url(edl_env)}/api/users/revoke_token"
        url_params = urllib.parse.urlencode({"token": token})
        full_url = f"{url}?{url_params}"

        auth_handler = urllib.request.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm=None,
            uri=url,
            user=username,
            passwd=password,
        )
        opener = urllib.request.build_opener(auth_handler)
        opener.open(
            urllib.request.Request(full_url, method="POST"),
        )
    except urllib.error.HTTPError as e:
        raise parse_http_error(e, "revoke")
    except Exception as e:
        raise parse_caught_error(e)


def get_edl_token(
    username: str,
    password: str,
    edl_env: str,
) -> Optional[str]:
    """Get a token by retrieving an existing token or creating a new one

    :param username: the username of the Earthdata Login user
    :param password: the password of the Earthdata Login user
    :param edl_env: the environment of the Earthdata Login (ex. 'SIT')
    :returns: Optional[str] - the JSON Web Token string or undefined
    """
    token = retrieve_edl_token(username, password, edl_env)
    if token is None:
        token = create_edl_token(username, password, edl_env)

    return token
