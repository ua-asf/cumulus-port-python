import os

import boto3
import pytest
from moto import mock_aws


@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def s3_client():
    with mock_aws():
        yield boto3.client("s3")


@pytest.fixture
def s3_resource():
    with mock_aws():
        yield boto3.resource("s3")


@pytest.fixture
def s3_bucket(s3_resource):
    bucket = s3_resource.Bucket("test-bucket")
    bucket.create()
    return bucket


@pytest.fixture
def buckets_config() -> dict:
    return {
        "browse": {
            "name": "stack-cumulus-dev-browse",
            "type": "public",
        },
        "private": {
            "name": "stack-cumulus-dev-private",
            "type": "private",
        },
        "protected": {
            "name": "stack-cumulus-dev-protected",
            "type": "protected",
        },
        "staging": {
            "name": "stack-cumulus-dev-staging",
            "type": "workflow",
        },
    }


@pytest.fixture
def collection() -> dict:
    return {
        "createdAt": 1711567923110,
        "updatedAt": 1728584062910,
        "name": "SAMPLE-COLLECTION",
        "version": "1",
        "process": "rtc",
        "url_path": "default/{granule.granuleId}/",
        "duplicateHandling": "replace",
        "granuleId": "^SAMPLE.*$",
        "granuleIdExtraction": "(SAMPLE.*)(\\.nc)",
        "files": [
            {
                "regex": "^SAMPLE_.*\\.(?:nc|iso\\.xml|)(?!png)(?:\\.md5)?$",
                "bucket": "protected",
                "sampleFileName": "SAMPLE_000000.nc",
                "url_path": "products/{granule.granuleId}/",
            },
            {
                "regex": "^SAMPLE_.*\\.(?!nc|iso\\.xml)(?:png)(?:\\.md5)?$",
                "bucket": "browse",
                "sampleFileName": "SAMPLE_000000.png",
            },
        ],
        "sampleFileName": "SAMPLE_000000.nc",
    }
