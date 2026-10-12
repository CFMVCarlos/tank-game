"""UDP Multicast network transceiver with secure JSON serialization."""

import json
import socket
import struct
from typing import Any

DEFAULT_MCAST_GRP: str = "224.1.1.1"
DEFAULT_MCAST_PORT: int = 5007


def create_receiver_socket(
    mcast_grp: str = DEFAULT_MCAST_GRP,
    mcast_port: int = DEFAULT_MCAST_PORT,
) -> socket.socket:
    """Create and configure a non-blocking UDP multicast receiver socket.

    Parameters
    ----------
    mcast_grp : str, default=DEFAULT_MCAST_GRP
        Multicast group IP address.
    mcast_port : int, default=DEFAULT_MCAST_PORT
        UDP port number.

    Returns
    -------
    socket.socket
        Configured and bound UDP socket listening for multicast packets.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", mcast_port))
    mreq = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setblocking(False)
    return sock


def create_sender_socket(multicast_ttl: int = 2) -> socket.socket:
    """Create a UDP socket configured for sending multicast datagrams.

    Parameters
    ----------
    multicast_ttl : int, default=2
        Time-to-live for multicast datagrams.

    Returns
    -------
    socket.socket
        Configured sender UDP socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, multicast_ttl)
    return sock


def send_json_message(
    sock: socket.socket,
    payload: dict[str, Any],
    mcast_grp: str = DEFAULT_MCAST_GRP,
    mcast_port: int = DEFAULT_MCAST_PORT,
) -> None:
    """Serialize and send a JSON payload across UDP multicast.

    Parameters
    ----------
    sock : socket.socket
        Configured sender socket.
    payload : dict[str, Any]
        Dictionary to serialize into JSON and transmit.
    mcast_grp : str, default=DEFAULT_MCAST_GRP
        Target multicast IP address.
    mcast_port : int, default=DEFAULT_MCAST_PORT
        Target port number.
    """
    raw_data = json.dumps(payload).encode("utf-8")
    sock.sendto(raw_data, (mcast_grp, mcast_port))


def receive_json_message(
    sock: socket.socket,
    buffer_size: int = 4096,
) -> dict[str, Any] | None:
    """Attempt non-blocking reception and JSON deserialization of a datagram.

    Parameters
    ----------
    sock : socket.socket
        Configured receiver socket.
    buffer_size : int, default=4096
        Maximum packet buffer size in bytes.

    Returns
    -------
    dict[str, Any] | None
        Decoded payload dictionary, or None if no packet is available or invalid.
    """
    try:
        data, _ = sock.recvfrom(buffer_size)
        decoded = json.loads(data.decode("utf-8"))
        if isinstance(decoded, dict):
            return decoded
    except (BlockingIOError, OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return None


# Backward-compatible camelCase aliases
createReceiverSocket = create_receiver_socket
createSenderSocket = create_sender_socket
sendMessage = send_json_message
