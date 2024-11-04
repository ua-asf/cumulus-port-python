import json
import time

from moto import mock_aws

from cumulus_port.launchpad_auth import (
    get_launchpad_token,
    get_valid_launchpad_token_from_s3,
    launchpad_token_bucket_key,
)


def test_launchpad_token_bucket_key(s3_bucket, monkeypatch):
    monkeypatch.setenv("system_bucket", s3_bucket.name)
    monkeypatch.setenv("stackName", "test-stack")
    assert launchpad_token_bucket_key() == {
        "Bucket": "test-bucket",
        "Key": "test-stack/launchpad/token.json",
    }


def test_get_valid_launchpad_token_from_s3(s3_bucket, monkeypatch):
    obj = s3_bucket.Object("test-stack/launchpad/token.json")
    obj.put(
        Body=json.dumps({
            "session_maxtimeout": 5000,
            "session_starttime": int(time.time()),
            "sm_token": "the-token",
        }),
    )

    monkeypatch.setenv("system_bucket", s3_bucket.name)
    monkeypatch.setenv("stackName", "test-stack")
    assert get_valid_launchpad_token_from_s3() == "the-token"


@mock_aws
def test_get_launchpad_token(s3_bucket, mocker, monkeypatch):
    mocker.patch(
        "cumulus_port.launchpad_auth.LaunchpadToken.request_token",
        return_value={
            "sm_token": "the-token",
        },
    )
    monkeypatch.setenv("system_bucket", s3_bucket.name)
    monkeypatch.setenv("stackName", "test-stack")
    assert get_launchpad_token(
        api="foo",
        passphrase="foo",
        certificate="foo",
    ) == "the-token"
