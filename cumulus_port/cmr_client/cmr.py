# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/cmr-client/src/CMR.ts#L8

from typing import Optional

from cumulus_port.aws_client import secrets_manager as secrets_manager_utils
from cumulus_port.common.env import get_required_env_var

from .earthdata_login import get_edl_token
from .search_concept import search_concept


def update_token(
    username: str,
    password: str,
) -> Optional[str]:
    """Returns a valid a CMR token

    :param username: CMR username
    :param password: CMR password
    :returns: the token
    """
    edl_env = get_required_env_var("CMR_ENVIRONMENT")
    if not edl_env:
        raise Exception("CMR_ENVIRONMENT not set")
    return get_edl_token(username, password, edl_env)


class CMR:
    """A class to simplify requests to the CMR

    Example:
    >>> cmr_client = CMR(
    ...     provider="my-provider",
    ...     client_id="my-clientId",
    ...     username="my-username",
    ...     password="my-password",
    ... )
    ...

    or

    >>> cmr_client = CMR(
    ...     provider="my-provider",
    ...     client_id="my-clientId",
    ...     token="cmr_or_launchpad_token",
    ... )
    ...
    """
    def __init__(
        self,
        *,
        provider: str,
        client_id: str,
        username: Optional[str] = None,
        password_secret_name: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        oauth_provider: str,
    ):
        """The constructor for the CMR class

        :param provider: the CMR provider id
        :param client_id: the CMR clientId
        :param username: CMR username, not used if token is provided
        :param password_secret_name: CMR password secret, not used if token is provided
        :param password: CMR password, not used if token or passwordSecretName
            is provided
        :param token: CMR or Launchpad token, if not provided, CMR username and
            password are used to get a cmr token
         :param oauth_provider: Oauth provider: 'earthdata' or 'launchpad'
        """
        self.provider = provider
        self.client_id = client_id
        self.username = username
        self.oauth_provider = oauth_provider
        self.password_secret_name = password_secret_name
        self.password = password
        self.token = token

    def get_cmr_password(self) -> str:
        """Get the CMR password, from the AWS secret if set, else return the
        password

        :returns: the CMR password
        """
        if self.password_secret_name:
            value = secrets_manager_utils.get_secret_string(
                self.password_secret_name,
            )

            if not value:
                raise Exception("Unable to retrieve CMR password")

            return value

        if not self.password:
            raise Exception("No CMR password set")

        return self.password

    def get_token(self) -> Optional[str]:
        """The method for getting the token

        :returns: the token
        """
        if self.token:
            return self.token

        return update_token(self.username, self.get_cmr_password())

    def get_write_headers(
        self,
        *,
        token: Optional[str] = None,
        ummg_version: Optional[str] = None,
        cmr_revision_id: Optional[str] = None,
    ) -> dict:
        """Return object containing CMR request headers for PUT / POST / DELETE

        :param token: CMR request token
        :param ummg_version: UMMG metadata version string or null if echo10
            metadata
        :param cmr_revision_id: CMR Revision ID
        :returns: CMR headers object
        """
        raise NotImplementedError()

    def get_read_headers(self, *, token: Optional[str] = None) -> dict:
        """Return object containing CMR request headers for GETs

        :param token: CMR request token
        :returns: CMR headers object
        """
        headers = {
            "Client-Id": self.client_id,
        }

        if token:
            headers["Authorization"] = token

        return headers

    def ingest_collection(self, xml: str):
        """Adds a collection record to the CMR

        :param xml: the collection XML document
        :returns: the CMR response
        """
        raise NotImplementedError()

    def ingest_granule(self, xml: str, cmr_revision_id: Optional[str] = None):
        """Adds a granule record to the CMR

        :param xml: the granule XML document
        :param cmr_revision_id: Optional CMR Revision ID
        :returns: the CMR response
        """
        raise NotImplementedError()

    def ingest_umm_granule(
        self,
        ummg_metadata: dict,
        cmr_revision_id: Optional[str] = None,
    ) -> dict:
        """Adds/Updates UMMG json metadata in the CMR

        :param ummg_metadata: UMMG metadata object
        :param cmr_revision_id: Optional CMR Revision ID
        :returns: the CMR response object.
        """
        raise NotImplementedError()

    def delete_collection(self, dataset_id: str):
        """Deletes a collection record from the CMR

        :param dataset_id: the collection unique id
        :returns: the CMR response
        """
        raise NotImplementedError()

    def delete_granule(self, granule_ur: str):
        """Deletes a granule record from the CMR

        :param granule_ur: the granule unique id
        :returns: the CMR response
        """
        raise NotImplementedError()

    def search_concept(
        self,
        type: str,
        search_params: dict[str, str],
        format: str = "json",
        recursive: bool = True,
    ) -> list:
        headers = self.get_read_headers(token=self.get_token())
        return search_concept(
            type=type,
            search_params=search_params,
            previous_results=[],
            headers=headers,
            format=format,
            recursive=recursive,
        )

    def search_collections(
        self,
        params: dict[str, str] = {},
        format: str = "json",
    ) -> list:
        """Search in collections

        :param params: the search parameters
        :param format: format of the response
        :returns: the CMR response
        """
        search_params = {
            "provider_short_name": self.provider,
            **params,
        }
        return self.search_concept(
            "collections",
            search_params,
            format,
        )

    def search_granules(
        self,
        params: dict[str, str] = {},
        format: str = "json",
    ) -> list:
        """Search in granules

        :param params: the search parameters
        :param format: format of the response
        :returns: the CMR response
        """
        search_params = {
            "provider_short_name": self.provider,
            **params,
        }
        return self.search_concept(
            "granules",
            search_params,
            format,
        )

    def get_granule_metadata(self, cmr_link: str):
        """Get the granule metadata from CMR using the cmr_link

        :param cmr_link: URL to concept
        :returns: metadata as a JS object, null if not found
        """
        raise NotImplementedError()
