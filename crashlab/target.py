import socket
import dns.resolver
from urllib.parse import urlparse

class Target:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.parsed = urlparse(self.base_url)
        self.hostname = self.parsed.hostname
        self.port = self.parsed.port or (443 if self.parsed.scheme == 'https' else 80)
        self.scheme = self.parsed.scheme
        self.origin_ip = None

    def resolve_origin_ip(self):
        """Try to get the real server IP (educational - only with permission).
        Uses multiple public DNS resolvers to bypass CDN caching."""
        resolvers = ['1.1.1.1', '8.8.8.8', '9.9.9.9']
        ips = set()
        for resolver_ip in resolvers:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [resolver_ip]
            try:
                answers = resolver.resolve(self.hostname, 'A')
                for rdata in answers:
                    ips.add(rdata.address)
            except:
                continue
        # Educational: if multiple IPs, maybe one is the origin behind a CDN
        if len(ips) == 1:
            self.origin_ip = ips.pop()
        else:
            # Simple heuristic: pick the first one (students can research more advanced methods)
            self.origin_ip = list(ips)[0] if ips else self.hostname
        print(f"[*] Resolved {self.hostname} to origin IP: {self.origin_ip}")
        return self.origin_ip

    @property
    def netloc(self):
        return f"{self.hostname}:{self.port}"
