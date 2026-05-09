import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class Crawler:
    def __init__(self, target, proxy_pool=None, delay=0.5, user_agent="CrashLab"):
        self.target = target
        self.proxy_pool = proxy_pool
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.visited = set()
        # Endpoints we care about
        self.login_forms = []   # (url, method, inputs)
        self.search_forms = []
        self.signup_forms = []
        self.dynamic_endpoints = []  # URLs with query params

    def fetch(self, url):
        proxies = self.proxy_pool.get_proxies_dict() if self.proxy_pool else None
        try:
            resp = self.session.get(url, timeout=5, proxies=proxies)
            return resp
        except Exception as e:
            print(f"[-] Failed to fetch {url}: {e}")
            return None

    def extract_forms(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for form in soup.find_all('form'):
            action = form.get('action') or ''
            method = form.get('method', 'get').upper()
            inputs = []
            for inp in form.find_all(['input', 'textarea', 'select']):
                name = inp.get('name')
                if name:
                    inputs.append(name)
            # Heuristic classification
            text_lower = form.get_text().lower() + action.lower()
            if any(kw in text_lower for kw in ['login', 'signin', 'log in']):
                self.login_forms.append((urljoin(url, action), method, inputs))
            elif any(kw in text_lower for kw in ['signup', 'register', 'create account']):
                self.signup_forms.append((urljoin(url, action), method, inputs))
            elif any(kw in text_lower for kw in ['search', 'find', 'query']):
                self.search_forms.append((urljoin(url, action), method, inputs))

    def extract_links(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == self.target.hostname:
                links.append(full_url)
        return links

    def extract_dynamic_params(self, url):
        """Save any URL that has query parameters."""
        parsed = urlparse(url)
        if parsed.query:
            self.dynamic_endpoints.append(url)

    def crawl(self, start_url, max_depth=2):
        queue = [(start_url, 0)]
        while queue:
            url, depth = queue.pop(0)
            if url in self.visited or depth > max_depth:
                continue
            self.visited.add(url)
            self.extract_dynamic_params(url)
            resp = self.fetch(url)
            if resp and resp.status_code == 200 and 'text/html' in resp.headers.get('Content-Type', ''):
                self.extract_forms(url, resp.text)
                links = self.extract_links(url, resp.text)
                for link in links:
                    queue.append((link, depth+1))
                time.sleep(self.delay)
        print(f"[*] Crawl done. Found {len(self.login_forms)} login, "
              f"{len(self.search_forms)} search, {len(self.signup_forms)} signup, "
              f"{len(self.dynamic_endpoints)} dynamic endpoints.")
