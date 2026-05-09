import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self, target, proxy_pool=None, user_agent="CrashLab-Edu/2.0"):
        self.target = target
        self.proxy_pool = proxy_pool
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.visited = set()
        self.login_forms = []
        self.search_forms = []
        self.signup_forms = []
        self.dynamic_endpoints = []

    def _fetch(self, url):
        proxies = self.proxy_pool.get_dict() if self.proxy_pool else None
        try:
            resp = self.session.get(url, timeout=10, proxies=proxies)
            return resp
        except Exception as e:
            logger.warning("Fetch failed for %s: %s", url, e)
            return None

    def _extract_forms(self, url, html):
        soup = BeautifulSoup(html, 'lxml')
        for form in soup.find_all('form'):
            action = form.get('action') or ''
            method = form.get('method', 'get').upper()
            inputs = [inp.get('name') for inp in form.find_all(['input','textarea','select']) if inp.get('name')]
            full_url = urljoin(url, action)
            text = (form.get_text() + action).lower()
            if any(kw in text for kw in ['login', 'signin', 'log in']):
                self.login_forms.append((full_url, method, inputs))
            elif any(kw in text for kw in ['signup', 'register', 'create']):
                self.signup_forms.append((full_url, method, inputs))
            elif any(kw in text for kw in ['search', 'query', 'find']):
                self.search_forms.append((full_url, method, inputs))

    def _extract_links(self, url, html):
        soup = BeautifulSoup(html, 'lxml')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == self.target.hostname:
                links.append(full_url)
        return links

    def crawl(self, start_url, max_depth=2, delay=0.5):
        queue = [(start_url, 0)]
        while queue:
            url, depth = queue.pop(0)
            if url in self.visited or depth > max_depth:
                continue
            self.visited.add(url)
            parsed = urlparse(url)
            if parsed.query:
                self.dynamic_endpoints.append(url)
            logger.debug("Crawling: %s", url)
            resp = self._fetch(url)
            if not resp or resp.status_code != 200:
                continue
            ct = resp.headers.get('Content-Type', '')
            if 'html' not in ct:
                continue
            html = resp.text
            self._extract_forms(url, html)
            for link in self._extract_links(url, html):
                queue.append((link, depth+1))
            time.sleep(delay)
        logger.info("Crawl complete. Found %d forms, %d dynamic URLs.",
                    len(self.login_forms)+len(self.search_forms)+len(self.signup_forms),
                    len(self.dynamic_endpoints))
