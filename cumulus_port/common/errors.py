# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/common/src/errors.ts

from typing import Any


def parse_caught_error(e: Any) -> Exception:
    """This method is for parsing a caught error which is not an HTTPerror in
    case the EDL endpoint call results in an unexpected error

    :param e: the Error, if e isn't of type Error then it returns itself
    :returns: Exception
    """
    if isinstance(e, Exception):
        return e

    return Exception(f"{e}")
