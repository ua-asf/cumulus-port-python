import boto3
from moto import mock_aws

from cumulus_port.aws_client.secrets_manager import get_secret_string


@mock_aws
def test_get_secret_string():
    client = boto3.client("secretsmanager")
    client.create_secret(
        Name="test-secret",
        SecretString="The secret value",
    )

    assert get_secret_string("test-secret") == "The secret value"
    assert get_secret_string("does-not-exist") is None
