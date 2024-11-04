# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/cmr-client/src/searchConcept.ts

import logging
import os
from typing import Optional

import requests

from .get_url import get_search_url

log = logging.getLogger(__name__)


def search_concept(
    *,
    type: str,
    search_params: dict,
    previous_results: list = [],
    headers: dict = {},
    format: str = "json",
    recursive: bool = True,
    cmr_environment: Optional[str] = os.getenv("CMR_ENVIRONMENT"),
    cmr_limit: Optional[int] = None,
    cmr_page_size: Optional[int] = None,
) -> list:
    """
    :param type: Concept type to search, choices: ['collections', 'granules']
    :param cmr_environment: - optional, CMR environment to use valid arguments
        are ['PROD', 'OPS', 'SIT', 'UAT']
    :param search_params: CMR search parameters
        Note initial searchParams.page_num should only be set if recursive is false
    :param previous_results: array of results returned in previous recursive
        calls to be included in the results returned
    :param headers: the CMR headers
    :param format: format of the response, supports umm_json, json, echo10
    :param recursive: indicate whether search recursively to get all the result
    :param cmr_limit: the CMR limit
    :param cmr_page_size: the CMR page size
    :returns: array of search results.
    """
    if cmr_limit is not None:
        records_limit = cmr_limit
    elif (env_cmr_limit := os.getenv("CMR_LIMIT")):
        records_limit = int(env_cmr_limit)
    else:
        records_limit = 100

    search_params_page_size = search_params.get("pageSize")

    if search_params_page_size:
        page_size = int(search_params_page_size)
    elif cmr_page_size is not None:
        page_size = cmr_page_size
    elif (env_cmr_page_size := os.getenv("CMR_PAGE_SIZE")):
        page_size = int(env_cmr_page_size)
    else:
        page_size = 50

    query = dict(search_params)

    query_page_num = query.get("page_num")
    page_num = 1 if query_page_num is None else int(query_page_num) + 1

    query["page_num"] = page_num

    if "page_size" not in query:
        query["page_size"] = str(page_size)

    url = f"{get_search_url(cmr_env=cmr_environment)}{type}.{format.lower()}"
    try:
        response = requests.get(url, params=query, headers=headers)
        response.raise_for_status()
    except Exception:
        log.error(
            "Error executing CMR search concept.\nSearching %s\n"
            "with search parameters %s\nand headers %s",
            url,
            query,
            headers,
        )
        raise

    if format == "echo10":
        raise NotImplementedError()
    else:
        body = response.json()
        if "items" in body:
            response_items = body["items"]
        else:
            response_items = body.get("feed", {}).get("entry", [])

    fetched_results = previous_results + (response_items or [])

    num_records_collected = len(fetched_results)

    cmr_hits = response.headers.get("cmr-hits")
    if cmr_hits is None:
        raise TypeError("cmr-hits header not found")

    cmr_has_more_results = int(cmr_hits) > num_records_collected
    records_limit_reached = num_records_collected >= records_limit
    if recursive and cmr_has_more_results and not records_limit_reached:
        return search_concept(
            type=type,
            search_params=query,
            previous_results=fetched_results,
            headers=headers,
            format=format,
            recursive=recursive,
        )

    return fetched_results[:records_limit]
