import random
from itertools import cycle

class ProxyPool:
    def __init__(self, proxy_file=None):
        self.proxies = []
        if proxy_file:
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        self._cycler = cycle(self.proxies) if self.proxies else None

    def get(self):
        """Return a single proxy URL (e.g., socks5://127.0.0.1:9050) or None."""
        if not self.proxies:
            return None
        return next(self._cycler)

    def get_dict(self):
        """Return dict for requests library."""
        p = self.get()
        if p:
            return {'http': p, 'https': p}
        return None
