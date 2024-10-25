import pytest
from moto import mock_aws

try:
    import boto3

    from cumulus_port.cmr_client import CMR
    from cumulus_port.cmr_client.cmr import update_token
    from cumulus_port.errors import MissingRequiredEnvVarError
except ImportError:
    pass

pytestmark = pytest.mark.auth


@pytest.fixture
def cmr_password_secret_name():
    secret_name = "test_cmr_passwrd"
    with mock_aws():
        client = boto3.client("secretsmanager")
        client.create_secret(
            Name=secret_name,
            SecretString="password",
        )
        yield secret_name


def test_update_token(monkeypatch, mocker):
    with pytest.raises(MissingRequiredEnvVarError):
        update_token("username", "password")

    monkeypatch.setenv("CMR_ENVIRONMENT", "")
    with pytest.raises(Exception, match="CMR_ENVIRONMENT not set"):
        update_token("username", "password")

    monkeypatch.setenv("CMR_ENVIRONMENT", "UAT")
    mocker.patch(
        "cumulus_port.cmr_client.cmr.get_edl_token",
        return_value="edl-token",
    )

    assert update_token("username", "password") == "edl-token"


def test_get_cmr_password(cmr_password_secret_name):
    kwargs = {
        "provider": "TEST",
        "client_id": "unit-tests",
        "oauth_provider": "earthdata",
    }
    assert CMR(password="foobar", **kwargs).get_cmr_password() == "foobar"
    assert CMR(
        password_secret_name=cmr_password_secret_name,
        **kwargs,
    ).get_cmr_password() == "password"

    with pytest.raises(Exception, match="No CMR password set"):
        CMR(**kwargs).get_cmr_password()

    with pytest.raises(Exception, match="Unable to retrieve CMR password"):
        CMR(
            password_secret_name="does-not-exist",
            **kwargs,
        ).get_cmr_password()


def test_get_token(mocker):
    kwargs = {
        "provider": "TEST",
        "client_id": "unit-tests",
        "oauth_provider": "earthdata",
    }
    assert CMR(token="the-token", **kwargs).get_token() == "the-token"

    mock_update_token = mocker.patch(
        "cumulus_port.cmr_client.cmr.update_token",
        return_value="the-new-token",
    )
    assert CMR(
        username="username",
        password="password",
        **kwargs,
    ).get_token() == "the-new-token"
    mock_update_token.assert_called_once_with("username", "password")


def test_get_read_headers():
    cmr_client = CMR(
        provider="TEST",
        client_id="unit-test-client-id",
        oauth_provider="earthdata",
    )
    assert cmr_client.get_read_headers() == {
        "Client-Id": "unit-test-client-id",
    }
    assert cmr_client.get_read_headers(token="the-token") == {
        "Client-Id": "unit-test-client-id",
        "Authorization": "the-token",
    }


def test_search_concept(mocker):
    cmr_client = CMR(
        provider="TEST",
        client_id="unit-test-client-id",
        oauth_provider="earthdata",
        token="the-token",
    )
    mock_search_concept = mocker.patch(
        "cumulus_port.cmr_client.cmr.search_concept",
        return_value=[{"foo": "bar"}],
    )

    assert cmr_client.search_concept("some-type", {"a": "b"}) == [
        {"foo": "bar"},
    ]
    mock_search_concept.assert_called_once_with(
        type="some-type",
        search_params={"a": "b"},
        previous_results=[],
        headers={
            "Client-Id": "unit-test-client-id",
            "Authorization": "the-token",
        },
        format="json",
        recursive=True,
    )


def test_search_collections(mocker):
    cmr_client = CMR(
        provider="TEST",
        client_id="unit-test-client-id",
        oauth_provider="earthdata",
        token="the-token",
    )
    mock_search_concept = mocker.patch(
        "cumulus_port.cmr_client.cmr.search_concept",
        return_value=[{"foo": "bar"}],
    )

    assert cmr_client.search_collections({"a": "b"}, "umm_json") == [
        {"foo": "bar"},
    ]
    mock_search_concept.assert_called_once_with(
        type="collections",
        search_params={
            "provider_short_name": "TEST",
            "a": "b",
        },
        previous_results=[],
        headers={
            "Client-Id": "unit-test-client-id",
            "Authorization": "the-token",
        },
        format="umm_json",
        recursive=True,
    )


def test_search_granules(mocker):
    cmr_client = CMR(
        provider="TEST",
        client_id="unit-test-client-id",
        oauth_provider="earthdata",
        token="the-token",
    )
    mock_search_concept = mocker.patch(
        "cumulus_port.cmr_client.cmr.search_concept",
        return_value=[{"foo": "bar"}],
    )

    assert cmr_client.search_granules({"a": "b"}, "umm_json") == [
        {"foo": "bar"},
    ]
    mock_search_concept.assert_called_once_with(
        type="granules",
        search_params={
            "provider_short_name": "TEST",
            "a": "b",
        },
        previous_results=[],
        headers={
            "Client-Id": "unit-test-client-id",
            "Authorization": "the-token",
        },
        format="umm_json",
        recursive=True,
    )
