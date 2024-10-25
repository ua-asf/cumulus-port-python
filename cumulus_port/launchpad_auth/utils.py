# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/launchpad-auth/src/utils.ts

import os


def get_env_var(name: str) -> str:
    env_var = os.getenv(name)
    if not env_var:
        raise Exception(f"Must set environment variable {name}")

    return env_var
