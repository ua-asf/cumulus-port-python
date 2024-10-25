# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/aws-client/src/SecretsManager.ts

import boto3


def get_secret_string(secret_id: str) -> str:
    secrets_manager = boto3.client("secretsmanager")
    return secrets_manager.get_secret_value(SecretId=secret_id)["SecretString"]
