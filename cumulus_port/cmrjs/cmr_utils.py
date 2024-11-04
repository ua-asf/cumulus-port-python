# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/cmrjs/src/cmr-utils.js

import logging
import os

from cumulus_port import launchpad_auth as launchpad
from cumulus_port.aws_client.secrets_manager import get_secret_string

log = logging.getLogger(__name__)


def get_cmr_settings(cmr_config: dict = {}) -> dict:
    """Helper to build an CMR settings object, used to initialize CMR.

    :param cmr_config: CMR configuration object
        key "oauthProvider" - Oauth provider: launchpad or earthdata
        key "provider" - the CMR provider
        key "clientId" - Client id for CMR requests
        key "passphraseSecretName" - Launchpad passphrase secret name
        key "api" - Launchpad api
        key "certificate" - Launchpad certificate
        key "username" - EDL username
        key "passwordSecretName" - CMR password secret name
    :returns: dict - object to create CMR instance - contains the provider,
        clientId, and either launchpad token or EDL username and password
    """
    oauth_provider = (
        cmr_config.get("oauthProvider") or os.getenv("cmr_oauth_provider")
    )

    cmr_credentials = {
        "provider": cmr_config.get("provider") or os.getenv("cmr_provider"),
        "client_id": cmr_config.get("clientId") or os.getenv("cmr_client_id"),
        "oauth_provider": oauth_provider,
    }

    if oauth_provider == "launchpad":
        launchpad_passphrase_secret_name = (
            cmr_config.get("passphraseSecretName")
            or os.getenv("launchpad_passphrase_secret_name")
        )
        passphrase = get_secret_string(launchpad_passphrase_secret_name)

        config = {
            "passphrase": passphrase,
            "api": cmr_config.get("api") or os.getenv("launchpad_api"),
            "certificate": (
                cmr_config.get("certificate")
                or os.getenv("launchpad_certificate")
            ),
        }

        log.debug("cmrjs.getCreds getLaunchpadToken")
        token = launchpad.get_launchpad_token(**config)
        return {
            **cmr_credentials,
            "token": token,
        }

    password_secret_name = (
        cmr_config.get("passwordSecretName")
        or os.getenv("cmr_password_secret_name")
    )
    password = get_secret_string(password_secret_name)

    return {
        **cmr_credentials,
        "password": password,
        "username": cmr_config.get("username") or os.getenv("cmr_username"),
    }
