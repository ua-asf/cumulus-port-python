# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/aws-client/src/SecretsManager.ts

import contextlib
from typing import Optional

import boto3


def get_secret_string(secret_id: str) -> Optional[str]:
    secrets_manager = boto3.client("secretsmanager")
    with contextlib.suppress(Exception):
        response = secrets_manager.get_secret_value(SecretId=secret_id)
        return response["SecretString"]

    return None
