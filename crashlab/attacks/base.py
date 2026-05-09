import threading
import time

class AttackBase:
    def __init__(self, target, duration=60):
        self.target = target
        self.duration = duration
        self._running = False
        self.threads = []

    def start(self):
        self._running = True
        print(f"[+] Starting {self.__class__.__name__} for {self.duration}s")
        self._start_threads()
        time.sleep(self.duration)
        self.stop()

    def stop(self):
        self._running = False
        print(f"[-] Stopping {self.__class__.__name__}")

    def _start_threads(self):
        raise NotImplementedError
