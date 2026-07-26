import socket
import threading

import pytest

from rivet.telemetry.network_guard import OFFLINE_ENV, OutboundBlocked, block_outbound


def test_outbound_connection_is_blocked_and_recorded() -> None:
    with block_outbound() as attempts, pytest.raises(OutboundBlocked):
        socket.create_connection(("huggingface.co", 443), timeout=1)
    assert attempts == ["huggingface.co"]


def test_socket_connect_is_blocked() -> None:
    with block_outbound():
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with pytest.raises(OutboundBlocked):
            probe.connect(("1.1.1.1", 80))
        probe.close()


def test_loopback_still_works() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    threading.Thread(target=lambda: server.accept(), daemon=True).start()
    with block_outbound() as attempts:
        client = socket.create_connection(("127.0.0.1", port), timeout=2)
        client.close()
    assert attempts == []
    server.close()


def test_guard_restores_the_real_socket_api() -> None:
    original_connect = socket.socket.connect
    original_create = socket.create_connection
    with block_outbound():
        assert socket.socket.connect is not original_connect
    assert socket.socket.connect is original_connect
    assert socket.create_connection is original_create


def test_offline_env_covers_the_model_hubs() -> None:
    assert OFFLINE_ENV["HF_HUB_OFFLINE"] == "1"
    assert "TRANSFORMERS_OFFLINE" in OFFLINE_ENV
    assert "DIFFUSERS_OFFLINE" in OFFLINE_ENV
