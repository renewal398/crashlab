import socket
import logging
from urllib.parse import urlparse
import dns.resolver

logger = logging.getLogger(__name__)

class Target:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        parsed = urlparse(self.base_url)
        self.scheme = parsed.scheme
        self.hostname = parsed.hostname
        self.port = parsed.port or (443 if self.scheme == 'https' else 80)
        self.origin_ip = None

    def resolve_origin_ip(self):
        """Retrieve the most likely origin IP (educational only)."""
        # Use multiple public resolvers to reduce CDN caching bias
        resolvers = ['1.1.1.1', '8.8.8.8', '9.9.9.9']
        ips = set()
        for r_ip in resolvers:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [r_ip]
                answers = resolver.resolve(self.hostname, 'A')
                for ans in answers:
                    ips.add(ans.address)
            except Exception:
                continue
        if ips:
            self.origin_ip = list(ips)[0]
        else:
            # Fallback to DNS from system
            try:
                self.origin_ip = socket.gethostbyname(self.hostname)
            except socket.gaierror:
                logger.error("Could not resolve hostname %s", self.hostname)
                self.origin_ip = self.hostname
        logger.info("Resolved %s -> %s", self.hostname, self.origin_ip)
        return self.origin_ip

    @property
    def netloc(self):
        return f"{self.hostname}:{self.port}"
