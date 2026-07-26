import socket
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

LOOPBACK = frozenset({"127.0.0.1", "::1", "localhost", ""})

OFFLINE_ENV = {
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
    "HF_DATASETS_OFFLINE": "1",
    "DIFFUSERS_OFFLINE": "1",
}


class OutboundBlocked(RuntimeError):
    pass


def _host_of(address: Any) -> str:
    if isinstance(address, tuple) and address:
        return str(address[0])
    return ""


@contextmanager
def block_outbound() -> Iterator[list[str]]:
    attempts: list[str] = []
    real_connect = socket.socket.connect
    real_create = socket.create_connection

    def guarded_connect(self: socket.socket, address: Any) -> Any:
        host = _host_of(address)
        if host not in LOOPBACK:
            attempts.append(host)
            raise OutboundBlocked(f"outbound connection attempted to {host}")
        return real_connect(self, address)

    def guarded_create(address: Any, *args: Any, **kwargs: Any) -> Any:
        host = _host_of(address)
        if host not in LOOPBACK:
            attempts.append(host)
            raise OutboundBlocked(f"outbound connection attempted to {host}")
        return real_create(address, *args, **kwargs)

    socket.socket.connect = guarded_connect  # type: ignore[method-assign,assignment]
    socket.create_connection = guarded_create
    try:
        yield attempts
    finally:
        socket.socket.connect = real_connect  # type: ignore[method-assign]
        socket.create_connection = real_create
