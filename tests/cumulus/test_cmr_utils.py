from cumulus_port.cmrjs.cmr_utils import get_cmr_settings


def test_get_cmr_settings_launchpad(mocker):
    cmr = {
        "clientId": "unit-test-client-id",
        "cmrEnvironment": "UAT",
        "cmrLimit": 100,
        "cmrPageSize": 50,
        "oauthProvider": "launchpad",
        "passwordSecretName": "cmr-password-secret-name",
        "provider": "ASFDEV",
        "username": "username",
    }
    launchpad = {
        "api": "https://api.launchpad.nasa.gov/icam/api/sm/v1",
        "certificate": "Modify-012345678.pfx",
        "passphraseSecretName": "launchpad-passphrase-secret-name",
    }
    mocker.patch(
        "cumulus_port.cmrjs.cmr_utils.launchpad.get_launchpad_token",
        return_value="the-launchpad-token",
    )

    assert get_cmr_settings({**cmr, **launchpad}) == {
        "client_id": "unit-test-client-id",
        "oauth_provider": "launchpad",
        "provider": "ASFDEV",
        "token": "the-launchpad-token",
    }


def test_get_cmr_settings_earthdata(mocker):
    cmr = {
        "clientId": "unit-test-client-id",
        "cmrEnvironment": "UAT",
        "cmrLimit": 100,
        "cmrPageSize": 50,
        "oauthProvider": "earthdata",
        "passwordSecretName": "cmr-password-secret-name",
        "provider": "ASFDEV",
        "username": "username",
    }
    mocker.patch(
        "cumulus_port.cmrjs.cmr_utils.get_secret_string",
        return_value="password",
    )

    assert get_cmr_settings(cmr) == {
        "provider": "ASFDEV",
        "client_id": "unit-test-client-id",
        "oauth_provider": "earthdata",
        "password": "password",
        "username": "username",
    }
