import socket
import struct


def createReceiverSocket(
    MCAST_GRP: str = "224.1.1.1", MCAST_PORT: int = 5007
) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock


def createSenderSocket(MULTICAST_TTL: int = 2) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    return sock


def sendMessage(
    sock: socket.socket,
    message: bytes,
    MCAST_GRP: str = "224.1.1.1",
    MCAST_PORT: int = 5007,
) -> None:
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))
