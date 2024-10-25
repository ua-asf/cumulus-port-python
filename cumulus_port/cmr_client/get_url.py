# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/cmr-client/src/getUrl.ts

import os
from typing import Optional


def get_cmr_host(
    *,
    cmr_environment: Optional[str] = os.getenv("CMR_ENVIRONMENT"),
    cmr_host: Optional[str] = os.getenv("CMR_HOST"),
) -> str:
    """Get host to use for CMR requests.

    :param cmr_environment: CMR environment logical name to use for requests.
    :param cmr_host: Custom host name to use for CMR requests.
    :returns: str
    """
    if cmr_host:
        return cmr_host

    if cmr_environment in ("PROD", "OPS"):
        return "https://cmr.earthdata.nasa.gov"
    if cmr_environment == "UAT":
        return "https://cmr.uat.earthdata.nasa.gov"
    if cmr_environment == "SIT":
        return "https://cmr.sit.earthdata.nasa.gov"

    raise TypeError(f"Invalid CMR environment: {cmr_environment}")


def get_bucket_access_url(
    *,
    host: Optional[str] = os.getenv("CMR_HOST"),
    cmr_env: Optional[str] = os.getenv("CMR_ENVIRONMENT"),
) -> str:
    base_url = get_cmr_host(cmr_environment=cmr_env, cmr_host=host)
    return f"{base_url}/access-control/s3-buckets/"


def get_ingest_url(
    *,
    host: Optional[str] = os.getenv("CMR_HOST"),
    cmr_env: Optional[str] = os.getenv("CMR_ENVIRONMENT"),
    provider: str,
) -> str:
    base_url = get_cmr_host(cmr_environment=cmr_env, cmr_host=host)
    return f"{base_url}/ingest/providers/{provider}/"


def get_search_url(
    *,
    host: Optional[str] = os.getenv("CMR_HOST"),
    cmr_env: Optional[str] = os.getenv("CMR_ENVIRONMENT"),
) -> str:
    base_url = get_cmr_host(cmr_environment=cmr_env, cmr_host=host)
    return f"{base_url}/search/"


def get_token_url(
    *,
    host: Optional[str] = os.getenv("CMR_HOST"),
    cmr_env: Optional[str] = os.getenv("CMR_ENVIRONMENT"),
) -> str:
    base_url = get_cmr_host(cmr_environment=cmr_env, cmr_host=host)
    return f"{base_url}/legacy-services/rest/tokens"


def get_validate_url(
    *,
    host: Optional[str] = os.getenv("CMR_HOST"),
    cmr_env: Optional[str] = os.getenv("CMR_ENVIRONMENT"),
    provider: str,
) -> str:
    base_url = get_cmr_host(cmr_environment=cmr_env, cmr_host=host)
    return f"{base_url}/ingest/providers/{provider}/validate/"
