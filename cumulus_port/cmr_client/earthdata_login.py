# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/cmr-client/src/EarthdataLogin.ts

from typing import Optional

import jwt
import requests

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
    error: requests.exceptions.HTTPError,
    request_type: str,
) -> Exception:
    """Parse and handle error returned from EDL endpoint

    :param error: the HTTP error response returned by the EarthdataLogin
        endpoint
    :param request_type: the type of token request
        (options: 'retrieve', 'create', 'revoke')
    :returns: Exception - EarthdataLogin error
    """
    status_code = error.response.status_code
    status_message = error.response.reason or "Unknown"
    # In JavaScript the request_type is used to determine whether or not to
    # serialize the response body. In Python, the body is not deserialized for
    # us, so we know that we never need to serialize it again. request_type is
    # therefore unused.
    error_body = error.response.text
    message = (
        f"EarthdataLogin error: {error_body},  statusCode: {status_code}, "
        f"statusMessage: {status_message}. Earthdata Login Request failed"
    )
    return Exception(message)


def is_token_expired(token: dict) -> bool:
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
    :returns: Optional[str] - the token or None if there
    """
    try:
        url = f"{get_edl_url(edl_env)}/api/users/tokens"
        raw_response = requests.get(url, auth=(username, password))
    except requests.exceptions.HTTPError as e:
        raise parse_http_error(e, "retrieve")
    except Exception as e:
        raise parse_caught_error(e)

    tokens = raw_response.json()
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
        url = f"{get_edl_url(edl_env)}/api/users/token"
        raw_response = requests.post(url, auth=(username, password))
        raw_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise parse_http_error(e, "create")
    except Exception as e:
        raise parse_caught_error(e)

    response = raw_response.json()
    if response:
        return response["access_token"]

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
        response = requests.post(
            url,
            params={"token": token},
            auth=(username, password),
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
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
