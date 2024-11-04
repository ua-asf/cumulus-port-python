# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/launchpad-auth/src/index.ts

import json
import logging
import time
from typing import Optional

import boto3

from cumulus_port.aws_client.s3 import s3_join, s3_object_exists

from .launchpad_token import LaunchpadToken
from .utils import get_env_var

log = logging.getLogger(__name__)


def launchpad_token_bucket_key() -> dict[str, str]:
    """Get S3 location of the Launchpad token

    :returns: dict - S3 Bucket and Key where Launchpad token is stored
    """
    bucket = get_env_var("system_bucket")
    stack_name = get_env_var("stackName")
    return {
        "Bucket": bucket,
        "Key": s3_join(stack_name, "launchpad/token.json"),
    }


def get_valid_launchpad_token_from_s3() -> Optional[str]:
    """Retrieve Launchpad token from S3

    :returns: Optional[str] - the Launchpad token, None if token doesn't exist
        or invalid
    """
    s3 = boto3.client("s3")
    s3location = launchpad_token_bucket_key()
    key_exists = s3_object_exists(s3, **s3location)

    token = None
    if key_exists:
        s3object = s3.get_object(**s3location)
        launchpad_token = json.load(s3object["Body"])
        now = time.time()
        token_expiration_in_sec = (
            launchpad_token["session_maxtimeout"]
            + launchpad_token["session_starttime"]
        )

        # check if token is still valid
        if now < token_expiration_in_sec:
            token = launchpad_token["sm_token"]

    return token


def get_launchpad_token(*, api: str, passphrase: str, certificate: str) -> str:
    """Get a Launchpad token

    :param api: the Launchpad token service api endpoint
    :param passphrase: the passphrase of the Launchpad PKI certificate
    :param certificate: the name of the Launchpad PKI pfx certificate
    :returns: str - the Launchpad token
    """
    token = get_valid_launchpad_token_from_s3()

    if not token:
        log.debug("getLaunchpadToken requesting launchpad token")
        launchpad = LaunchpadToken(
            api=api,
            passphrase=passphrase,
            certificate=certificate,
        )
        token_response = launchpad.request_token()
        # add session_starttime to token object, assume token is generated 5 min ago
        token_object = {
            **token_response,
            "session_starttime": int(time.time()) - (5 * 60),
        }

        s3location = launchpad_token_bucket_key()
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=s3location["Bucket"],
            Key=s3location["Key"],
            Body=json.dumps(token_object),
        )

        token = token_object["sm_token"]

    return token
