import socket
from .log import def_log


class TCPClient:
    def connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        def_log.debug("New socket: %s", s)
