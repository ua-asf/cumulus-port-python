import pytest

try:
    from cumulus_port.cmr_client.earthdata_login import get_edl_token, get_edl_url
except ImportError:
    pass


pytestmark = pytest.mark.auth


def test_get_edl_url():
    assert get_edl_url("PROD") == "https://urs.earthdata.nasa.gov"
    assert get_edl_url("UAT") == "https://uat.urs.earthdata.nasa.gov"
    assert get_edl_url("SIT") == "https://sit.urs.earthdata.nasa.gov"


def test_get_edl_token(mocker):
    mock_retrieve_edl_token = mocker.patch(
        "cumulus_port.cmr_client.earthdata_login.retrieve_edl_token",
        return_value=None,
    )
    mocker.patch(
        "cumulus_port.cmr_client.earthdata_login.create_edl_token",
        return_value="the-new-token",
    )
    assert get_edl_token("username", "password", "UAT") == "the-new-token"

    mock_retrieve_edl_token.return_value = "old-token"
    assert get_edl_token("username", "password", "UAT") == "old-token"
