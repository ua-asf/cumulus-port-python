# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/aws-client/src/S3.ts

import re
from typing import Union

import boto3
import botocore


def s3_join(*args: Union[str, list[str]]) -> str:
    """Join strings into an S3 key without a leading slash

    :param args: - the strings to join
    :returns: str - the full S3 key
    """
    if not args:
        return ""

    tokens: list[str]
    if isinstance(args[0], str):
        tokens = args
    else:
        tokens = args[0]

    # The regexes have been combined into one to make the list comprehension
    # below simpler.
    def remove_slashes(token: str) -> str:
        return re.sub(r"^/|/$", "", token)

    key = "/".join([
        stripped_token
        for token in tokens
        if (stripped_token := remove_slashes(token))
    ])

    if tokens[-1].endswith("/"):
        return f"{key}/"
    return key


def s3_object_exists(s3: boto3.client, **kwargs) -> bool:
    """Test if an object exists in S3

    :param kwargs: same params as
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/head_object.html
    :returns: bool - a Promise that will resolve to a boolean indicating if the
        object exists
    """
    try:
        s3.head_object(**kwargs)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Message"] == "Not Found":
            return False
        raise

    return True
