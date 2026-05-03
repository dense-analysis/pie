import socket
from collections.abc import Generator
from typing import Any, NoReturn

import pytest


@pytest.fixture(autouse=True)
def no_network(request: Any) -> Generator[None]:
    """
    Disable outgoing network access unless test opts in.
    """
    if request.node.get_closest_marker("allow_network"):
        yield
        return

    orig_socket = socket.socket
    orig_create_connection = socket.create_connection

    class NoNetworkSocket(orig_socket):
        def connect(self, *args: Any, **kwargs: Any) -> NoReturn:
            raise RuntimeError(
                "Network disabled: use @pytest.mark.allow_network",
            )

    def _no_network_create(*args: Any, **kwargs: Any) -> NoReturn:
        raise RuntimeError(
            "Network disabled: use @pytest.mark.allow_network",
        )

    socket.socket = NoNetworkSocket
    socket.create_connection = _no_network_create

    try:
        yield
    finally:
        socket.socket = orig_socket
        socket.create_connection = orig_create_connection
