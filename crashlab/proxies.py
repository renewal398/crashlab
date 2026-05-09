import random
from itertools import cycle

class ProxyPool:
    def __init__(self, proxy_file=None):
        self.proxies = []
        if proxy_file:
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        self._cycler = cycle(self.proxies) if self.proxies else None

    def get_proxy(self):
        if not self.proxies:
            return None
        return next(self._cycler)

    def get_proxies_dict(self):
        """Return dict for requests lib {'http': ..., 'https': ...}"""
        proxy = self.get_proxy()
        if proxy:
            return {'http': proxy, 'https': proxy}
        return None
