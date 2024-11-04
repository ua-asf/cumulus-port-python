# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/errors/src/index.ts

class MissingRequiredEnvVarError(Exception):
    pass
