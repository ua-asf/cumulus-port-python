from contextlib import contextmanager
from tempfile import NamedTemporaryFile

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)


@contextmanager
def pfx_to_pem(pfx: bytes, pfx_password: str):
    """Decrypts the .pfx file and writes to a termporary location as a .pem"""
    private_key, main_cert, add_certs = load_key_and_certificates(
        pfx,
        pfx_password.encode(),
        None,
    )

    if private_key is None:
        raise Exception("pfx missing private key")

    if main_cert is None:
        raise Exception("pfx missing certificate")

    with NamedTemporaryFile(suffix=".pem") as t_pem:
        with open(t_pem.name, "wb") as pem_file:
            pem_file.write(
                private_key.private_bytes(
                    Encoding.PEM,
                    PrivateFormat.PKCS8,
                    NoEncryption(),
                ),
            )
            pem_file.write(main_cert.public_bytes(Encoding.PEM))
            for ca in add_certs:
                pem_file.write(ca.public_bytes(Encoding.PEM))
        yield t_pem.name
