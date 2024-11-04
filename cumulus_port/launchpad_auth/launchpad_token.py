# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/launchpad-auth/src/LaunchpadToken.ts

import logging
import urllib.parse

import boto3
import requests

from cumulus_port._internal.pfx_to_pem import pfx_to_pem
from cumulus_port.aws_client.s3 import s3_object_exists

from .utils import get_env_var

log = logging.getLogger(__name__)


class LaunchpadToken:
    """A class for sending requests to Launchpad token service endpoints

    Example:
    >>> launchpad_token = LaunchpadToken(
    ...     api="launchpad-token-api-endpoint",
    ...     passphrase="my-pki-passphrase",
    ...     certificate="my-pki-certificate.pfx",
    ... )
    ...
    """

    def __init__(self, *, api: str, passphrase: str, certificate: str):
        """
        :param api: the Launchpad token service api endpoint
        :param passphrase: the passphrase of the Launchpad PKI certificate
        :param certificate: the name of the Launchpad PKI pfx certificate
        """
        self.api = api
        self.passphrase = passphrase
        self.certificate = certificate

    def retrieve_certificate(self) -> bytes:
        """Retrieve Launchpad credentials

        :returns: Optional[bytes] - body of certificate found on S3
        """
        bucket = get_env_var("system_bucket")
        stack_name = get_env_var("stackName")

        # we are assuming that the specified certificate file is in the S3
        # crypto directory
        crypt_key = f"{stack_name}/crypto/{self.certificate}"

        s3 = boto3.client("s3")
        key_exists = s3_object_exists(
            s3,
            Bucket=bucket,
            Key=crypt_key,
        )

        if not key_exists:
            raise Exception(
                f"{self.certificate} does not exist in S3 {bucket} crypto "
                f"directory: {crypt_key}",
            )

        log.debug(
            "Reading Key: %s bucket:%s,stack:%s",
            self.certificate,
            bucket,
            stack_name,
        )

        pfx_object = s3.get_object(
            Bucket=bucket,
            Key=crypt_key,
        )
        return pfx_object["Body"].read()

    def request_token(self) -> dict:
        """Get a token from Launchpad

        :returns: dict - the Launchpad gettoken response object
        """
        log.debug("LaunchpadToken.requestToken")
        pfx = self.retrieve_certificate()

        with pfx_to_pem(pfx, self.passphrase) as cert:
            url = urllib.parse.urljoin(f"{self.api}/", "gettoken")
            response = requests.get(url, cert=cert)
            response.raise_for_status()
            return response.json()

    def validate_token(self, token: str) -> dict:
        """Validate a Launchpad token

        :param token: the Launchpad token for validation
        :returns: dict - the Launchpad validate token response object
        """
        log.debug("LaunchpadToken.validateToken")
        pfx = self.retrieve_certificate()

        with pfx_to_pem(pfx, self.passphrase) as cert:
            url = urllib.parse.urljoin(f"{self.api}/", "validate")
            response = requests.post(
                url,
                json={"token": token},
                cert=cert,
            )
            response.raise_for_status()
            return response.json()
