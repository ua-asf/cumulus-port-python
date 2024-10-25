import pytest

try:
    from cumulus_port.cmr_client.get_url import (
        get_bucket_access_url,
        get_cmr_host,
        get_ingest_url,
        get_search_url,
        get_token_url,
        get_validate_url,
    )
except ImportError:
    pass


pytestmark = pytest.mark.auth


def test_get_cmr_host():
    assert get_cmr_host(
        cmr_environment="PROD",
        cmr_host=None,
    ) == "https://cmr.earthdata.nasa.gov"
    assert get_cmr_host(
        cmr_environment="UAT",
        cmr_host=None,
    ) == "https://cmr.uat.earthdata.nasa.gov"
    assert get_cmr_host(
        cmr_environment="SIT",
        cmr_host=None,
    ) == "https://cmr.sit.earthdata.nasa.gov"

    assert get_cmr_host(
        cmr_environment="FOO",
        cmr_host="https://foo.bar",
    ) == "https://foo.bar"

    with pytest.raises(TypeError, match="Invalid CMR environment: FOO"):
        assert get_cmr_host(cmr_environment="FOO", cmr_host=None)


def test_get_bucket_access_url():
    assert get_bucket_access_url(
        host=None,
        cmr_env="PROD",
    ) == "https://cmr.earthdata.nasa.gov/access-control/s3-buckets/"


def test_get_ingest_url():
    assert get_ingest_url(
        host=None,
        cmr_env="PROD",
        provider="ASFDEV",
    ) == "https://cmr.earthdata.nasa.gov/ingest/providers/ASFDEV/"


def test_get_search_url():
    assert get_search_url(
        host=None,
        cmr_env="PROD",
    ) == "https://cmr.earthdata.nasa.gov/search/"


def test_get_token_url():
    assert get_token_url(
        host=None,
        cmr_env="PROD",
    ) == "https://cmr.earthdata.nasa.gov/legacy-services/rest/tokens"


def test_get_validate_url():
    assert get_validate_url(
        host=None,
        cmr_env="PROD",
        provider="ASFDEV",
    ) == "https://cmr.earthdata.nasa.gov/ingest/providers/ASFDEV/validate/"
