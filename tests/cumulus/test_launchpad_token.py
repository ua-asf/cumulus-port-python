import pytest

from cumulus_port.launchpad_auth.launchpad_token import LaunchpadToken


def test_retrieve_certificate(s3_bucket, monkeypatch):
    monkeypatch.setenv("system_bucket", s3_bucket.name)
    monkeypatch.setenv("stackName", "test-stack")

    launchpad = LaunchpadToken(
        api="foo",
        passphrase="foo",
        certificate="Modify.pfx",
    )
    with pytest.raises(Exception, match="Modify.pfx does not exist in S3"):
        launchpad.retrieve_certificate()

    obj = s3_bucket.Object("test-stack/crypto/Modify.pfx")
    obj.put(Body="CERTIFICATE")

    assert launchpad.retrieve_certificate() == b"CERTIFICATE"
