# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/common/src/env.ts

import os

from cumulus_port.errors import MissingRequiredEnvVarError


def get_required_env_var(
    name: str,
    env: dict = os.environ,
) -> str:
    value = env.get(name)

    if value is not None:
        return value

    raise MissingRequiredEnvVarError(
        f"The {name} environment variable must be set",
    )
